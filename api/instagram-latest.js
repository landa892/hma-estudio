// Ultima publicacion del Instagram profesional del estudio.
//
// El token vive solamente en Vercel. El navegador consulta esta funcion y la
// imagen tambien pasa por aca, para no exponer la credencial ni depender del
// dominio temporal que Meta entrega para cada archivo.
const FALLBACK = {
  automatic: false,
  title: "Movistar Arena",
  text: "Nuestro proyecto VIP Lounge Movistar Arena fue distinguido con una Mención Especial en la categoría Commercial Interiors de los Architizer A+ Awards 2026.",
  url: "https://www.instagram.com/p/DYANnd0CXnT/",
  image: "/assets/covers/movistar-arena.webp",
};

const VERSION = process.env.INSTAGRAM_API_VERSION || "v23.0";
const API = `https://graph.instagram.com/${VERSION}`;

function limpiar(texto) {
  return (texto || "").replace(/https?:\/\/\S+/g, "").replace(/#\S+/g, "")
    .replace(/\s+/g, " ").trim();
}

function tituloDe(texto) {
  const limpio = limpiar(texto);
  if (!limpio) return "Última novedad del estudio";
  // Algunas publicaciones usan un punto solo como separador en el primer
  // renglon. No puede convertirse en un titulo vacio en el Inicio.
  const frase = limpio.split(/[.!?]\s+/)
    .map((parte) => parte.replace(/^[\s.!?·•—–-]+/, "").trim())
    .find((parte) => /[A-Za-zÀ-ÿ0-9]/.test(parte)) || "Última novedad del estudio";
  const palabras = frase.split(" ");
  return (palabras.length > 12 ? palabras.slice(0, 12).join(" ") + "…" : frase).slice(0, 100);
}

function normalizarComparacion(texto) {
  return limpiar(texto).toLocaleLowerCase("es").replace(/[^a-zà-ÿ0-9]+/g, " ").trim();
}

function textoDe(texto, titulo) {
  const lineas = (texto || "").split(/\r?\n/)
    .map((linea) => limpiar(linea))
    .filter((linea) => /[A-Za-zÀ-ÿ0-9]/.test(linea));
  if (lineas.length && normalizarComparacion(lineas[0]) === normalizarComparacion(titulo)) {
    lineas.shift();
  }
  return lineas.join(" ").replace(/^[\s.!?·•—–-]+/, "").trim().slice(0, 360);
}

function esDemasiadoAntigua(publicacion) {
  if (!publicacion || !publicacion.timestamp) return false;
  const fecha = Date.parse(publicacion.timestamp);
  if (!Number.isFinite(fecha)) return false;
  const dias = Number(process.env.INSTAGRAM_MAX_AGE_DAYS || 45);
  return Date.now() - fecha > Math.max(1, dias) * 86400000;
}

function imagenDe(publicacion) {
  if (!publicacion) return null;
  if (publicacion.media_type === "VIDEO") {
    return publicacion.thumbnail_url || publicacion.media_url || null;
  }
  if (publicacion.media_url) return publicacion.media_url;
  const hijos = publicacion.children && publicacion.children.data;
  if (!Array.isArray(hijos)) return null;
  const primero = hijos.find((item) => item && (item.thumbnail_url || item.media_url));
  return primero ? (primero.thumbnail_url || primero.media_url) : null;
}

async function ultimaPublicacion() {
  const token = process.env.INSTAGRAM_ACCESS_TOKEN;
  if (!token) return null;
  const campos = "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,children{media_type,media_url,thumbnail_url}";
  const parametros = new URLSearchParams({ fields: campos, limit: "10" });
  const respuesta = await fetch(`${API}/me/media?${parametros}`, {
    headers: { Authorization: `Bearer ${token}` },
    signal: AbortSignal.timeout(10000),
  });
  if (!respuesta.ok) {
    throw new Error(`Instagram respondió ${respuesta.status}: ${await respuesta.text()}`);
  }
  const datos = await respuesta.json();
  return (datos.data || [])
    .filter((item) => item && item.permalink && imagenDe(item))
    .sort((a, b) => Date.parse(b.timestamp || 0) - Date.parse(a.timestamp || 0))[0] || null;
}

async function enviarImagen(res, publicacion) {
  const remota = imagenDe(publicacion);
  if (!remota) return res.redirect(307, FALLBACK.image);
  const imagen = await fetch(remota, { signal: AbortSignal.timeout(10000) });
  if (!imagen.ok) return res.redirect(307, FALLBACK.image);
  res.setHeader("Content-Type", imagen.headers.get("content-type") || "image/jpeg");
  res.setHeader("Cache-Control", "public, s-maxage=900, stale-while-revalidate=86400");
  return res.status(200).send(Buffer.from(await imagen.arrayBuffer()));
}

async function handler(req, res) {
  res.setHeader("Cache-Control", "public, s-maxage=900, stale-while-revalidate=86400");
  try {
    const publicacion = await ultimaPublicacion();
    if (!publicacion) {
      if (req.query && req.query.image) return res.redirect(307, FALLBACK.image);
      return res.status(200).json(FALLBACK);
    }
    if (req.query && req.query.image) return enviarImagen(res, publicacion);

    const texto = (publicacion.caption || "").trim();
    const titulo = tituloDe(texto);
    // Instagram Login solo lista contenido creado por la cuenta. Si esa lista
    // quedo vieja pero el perfil muestra colaboraciones nuevas, no debe pisar
    // el respaldo que el estudio eligio desde el panel llamandolo "lo ultimo".
    if (esDemasiadoAntigua(publicacion)) {
      return res.status(200).json({
        ...FALLBACK,
        reason: "latest-owned-post-is-stale",
        latestOwnedAt: publicacion.timestamp || null,
      });
    }
    return res.status(200).json({
      automatic: true,
      title: titulo,
      text: textoDe(texto, titulo),
      url: publicacion.permalink,
      image: "/api/instagram-latest?image=1",
      publishedAt: publicacion.timestamp || null,
    });
  } catch (error) {
    console.error("Instagram:", error.message);
    if (req.query && req.query.image) return res.redirect(307, FALLBACK.image);
    return res.status(200).json(FALLBACK);
  }
}

handler._internals = { limpiar, tituloDe, textoDe, imagenDe, esDemasiadoAntigua };
module.exports = handler;
