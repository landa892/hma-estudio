// Sirve las miniaturas de YouTube desde estudiohma.com. Varias universidades
// y redes corporativas bloquean i.ytimg.com aunque permitan abrir el sitio, y
// eso dejaba las tarjetas de Inicio y Prensa con un rectangulo vacio.
module.exports = async function handler(req, res) {
  const id = String((req.query || {}).id || "");
  if (!/^[A-Za-z0-9_-]{11}$/.test(id)) {
    return res.status(400).send("Video invalido");
  }

  const variantes = ["maxresdefault", "sddefault", "hqdefault"];
  for (const nombre of variantes) {
    let respuesta;
    try {
      respuesta = await fetch(`https://i.ytimg.com/vi/${id}/${nombre}.jpg`);
    } catch (_) {
      continue;
    }
    if (!respuesta.ok) continue;
    const tipo = respuesta.headers.get("content-type") || "";
    if (!tipo.startsWith("image/")) continue;
    const cuerpo = Buffer.from(await respuesta.arrayBuffer());
    res.setHeader("Content-Type", tipo);
    res.setHeader("Cache-Control", "public, s-maxage=86400, stale-while-revalidate=604800");
    return res.status(200).send(cuerpo);
  }
  return res.status(404).send("Miniatura no disponible");
};
