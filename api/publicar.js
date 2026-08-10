// Dispara la reconstruccion del sitio cuando el estudio aprieta "Publicar".
//
// La URL del deploy hook de Vercel NO puede vivir en el panel: cualquiera que
// abra el codigo de la pagina la ve, y con esa URL sola se pueden disparar
// builds sin limite hasta agotar la cuota de la cuenta. Por eso vive aca, en
// una variable de entorno del servidor, y esta funcion la usa solo despues de
// comprobar que quien pide tiene una sesion valida del panel.

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");

  if (req.method !== "POST") {
    return res.status(405).json({ error: "Método no permitido." });
  }

  const hook = process.env.VERCEL_DEPLOY_HOOK;
  const supabaseUrl = process.env.SUPABASE_URL;
  const anonKey = process.env.SUPABASE_ANON_KEY;

  if (!hook || !supabaseUrl || !anonKey) {
    console.error(
      "Faltan variables de entorno: VERCEL_DEPLOY_HOOK, SUPABASE_URL o SUPABASE_ANON_KEY."
    );
    return res
      .status(500)
      .json({ error: "La publicación no está configurada todavía." });
  }

  // --- quien pide ---------------------------------------------------------
  const cabecera = req.headers.authorization || "";
  const token = cabecera.startsWith("Bearer ") ? cabecera.slice(7) : "";
  if (!token) {
    return res.status(401).json({ error: "Falta la sesión." });
  }

  try {
    // Se le pregunta a Supabase si el token vale. No se valida la firma a mano:
    // eso obligaria a tener el secreto del proyecto en este servidor, que es
    // justo la llave que no queremos repartir.
    const quien = await fetch(supabaseUrl.replace(/\/+$/, "") + "/auth/v1/user", {
      headers: { apikey: anonKey, Authorization: "Bearer " + token },
    });

    if (!quien.ok) {
      return res.status(401).json({ error: "Tu sesión venció. Volvé a entrar." });
    }

    // --- disparar ---------------------------------------------------------
    const build = await fetch(hook, { method: "POST" });
    if (!build.ok) {
      console.error("El deploy hook contestó", build.status);
      return res.status(502).json({
        error: "No pudimos avisarle al servidor. Probá de nuevo en un minuto.",
      });
    }

    return res.status(200).json({
      ok: true,
      // El build tarda un par de minutos: el panel lo usa para no prometer
      // que el cambio ya se ve.
      demoraAproximada: "2 a 3 minutos",
    });
  } catch (e) {
    console.error("publicar", e);
    return res
      .status(500)
      .json({ error: "No pudimos conectar con el servidor." });
  }
};
