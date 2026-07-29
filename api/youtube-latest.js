// Canal de YouTube del estudio. Cambiar aca si el canal cambia — no requiere
// tocar nada mas (el resto de la pagina se actualiza solo).
const YOUTUBE_CHANNEL_ID = "UC1BfV3DzfGbaWfiMNHd0baw"; // HMA Estudio — youtube.com/@HMAEstudio

const MAX_VIDEOS = 3;

function extractAll(regex, xml) {
  const out = [];
  let m;
  while ((m = regex.exec(xml)) !== null) out.push(m);
  return out;
}

function decodeEntities(str) {
  return str
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function parseFeed(xml) {
  const entryRegex = /<entry>([\s\S]*?)<\/entry>/g;
  const entries = extractAll(entryRegex, xml).map((m) => m[1]);

  return entries.slice(0, MAX_VIDEOS).map((entry) => {
    const videoId = (entry.match(/<yt:videoId>(.*?)<\/yt:videoId>/) || [, ""])[1];
    const title = decodeEntities((entry.match(/<title>([\s\S]*?)<\/title>/) || [, ""])[1]);
    const published = (entry.match(/<published>(.*?)<\/published>/) || [, ""])[1];
    const thumbnail = (entry.match(/<media:thumbnail url="(.*?)"/) || [, ""])[1];

    return {
      id: videoId,
      title,
      url: `https://www.youtube.com/watch?v=${videoId}`,
      thumbnail,
      published,
    };
  });
}

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "https://estudiohma.com");
  res.setHeader("Cache-Control", "public, s-maxage=3600, stale-while-revalidate=86400");

  if (YOUTUBE_CHANNEL_ID.startsWith("UC_REPLACE")) {
    return res.status(200).json({ videos: [] });
  }

  try {
    const feedRes = await fetch(
      `https://www.youtube.com/feeds/videos.xml?channel_id=${encodeURIComponent(YOUTUBE_CHANNEL_ID)}`
    );
    if (!feedRes.ok) {
      return res.status(502).json({ error: "No se pudo leer el canal de YouTube.", videos: [] });
    }
    const xml = await feedRes.text();
    const videos = parseFeed(xml);
    return res.status(200).json({ videos });
  } catch (err) {
    console.error("Error leyendo el feed de YouTube:", err);
    return res.status(500).json({ error: "Error interno.", videos: [] });
  }
};
