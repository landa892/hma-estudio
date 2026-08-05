// Canal de YouTube del estudio. Cambiar aca si el canal cambia — no requiere
// tocar nada mas (el resto de la pagina se actualiza solo).
const YOUTUBE_CHANNEL_ID = "UC1BfV3DzfGbaWfiMNHd0baw"; // HMA Estudio — youtube.com/@HMAEstudio

// El feed RSS publico de YouTube (feeds/videos.xml) fue dado de baja por
// Google — devuelve 404 incluso para canales conocidos. Se usa en su lugar
// la YouTube Data API v3 oficial, gratuita y sin revision, via la playlist
// de "subidos" del canal (se arma cambiando el prefijo UC por UU).
// La pagina reparte los videos en dos secciones (entrevistas y charlas),
// asi que pedir tres dejaba una de las dos vacia o repetida. Con doce hay
// material para las dos y sigue entrando de sobra en la cuota gratuita.
const MAX_VIDEOS = 12;

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "https://estudiohma.com");
  res.setHeader("Cache-Control", "public, s-maxage=3600, stale-while-revalidate=86400");

  const apiKey = process.env.YOUTUBE_API_KEY;
  if (!apiKey) {
    console.error("Falta configurar YOUTUBE_API_KEY en las variables de entorno de Vercel.");
    return res.status(200).json({ videos: [] });
  }

  const uploadsPlaylistId = "UU" + YOUTUBE_CHANNEL_ID.slice(2);

  try {
    const apiUrl = `https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=${MAX_VIDEOS}&playlistId=${uploadsPlaylistId}&key=${apiKey}`;
    const ytRes = await fetch(apiUrl);

    if (!ytRes.ok) {
      const detail = await ytRes.text();
      console.error("Error de YouTube Data API:", ytRes.status, detail);
      return res.status(502).json({ error: "No se pudo leer el canal de YouTube.", videos: [] });
    }

    const data = await ytRes.json();
    const videos = (data.items || []).map((item) => {
      const s = item.snippet || {};
      const videoId = s.resourceId ? s.resourceId.videoId : "";
      const thumb = s.thumbnails || {};
      // Varios videos del canal son verticales, y para esos "high"
      // (hqdefault) viene con bandas negras que ocupan dos tercios del
      // cuadro. "maxres" trae la imagen completa cuando existe.
      const thumbnail = (thumb.maxres || thumb.standard || thumb.high ||
        thumb.medium || thumb.default || {}).url || "";

      return {
        id: videoId,
        title: s.title || "",
        url: `https://www.youtube.com/watch?v=${videoId}`,
        thumbnail,
        published: s.publishedAt || "",
      };
    });

    return res.status(200).json({ videos });
  } catch (err) {
    console.error("Error leyendo YouTube:", err);
    return res.status(500).json({ error: "Error interno.", videos: [] });
  }
};
