// Ultima publicacion organica de la pagina de LinkedIn del estudio.
//
// La API de LinkedIn requiere una aplicacion aprobada y r_organization_social.
// Si falta el permiso, el token vence o LinkedIn falla, el home conserva la
// publicacion editorial que ya trae en el HTML: nunca queda un bloque vacio.
const FALLBACK = {
  automatic: false,
  title: "El estudio detrás del Movistar Arena",
  text: "Leonardo Militello y Fernando Hitzig repasan dos décadas de trayectoria, el método de trabajo del estudio y el proceso creativo del espacio VIP gastronómico del Movistar Arena.",
  url: "https://www.linkedin.com/posts/hitzig-militello-arquitectos_dise%C3%B1amos-el-vip-del-movistar-arena-para-activity-7474580879424671744--V-b",
  image: "/assets/covers/movistar-arena.webp",
};

const VERSION = process.env.LINKEDIN_API_VERSION || "202606";

function headers(token, finder = false) {
  const result = {
    Authorization: `Bearer ${token}`,
    "X-Restli-Protocol-Version": "2.0.0",
    "Linkedin-Version": VERSION,
  };
  if (finder) result["X-RestLi-Method"] = "FINDER";
  return result;
}

async function latest() {
  const token = process.env.LINKEDIN_ACCESS_TOKEN;
  const organization = process.env.LINKEDIN_ORGANIZATION_URN;
  if (!token || !organization) return null;

  const params = new URLSearchParams({
    author: organization,
    q: "author",
    count: "10",
    sortBy: "CREATED",
    viewContext: "READER",
  });
  const response = await fetch(`https://api.linkedin.com/rest/posts?${params}`, {
    headers: headers(token, true),
  });
  if (!response.ok) {
    throw new Error(`LinkedIn respondió ${response.status}: ${await response.text()}`);
  }
  const data = await response.json();
  return (data.elements || []).find((post) =>
    post.lifecycleState === "PUBLISHED" && post.visibility === "PUBLIC"
  ) || null;
}

function imageUrn(post) {
  const content = (post && post.content) || {};
  if (content.media && /^urn:li:image:/.test(content.media.id || "")) {
    return content.media.id;
  }
  const images = content.multiImage && content.multiImage.images;
  if (images && images.length && /^urn:li:image:/.test(images[0].id || "")) {
    return images[0].id;
  }
  return null;
}

async function imageUrl(post) {
  const urn = imageUrn(post);
  const token = process.env.LINKEDIN_ACCESS_TOKEN;
  if (!urn || !token) return null;
  const response = await fetch(`https://api.linkedin.com/rest/images/${encodeURIComponent(urn)}`, {
    headers: headers(token),
  });
  if (!response.ok) return null;
  const data = await response.json();
  return data.downloadUrl || null;
}

function titleFrom(text) {
  const clean = (text || "").replace(/https?:\/\/\S+/g, "").replace(/#\S+/g, "")
    .replace(/\s+/g, " ").trim();
  if (!clean) return "Última novedad del estudio";
  const sentence = clean.split(/[.!?]\s/)[0];
  const words = sentence.split(" ");
  return (words.length > 12 ? words.slice(0, 12).join(" ") + "…" : sentence).slice(0, 100);
}

function postUrl(id) {
  return id ? `https://www.linkedin.com/feed/update/${id}/` : FALLBACK.url;
}

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "public, s-maxage=900, stale-while-revalidate=86400");
  try {
    const post = await latest();
    if (!post) {
      if (req.query && req.query.image) return res.redirect(307, FALLBACK.image);
      return res.status(200).json(FALLBACK);
    }

    if (req.query && req.query.image) {
      const remote = await imageUrl(post);
      if (!remote) return res.redirect(307, FALLBACK.image);
      const image = await fetch(remote);
      if (!image.ok) return res.redirect(307, FALLBACK.image);
      res.setHeader("Content-Type", image.headers.get("content-type") || "image/jpeg");
      return res.status(200).send(Buffer.from(await image.arrayBuffer()));
    }

    const commentary = (post.commentary || "").trim();
    return res.status(200).json({
      automatic: true,
      title: titleFrom(commentary),
      text: commentary.slice(0, 360),
      url: postUrl(post.id),
      image: imageUrn(post) ? "/api/linkedin-latest?image=1" : FALLBACK.image,
      publishedAt: post.publishedAt || post.createdAt || null,
    });
  } catch (error) {
    console.error("LinkedIn:", error.message);
    if (req.query && req.query.image) return res.redirect(307, FALLBACK.image);
    return res.status(200).json(FALLBACK);
  }
};
