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

  function avisar(texto, tipo) {
    aviso.textContent = texto || '';
    aviso.className = 'aviso' + (texto ? ' aviso--' + tipo : '');
  }

  boton.addEventListener('click', function () {
    if (!window.confirm(
      'Esto actualiza el sitio con lo que hayas guardado.\n\n'
      + 'Tarda dos o tres minutos en verse. ¿Publicamos?')) return;

    boton.disabled = true;
    boton.textContent = 'Publicando…';
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
        boton.disabled = false;
        boton.textContent = 'Publicar cambios';
        // A esta altura el build deberia haber terminado y anotado la
        // publicacion, asi que el aviso de cambios pendientes ya puede irse.
        if (window.PENDIENTES) PENDIENTES.revisar();
      }, 120000);
    }).catch(function (e) {
      boton.disabled = false;
      boton.textContent = 'Publicar cambios';
      avisar(e.message, 'error');
    });
  });
})();
