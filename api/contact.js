// A donde va lo que manda el formulario.
//
// El destino definitivo es hitzig.militello@gmail.com, que pidio el cliente.
// Todavia no esta activo, y por dos razones distintas:
//
//   1. La cuenta todavia no es del estudio. Hasta que no la creen, esa
//      direccion puede ser de cualquiera, y ahi irian a parar las consultas
//      de gente real.
//   2. Aunque se activara, no llegaria: mientras el dominio estudiohma.com no
//      este verificado en Resend, se envia desde el sandbox
//      (onboarding@resend.dev), que solo entrega a la casilla dueña de la
//      cuenta de Resend. Cualquier otro destino se descarta en silencio.
//
// Asi que hasta que existan la cuenta y el dominio verificado, sigue yendo a
// la casilla que hoy funciona. Cambiar TO_EMAIL por DESTINO_FINAL es todo lo
// que hay que hacer el dia que esten las dos cosas.
const DESTINO_FINAL = "hitzig.militello@gmail.com";
const TO_EMAIL = "nacholanda08@gmail.com";
const FROM_EMAIL = "HMA Web <onboarding@resend.dev>";

const submissions = new Map();
const RATE_LIMIT_WINDOW_MS = 60_000;
const RATE_LIMIT_MAX = 3;

function isRateLimited(ip) {
  const now = Date.now();
  for (const [key, value] of submissions) {
    const recent = value.filter((t) => now - t < RATE_LIMIT_WINDOW_MS);
    if (recent.length) submissions.set(key, recent);
    else submissions.delete(key);
  }
  const hits = (submissions.get(ip) || []).filter((t) => now - t < RATE_LIMIT_WINDOW_MS);
  hits.push(now);
  submissions.set(ip, hits);
  return hits.length > RATE_LIMIT_MAX;
}

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "https://estudiohma.com");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Método no permitido" });

  const ip = (req.headers["x-forwarded-for"] || req.socket.remoteAddress || "unknown").split(",")[0].trim();
  if (isRateLimited(ip)) {
    return res.status(429).json({ error: "Demasiados envíos. Probá de nuevo en un minuto." });
  }

  const { name, email, message, company } = req.body || {};

  // Honeypot: si el campo oculto "company" viene lleno, es un bot.
  if (company) return res.status(200).json({ ok: true });

  if (typeof name !== "string" || typeof email !== "string" || typeof message !== "string") {
    return res.status(400).json({ error: "Faltan datos del formulario." });
  }

  const cleanName = name.trim().slice(0, 120);
  const cleanEmail = email.trim().slice(0, 200);
  const cleanMessage = message.trim().slice(0, 4000);

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!cleanName || !cleanMessage || !emailRegex.test(cleanEmail)) {
    return res.status(400).json({ error: "Revisá los datos: nombre, email y mensaje son obligatorios." });
  }

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    console.error("Falta configurar RESEND_API_KEY en las variables de entorno de Vercel.");
    return res.status(500).json({ error: "El formulario no está configurado todavía. Escribinos a hma@estudiohma.com." });
  }

  try {
    const resendRes = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: FROM_EMAIL,
        to: [TO_EMAIL],
        reply_to: cleanEmail,
        subject: `Nueva consulta de ${cleanName} — sitio web`,
        html: `
          <p><strong>Nombre:</strong> ${escapeHtml(cleanName)}</p>
          <p><strong>Email:</strong> ${escapeHtml(cleanEmail)}</p>
          <p><strong>Mensaje:</strong></p>
          <p>${escapeHtml(cleanMessage).replace(/\n/g, "<br>")}</p>
        `,
      }),
    });

    if (!resendRes.ok) {
      const detail = await resendRes.text();
      console.error("Error de Resend:", resendRes.status, detail);
      return res.status(502).json({ error: "No se pudo enviar el mensaje. Probá de nuevo o escribinos directo." });
    }

    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error("Error enviando el formulario de contacto:", err);
    return res.status(500).json({ error: "No se pudo enviar el mensaje. Probá de nuevo o escribinos directo." });
  }
};
