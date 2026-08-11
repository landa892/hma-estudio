// Los videos que muestra la pagina de prensa.
//
// Salen de tres playlists del canal y no de "lo ultimo que subio el canal".
// El motivo es editorial: el estudio tambien publica despieces de planos y
// clips tecnicos que no van en la web, y con la lista de subidas esos eran
// justamente los mas recientes.
//
// Antes se filtraba por el titulo, buscando palabras como "entrevista" o
// "podcast". Eso funcionaba de casualidad: bastaba que bautizaran una charla
// "Charla en HOTELGA" para que quedara afuera, o que un despiece dijera
// "entrevista" adentro para que entrara. Con playlists la decision es del
// estudio y explicita: lo que agregan a estas listas aparece, lo demas no.
//
// Para sumar o sacar una lista, se toca este arreglo y nada mas.
const PLAYLISTS = [
  "PLzPPIqCbpvjQoVeH19BqSE5NefL6Tt5hw", // Oradores
  "PLzPPIqCbpvjTz-A_AzZrJRj_dIayTP3lv", // Entrevistas
  "PLzPPIqCbpvjTXso-Q666hx0thn96KLum3", // Ciclo de entrevistas
];

// Se piden de a 20 por lista y despues se recorta: asi el orden por fecha sale
// del conjunto y no de lo que devolvio cada lista por separado.
const POR_LISTA = 20;
const MAX_VIDEOS = 12;

async function traerLista(playlistId, apiKey) {
  const url =
    "https://www.googleapis.com/youtube/v3/playlistItems" +
    `?part=snippet&maxResults=${POR_LISTA}` +
    `&playlistId=${encodeURIComponent(playlistId)}&key=${apiKey}`;

  const r = await fetch(url);
  if (!r.ok) {
    // Una lista borrada, renombrada o puesta en privado no puede tumbar las
    // otras dos: se registra y se sigue.
    console.error("YouTube: falló la playlist", playlistId, r.status,
      await r.text());
    return [];
  }

  const data = await r.json();
  return (data.items || []).map((item) => {
    const s = item.snippet || {};
    const videoId = s.resourceId ? s.resourceId.videoId : "";
    const thumb = s.thumbnails || {};
    // Varios videos del canal son verticales, y para esos "high" (hqdefault)
    // viene con bandas negras que ocupan dos tercios del cuadro. "maxres" trae
    // la imagen completa cuando existe.
    const thumbnail =
      (thumb.maxres || thumb.standard || thumb.high || thumb.medium ||
        thumb.default || {}).url || "";

    return {
      id: videoId,
      title: s.title || "",
      url: `https://www.youtube.com/watch?v=${videoId}`,
      thumbnail,
      published: s.publishedAt || "",
    };
  }).filter((v) => {
    // YouTube deja en la lista los videos borrados o pasados a privado, con el
    // titulo cambiado y sin miniatura. Si entraran, la grilla mostraria huecos.
    if (!v.id || !v.thumbnail) return false;
    return !/^(Deleted|Private) video$/i.test(v.title);
  });
}

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "https://estudiohma.com");
  res.setHeader("Cache-Control", "public, s-maxage=3600, stale-while-revalidate=86400");

  const apiKey = process.env.YOUTUBE_API_KEY;
  if (!apiKey) {
    console.error("Falta configurar YOUTUBE_API_KEY en las variables de entorno de Vercel.");
    return res.status(200).json({ videos: [] });
  }

  try {
    const listas = await Promise.all(
      PLAYLISTS.map((id) => traerLista(id, apiKey))
    );

    // Un mismo video puede estar en dos listas —una entrevista que tambien es
    // parte del ciclo—, asi que se deduplica por id antes de ordenar.
    const porId = new Map();
    for (const lista of listas) {
      for (const v of lista) {
        if (!porId.has(v.id)) porId.set(v.id, v);
      }
    }

    const videos = [...porId.values()]
      .sort((a, b) => (b.published || "").localeCompare(a.published || ""))
      .slice(0, MAX_VIDEOS);

    if (!videos.length) {
      // Sin videos la pagina se queda con las tarjetas que trae el HTML, que es
      // mejor que mostrar la seccion vacia.
      console.error("YouTube: las playlists no devolvieron ningún video.");
    }

    return res.status(200).json({ videos });
  } catch (err) {
    console.error("Error leyendo YouTube:", err);
    return res.status(500).json({ error: "Error interno.", videos: [] });
  }
};
