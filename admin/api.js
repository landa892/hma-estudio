/* Acceso a Supabase para el panel.
   ---------------------------------------------------------------------------
   No usa la libreria oficial a proposito. El sitio no tiene build ni framework
   —son archivos HTML sueltos— y su politica de seguridad solo admite scripts
   del propio dominio. Traer el SDK obligaba a versionar 100 KB de terceros
   para lo que aca son cinco llamadas HTTP. Con fetch alcanza y el proyecto
   sigue sin dependencias.

   Lo unico que hay que sostener a mano es el refresco del token: el de acceso
   dura una hora y si no se renueva el panel se corta a mitad de una carga. */

(function () {
  'use strict';

  var cfg = window.HMA_CONFIG;
  if (!cfg || !cfg.SUPABASE_URL) {
    throw new Error('Falta admin/config.js. Copialo de admin/config.ejemplo.js.');
  }

  var BASE = cfg.SUPABASE_URL.replace(/\/+$/, '');
  var CLAVE = cfg.SUPABASE_ANON_KEY;
  var GUARDADO = 'hma.sesion';

  /* --- sesion ----------------------------------------------------------- */

  /* Va en localStorage y no en sessionStorage para que cerrar la pestaña no
     obligue a entrar de nuevo: el estudio carga una obra en varios ratos. */
  function leerSesion() {
    try {
      return JSON.parse(localStorage.getItem(GUARDADO)) || null;
    } catch (e) {
      return null;
    }
  }

  function guardarSesion(s) {
    if (!s || !s.access_token) return null;
    var sesion = {
      access_token: s.access_token,
      refresh_token: s.refresh_token,
      // expires_at viene en segundos; se guarda en milisegundos y con un
      // minuto de margen para no usar un token que expira en el camino.
      vence: (s.expires_at ? s.expires_at * 1000 : Date.now() + s.expires_in * 1000) - 60000,
      email: s.user && s.user.email,
    };
    localStorage.setItem(GUARDADO, JSON.stringify(sesion));
    return sesion;
  }

  function borrarSesion() {
    localStorage.removeItem(GUARDADO);
  }

  /* --- llamadas --------------------------------------------------------- */

  function pedir(ruta, opciones) {
    opciones = opciones || {};
    var cabeceras = { apikey: CLAVE, 'Content-Type': 'application/json' };
    if (opciones.token) cabeceras.Authorization = 'Bearer ' + opciones.token;

    return fetch(BASE + ruta, {
      method: opciones.method || 'GET',
      headers: cabeceras,
      body: opciones.body ? JSON.stringify(opciones.body) : undefined,
    }).catch(function () {
      // Cuando fetch se rechaza no hay respuesta HTTP que traducir: sin esto
      // al usuario le llegaba el "Failed to fetch" del navegador, en ingles.
      var e = new Error('No pudimos conectar con el servidor. '
        + 'Revisá tu conexión y probá de nuevo.');
      e.sinRed = true;
      throw e;
    }).then(function (r) {
      return r.text().then(function (t) {
        var datos = null;
        try { datos = t ? JSON.parse(t) : null; } catch (e) { datos = null; }
        if (!r.ok) {
          var e = new Error(mensaje(r.status, datos));
          e.status = r.status;
          e.datos = datos;
          throw e;
        }
        return datos;
      });
    });
  }

  /* Supabase contesta en ingles y con jerga. El panel lo usa una persona que no
     programa, asi que los casos que va a ver de verdad se traducen. */
  function mensaje(status, datos) {
    var crudo = (datos && (datos.error_description || datos.msg || datos.message)) || '';

    if (/Invalid login credentials/i.test(crudo)) {
      return 'El correo o la contraseña no son correctos.';
    }
    if (/Email not confirmed/i.test(crudo)) {
      return 'Todavía no confirmaste tu correo. Buscá el mail de alta.';
    }
    if (/should be at least/i.test(crudo)) {
      return 'La contraseña es demasiado corta: tiene que tener 8 caracteres o más.';
    }
    if (status === 429) {
      return 'Demasiados intentos seguidos. Esperá un minuto y probá de nuevo.';
    }
    if (status === 401 || status === 403) {
      return 'Tu sesión venció. Volvé a entrar.';
    }
    if (!crudo) {
      return 'No pudimos conectar con el servidor. Revisá tu conexión.';
    }
    return crudo;
  }

  /* --- autenticacion ---------------------------------------------------- */

  function entrar(email, clave) {
    return pedir('/auth/v1/token?grant_type=password', {
      method: 'POST',
      body: { email: email, password: clave },
    }).then(guardarSesion);
  }

  function refrescar(sesion) {
    return pedir('/auth/v1/token?grant_type=refresh_token', {
      method: 'POST',
      body: { refresh_token: sesion.refresh_token },
    }).then(guardarSesion).catch(function (e) {
      // Si el refresh token ya no vale no hay nada que rescatar: se limpia
      // para que el panel mande al login en vez de reintentar en loop.
      borrarSesion();
      throw e;
    });
  }

  /* Devuelve un token de acceso vigente, renovandolo si hace falta.
     Todo lo que hable con la base tiene que pasar por aca. */
  function token() {
    var s = leerSesion();
    if (!s) return Promise.reject(new Error('Sin sesión.'));
    if (Date.now() < s.vence) return Promise.resolve(s.access_token);
    return refrescar(s).then(function (nueva) { return nueva.access_token; });
  }

  function salir() {
    var s = leerSesion();
    borrarSesion();
    if (!s) return Promise.resolve();
    // Se avisa al servidor para invalidar el refresh token, pero la sesion
    // local ya se borro: si la llamada falla el usuario igual quedo afuera.
    return pedir('/auth/v1/logout', { method: 'POST', token: s.access_token })
      .catch(function () {});
  }

  function recuperar(email) {
    return pedir('/auth/v1/recover', {
      method: 'POST',
      body: {
        email: email,
        redirect_to: location.origin + '/admin/nueva-clave',
      },
    });
  }

  /* Cambia la contraseña. En el flujo de recupero el token no sale de la
     sesion guardada sino del enlace del mail, asi que se puede pasar aparte. */
  function cambiarClave(nueva, tokenSuelto) {
    var conToken = tokenSuelto ? Promise.resolve(tokenSuelto) : token();
    return conToken.then(function (t) {
      return pedir('/auth/v1/user', {
        method: 'PUT',
        token: t,
        body: { password: nueva },
      });
    });
  }

  /* --- guardia de las paginas del panel --------------------------------- */

  /* El panel es HTML estatico: esto solo evita mostrar la pantalla a quien no
     entro. Lo que de verdad protege los datos es el RLS de la base, que no
     devuelve ni un borrador sin un token valido. Si alguien abre el HTML a
     mano, ve el cascaron vacio. */
  function exigirSesion() {
    var s = leerSesion();
    if (!s) {
      location.replace('/admin/?volver=' + encodeURIComponent(location.pathname));
      return Promise.reject(new Error('Sin sesión.'));
    }
    return token().catch(function (e) {
      location.replace('/admin/');
      throw e;
    });
  }

  window.HMA = {
    entrar: entrar,
    salir: salir,
    recuperar: recuperar,
    cambiarClave: cambiarClave,
    token: token,
    sesion: leerSesion,
    exigirSesion: exigirSesion,
    BASE: BASE,
    CLAVE: CLAVE,
  };
})();
