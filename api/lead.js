// Recibe los datos que la persona deja antes de abrir WhatsApp (nombre +
// telefono), para que el estudio pueda contactarla aunque nunca llegue a
// escribir el mensaje.
//
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
