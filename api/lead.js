// Recibe los datos que la persona deja antes de abrir WhatsApp (nombre +
// telefono), para que el estudio pueda contactarla aunque nunca llegue a
// escribir el mensaje.
//
// A donde va. Mismo destino y mismo remitente que api/contact.js: si divergen,
// una de las dos vias de contacto termina llegando a otra casilla sin que nadie
// se de cuenta.
//
// Desde el 10/08/2026 va a la casilla del estudio. El remitente tiene que ser
// del dominio verificado en Resend; con un @gmail.com o con el sandbox, el
// envio se rechaza.
//
// Aca no hay reply_to: la persona deja nombre y telefono, no correo. El estudio
// la contacta por WhatsApp, que es lo que estaba haciendo cuando dejo los datos.
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

  const { name, phone, company } = req.body || {};

  // Honeypot: si el campo oculto viene lleno, es un bot.
  if (company) return res.status(200).json({ ok: true });

  if (typeof name !== "string" || typeof phone !== "string") {
    return res.status(400).json({ error: "Faltan datos." });
  }

  const cleanName = name.trim().slice(0, 120);
  const cleanPhone = phone.trim().slice(0, 40);

  if (!cleanName || cleanPhone.replace(/\D/g, "").length < 6) {
    return res.status(400).json({ error: "Revisá el nombre y el teléfono." });
  }

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    console.error("Falta configurar RESEND_API_KEY en las variables de entorno de Vercel.");
    // No bloqueamos a la persona: igual la dejamos seguir a WhatsApp.
    return res.status(200).json({ ok: true, stored: false });
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
        subject: `Nuevo contacto por WhatsApp: ${cleanName}`,
        html: `
          <p>Alguien dejó sus datos para hablar por WhatsApp desde el sitio.</p>
          <p><strong>Nombre:</strong> ${escapeHtml(cleanName)}</p>
          <p><strong>Teléfono:</strong> ${escapeHtml(cleanPhone)}</p>
          <p style="color:#666">Puede que todavía no haya enviado ningún mensaje — conviene escribirle.</p>
        `,
      }),
    });

    if (!resendRes.ok) {
      const detail = await resendRes.text();
      console.error("Error de Resend:", resendRes.status, detail);
      // Tampoco bloqueamos: el objetivo principal es que llegue a WhatsApp.
      return res.status(200).json({ ok: true, stored: false });
    }

    return res.status(200).json({ ok: true, stored: true });
  } catch (err) {
    console.error("Error guardando el contacto de WhatsApp:", err);
    return res.status(200).json({ ok: true, stored: false });
  }
};
