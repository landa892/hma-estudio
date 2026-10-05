// Lectura y guardado del token de Instagram, compartido por los dos endpoints.
//
// El token vive en la tabla `credenciales` de Supabase y no en una variable de
// entorno, porque una variable no se puede reescribir desde el propio sitio y
// este token hay que renovarlo cada menos de 60 dias. Ver la migracion 0021.
//
// La variable INSTAGRAM_ACCESS_TOKEN se sigue leyendo como respaldo: es de
// donde sale el primer token, antes de que el refresco haya guardado uno. Y si
// la base no contesta, el sitio sigue andando con ella en vez de quedarse sin
// publicacion.

const CLAVE = "instagram_access_token";

function configuracion() {
  const url = (process.env.SUPABASE_URL || "").replace(/\/+$/, "");
  const clave = process.env.SUPABASE_SERVICE_KEY || "";
  return url && clave ? { url, clave } : null;
}

function cabeceras(clave) {
  return {
    apikey: clave,
    Authorization: `Bearer ${clave}`,
    "Content-Type": "application/json",
  };
}

// La tabla la crea la migracion 0021, que se corre a mano como todas. Mientras
// no este, PostgREST contesta 404 con PGRST205. Conviene distinguirlo de "la
// base no anda": es un paso de instalacion pendiente, no una falla.
async function faltaLaTabla() {
  const conf = configuracion();
  if (!conf) return false;
  try {
    const respuesta = await fetch(
      `${conf.url}/rest/v1/credenciales?select=clave&limit=1`,
      { headers: cabeceras(conf.clave), signal: AbortSignal.timeout(8000) }
    );
    if (respuesta.ok) return false;
    const texto = await respuesta.text();
    return respuesta.status === 404 || texto.includes("PGRST205");
  } catch (_) {
    return false;
  }
}

// Devuelve { valor, vence_en, refrescado_en } o null.
async function guardado() {
  const conf = configuracion();
  if (!conf) return null;
  const ruta =
    `${conf.url}/rest/v1/credenciales` +
    `?clave=eq.${encodeURIComponent(CLAVE)}&select=valor,vence_en,refrescado_en`;
  const respuesta = await fetch(ruta, {
    headers: cabeceras(conf.clave),
    signal: AbortSignal.timeout(8000),
  });
  if (!respuesta.ok) return null;
  const filas = await respuesta.json();
  return Array.isArray(filas) && filas.length ? filas[0] : null;
}

// El token que hay que usar ahora. Prioriza el de la base; si no hay, el de la
// variable. Nunca tira: si la base falla, el sitio tiene que seguir en pie.
async function tokenVigente() {
  let fila = null;
  try {
    fila = await guardado();
  } catch (_) {
    fila = null;
  }
  if (fila && fila.valor) return { token: fila.valor, origen: "base", fila };
  const suelto = process.env.INSTAGRAM_ACCESS_TOKEN;
  return suelto ? { token: suelto, origen: "variable", fila: null } : null;
}

async function escribir(token, venceEn, nota) {
  const conf = configuracion();
  if (!conf) throw new Error("faltan SUPABASE_URL o SUPABASE_SERVICE_KEY");
  const cuerpo = [
    {
      clave: CLAVE,
      valor: token,
      vence_en: venceEn ? new Date(venceEn).toISOString() : null,
      refrescado_en: new Date().toISOString(),
      nota: nota || null,
    },
  ];
  // merge-duplicates: la primera vez inserta y despues actualiza la misma fila.
  const respuesta = await fetch(`${conf.url}/rest/v1/credenciales`, {
    method: "POST",
    headers: {
      ...cabeceras(conf.clave),
      Prefer: "resolution=merge-duplicates,return=minimal",
    },
    body: JSON.stringify(cuerpo),
    signal: AbortSignal.timeout(8000),
  });
  if (!respuesta.ok) {
    throw new Error(
      `No se pudo guardar el token (${respuesta.status}): ${await respuesta.text()}`
    );
  }
}

module.exports = { CLAVE, tokenVigente, guardado, escribir, faltaLaTabla };
