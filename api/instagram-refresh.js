// Renueva el token de Instagram antes de que venza. Lo llama el cron de Vercel.
//
// Por que existe: el token largo de Instagram dura 60 dias y NO tiene periodo
// de gracia. Si llega a vencer, no hay forma de recuperarlo desde el codigo y
// hay que volver a autorizar la app a mano en Meta for Developers. Eso ya paso
// y dejo el Inicio con la publicacion de respaldo durante semanas.
//
// Cada refresco reinicia los 60 dias desde el momento del pedido, asi que
// renovando con holgura el token no se cae nunca. Meta pide dos cosas para
// aceptar el refresco: que el token tenga al menos 24 horas y que todavia no
// haya vencido.
//
// El cron corre una vez por dia -el plan Hobby de Vercel no da mas-, pero el
// refresco real ocurre solo cuando faltan menos de DIAS_ANTES para el
// vencimiento. Las demas noches contesta "todavia no" y no gasta nada.

const { tokenVigente, guardado, escribir, faltaLaTabla } = require("./_token-instagram.js");

const VERSION = process.env.INSTAGRAM_API_VERSION || "v23.0";
const DIA = 24 * 60 * 60 * 1000;

// Se renueva faltando 20 dias. El margen es grande a proposito: si el cron no
// corre una noche, o si Meta contesta mal unos dias, quedan casi tres semanas
// de reintentos antes de que el token muera sin vuelta atras.
const DIAS_ANTES = Number(process.env.INSTAGRAM_REFRESH_DIAS || 20);

// Instagram no acepta refrescar un token con menos de 24 horas.
const HORAS_MINIMAS = 24;

function autorizado(req) {
  const secreto = process.env.CRON_SECRET;
  // Sin secreto configurado se permite: en Vercel el endpoint igual solo lo
  // dispara el cron, y asi la primera puesta en marcha no queda trabada. Con
  // secreto puesto, se exige.
  if (!secreto) return true;
  const cabecera = req.headers.authorization || "";
  return cabecera === `Bearer ${secreto}`;
}

async function refrescar(token) {
  const url =
    `https://graph.instagram.com/refresh_access_token` +
    `?grant_type=ig_refresh_token&access_token=${encodeURIComponent(token)}`;
  const respuesta = await fetch(url, { signal: AbortSignal.timeout(10000) });
  const texto = await respuesta.text();
  if (!respuesta.ok) {
    throw new Error(`Instagram respondio ${respuesta.status}: ${texto}`);
  }
  let datos;
  try {
    datos = JSON.parse(texto);
  } catch (_) {
    throw new Error(`Instagram devolvio algo que no es JSON: ${texto.slice(0, 200)}`);
  }
  if (!datos.access_token) {
    throw new Error(`Instagram no devolvio access_token: ${texto.slice(0, 200)}`);
  }
  // expires_in viene en segundos; son 60 dias salvo que Meta cambie de idea.
  const vence = Date.now() + Number(datos.expires_in || 60 * 24 * 60 * 60) * 1000;
  return { token: datos.access_token, vence };
}

async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (!autorizado(req)) {
    return res.status(401).json({ ok: false, error: "no autorizado" });
  }

  const forzar = Boolean(req.query && req.query.forzar);

  try {
    // Sin la migracion 0021 no hay donde guardar nada. Se contesta 200 y no 500
    // a proposito: es un paso de instalacion pendiente, y un cron en rojo todas
    // las noches por eso solo hace ruido y tapa los fallos de verdad.
    if (await faltaLaTabla()) {
      return res.status(200).json({
        ok: false,
        estado: "falta la migracion",
        detalle:
          "La tabla credenciales no existe. Corre " +
          "supabase/migrations/0021_token_instagram.sql en el editor SQL de " +
          "Supabase y volve a probar. Ver docs/INSTAGRAM-TOKEN.md.",
      });
    }

    const vigente = await tokenVigente();
    if (!vigente) {
      return res.status(200).json({
        ok: false,
        estado: "sin token",
        detalle:
          "No hay token ni en la base ni en INSTAGRAM_ACCESS_TOKEN. Hay que " +
          "generar uno en Meta for Developers y ponerlo en la variable; el " +
          "primer refresco lo pasa a la base.",
      });
    }

    const fila = vigente.fila || (await guardado().catch(() => null));
    const ahora = Date.now();

    // Nunca antes de las 24 horas: Instagram lo rechaza.
    if (fila && fila.refrescado_en) {
      const edad = ahora - Date.parse(fila.refrescado_en);
      if (edad < HORAS_MINIMAS * 60 * 60 * 1000 && !forzar) {
        return res.status(200).json({
          ok: true,
          estado: "recien refrescado",
          detalle: "Instagram exige que el token tenga 24 horas para renovarlo.",
        });
      }
    }

    // Si todavia falta, no se toca. El cron corre todos los dias.
    if (fila && fila.vence_en && !forzar) {
      const faltan = (Date.parse(fila.vence_en) - ahora) / DIA;
      if (faltan > DIAS_ANTES) {
        return res.status(200).json({
          ok: true,
          estado: "todavia no hace falta",
          faltan_dias: Math.round(faltan),
          renueva_faltando_dias: DIAS_ANTES,
        });
      }
    }

    const nuevo = await refrescar(vigente.token);
    await escribir(
      nuevo.token,
      nuevo.vence,
      `refrescado por el cron; venia de ${vigente.origen}`
    );

    return res.status(200).json({
      ok: true,
      estado: "refrescado",
      vence_en: new Date(nuevo.vence).toISOString(),
      dias: Math.round((nuevo.vence - ahora) / DIA),
      venia_de: vigente.origen,
    });
  } catch (error) {
    // 500 a proposito: asi el fallo aparece en el panel de Vercel en vez de
    // pasar por exitoso. Si esto se repite varios dias seguidos, el token esta
    // por morir y hay que volver a autorizar a mano.
    console.error("instagram-refresh", error);
    return res.status(500).json({ ok: false, error: String(error.message || error) });
  }
}

module.exports = handler;
module.exports.default = handler;
module.exports.VERSION = VERSION;
