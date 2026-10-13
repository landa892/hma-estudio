// Consulta diaria y minima para mantener comprobada la conexion con Supabase.
//
// Es independiente de Instagram: un token vencido de Meta no tiene que dejar
// sin actividad al proyecto gratuito. Lee una sola obra publicada, no toca
// Storage, no descarga imagenes y no expone el resultado de la consulta.

function configuracion() {
  const url = (process.env.SUPABASE_URL || "").replace(/\/+$/, "");
  const clave = process.env.SUPABASE_ANON_KEY || "";
  return url && clave ? { url, clave } : null;
}

function autorizado(req) {
  const secreto = process.env.CRON_SECRET;
  const cabecera = req.headers.authorization || "";

  // Vercel agrega este secreto automaticamente al cron cuando esta definido.
  if (secreto) return cabecera === `Bearer ${secreto}`;

  // En instalaciones antiguas sin CRON_SECRET se acepta solo la llamada que
  // identifica Vercel. La accion sigue siendo una lectura publica sin datos.
  return String(req.headers["user-agent"] || "").startsWith("vercel-cron/");
}

async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (!autorizado(req)) {
    return res.status(401).json({ ok: false, error: "no autorizado" });
  }

  const conf = configuracion();
  if (!conf) {
    console.error("supabase-health: faltan SUPABASE_URL o SUPABASE_ANON_KEY");
    return res.status(500).json({ ok: false, error: "configuracion incompleta" });
  }

  try {
    const respuesta = await fetch(
      `${conf.url}/rest/v1/obras?select=id&publicada=eq.true&limit=1`,
      {
        headers: {
          apikey: conf.clave,
          Authorization: `Bearer ${conf.clave}`,
        },
        signal: AbortSignal.timeout(8000),
      }
    );

    if (!respuesta.ok) {
      throw new Error(`Supabase respondio ${respuesta.status}`);
    }

    // No devolvemos filas ni identificadores: alcanza con confirmar la salud.
    return res.status(200).json({ ok: true, servicio: "supabase", actividad: "lectura diaria" });
  } catch (error) {
    console.error("supabase-health", error);
    return res.status(500).json({ ok: false, error: "Supabase no respondio" });
  }
}

module.exports = handler;
module.exports.default = handler;
