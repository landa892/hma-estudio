// A donde va lo que manda el formulario.
//
// Desde el 10/08/2026 las consultas van a la casilla del estudio. Antes iban a
// la del desarrollador, y no por comodidad: el dominio no estaba verificado en
// Resend, asi que se enviaba desde el sandbox (onboarding@resend.dev), que solo
// entrega a la casilla dueña de la cuenta y descarta en silencio cualquier otro
// destino. Con estudiohma.com verificado eso ya no aplica.
//
// El remitente tiene que ser del dominio verificado: si vuelve a un @gmail.com
// o al sandbox, Resend rechaza el envio.
//
// web@estudiohma.com no necesita existir como casilla. Nadie responde ahi: cada
// mail sale con reply_to apuntando a quien escribio, asi que el estudio contesta
// y le llega directo a la persona.
const TO_EMAIL = "hitzig.militello@gmail.com";
const FROM_EMAIL = "HMA Estudio <web@estudiohma.com>";

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
