/* El boton "Publicar cambios".
   ---------------------------------------------------------------------------
   Guardar una obra la deja en la base, pero el sitio publico son archivos: hay
   que reconstruirlo para que el cambio se vea. Eso lo dispara este boton.

   No llama al deploy hook de Vercel directamente. La URL del hook vive en el
   servidor, en /api/publicar, porque cualquiera que abra el codigo de esta
   pagina la veria y con esa URL sola se pueden lanzar builds sin limite. */

(function () {
  'use strict';

  var boton = document.getElementById('publicar');
  if (!boton) return;

  var aviso = document.getElementById('aviso');
  var CLAVE_BLOQUEO = 'hma-publicando-hasta';
  var DURACION_BLOQUEO = 4 * 60 * 1000;
  var reloj = null;

  function avisar(texto, tipo) {
    aviso.textContent = texto || '';
    aviso.className = 'aviso' + (texto ? ' aviso--' + tipo : '');
  }

  function hastaBloqueado() {
    try {
      return Number(window.localStorage.getItem(CLAVE_BLOQUEO)) || 0;
    } catch (_) {
      return 0;
    }
  }

  function guardarBloqueo(hasta) {
    try {
      if (hasta) window.localStorage.setItem(CLAVE_BLOQUEO, String(hasta));
      else window.localStorage.removeItem(CLAVE_BLOQUEO);
    } catch (_) {
      /* El boton igual queda bloqueado en esta pestaña. */
    }
  }

  function reflejarBloqueo() {
    var restante = hastaBloqueado() - Date.now();
    if (restante > 0) {
      boton.disabled = true;
      boton.textContent = 'Publicando…';
      if (!reloj) reloj = window.setInterval(reflejarBloqueo, 1000);
      return true;
    }

    if (reloj) window.clearInterval(reloj);
    reloj = null;
    guardarBloqueo(0);
    boton.disabled = false;
    boton.textContent = 'Publicar cambios';
    return false;
  }

  /* El bloqueo persiste si recargan y se comparte entre pestañas. Esto evita
     que dos clics creen builds que lean dos estados distintos de las fotos. */
  reflejarBloqueo();
  window.addEventListener('storage', function (e) {
    if (e.key === CLAVE_BLOQUEO) reflejarBloqueo();
  });

  boton.addEventListener('click', function () {
    if (reflejarBloqueo()) {
      avisar('Ya hay una publicación en curso. Esperá a que termine.', 'ok');
      return;
    }

    if (!window.confirm(
      'Esto actualiza el sitio con lo que hayas guardado.\n\n'
      + 'Tarda dos o tres minutos en verse. ¿Publicamos?')) return;

    boton.disabled = true;
    boton.textContent = 'Publicando…';
    guardarBloqueo(Date.now() + DURACION_BLOQUEO);
    avisar('', 'ok');

    HMA.token().then(function (t) {
      return fetch('/api/publicar', {
        method: 'POST',
        headers: { Authorization: 'Bearer ' + t },
      });
    }).then(function (r) {
      return r.json().then(function (d) {
        if (!r.ok) throw new Error(d.error || 'No pudimos publicar.');
        return d;
      });
    }).then(function (d) {
      // El boton queda bloqueado un rato: apretarlo tres veces seguidas lanza
      // tres builds que se pisan entre si y ninguno termina antes.
      boton.textContent = 'Publicando…';
      avisar('Listo. El sitio se está actualizando: en ' + d.demoraAproximada
        + ' vas a ver los cambios.', 'ok');
      setTimeout(function () {
        guardarBloqueo(0);
        reflejarBloqueo();
        // A esta altura el build deberia haber terminado y anotado la
        // publicacion, asi que el aviso de cambios pendientes ya puede irse.
        if (window.PENDIENTES) PENDIENTES.revisar();
      }, DURACION_BLOQUEO);
    }).catch(function (e) {
      guardarBloqueo(0);
      reflejarBloqueo();
      avisar(e.message, 'error');
    });
  });
})();
