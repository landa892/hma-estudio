/* Mantiene la novedad de YouTube del Inicio en la misma fuente editorial que
   Nuestro canal. Instagram no ofrece una lectura publica equivalente: esa
   tarjeta se actualiza desde Novedades en el panel. */
(function () {
  'use strict';

  var bloque = document.getElementById('section-5');
  if (!bloque) return;

  fetch('/api/youtube-latest').then(function (respuesta) {
    if (!respuesta.ok) throw new Error();
    return respuesta.json();
  }).then(function (datos) {
    var video = datos && datos.videos && datos.videos[0];
    if (!video || !video.url || !video.thumbnail) return;

    bloque.querySelectorAll('[data-youtube-link]').forEach(function (enlace) {
      enlace.href = video.url;
    });
    var imagen = bloque.querySelector('[data-youtube-image]');
    if (imagen) {
      imagen.src = video.thumbnail;
      imagen.alt = video.title || 'Último video de Hitzig Militello Arquitectos';
    }

    // Los titulos del canal se publican en su idioma original. No se coloca
    // castellano nuevo dentro del espejo ingles.
    if (!document.documentElement.lang.toLowerCase().startsWith('es')) return;
    var titulo = bloque.querySelector('[data-youtube-title]');
    if (titulo && video.title) titulo.textContent = video.title;
  }).catch(function () { /* El HTML conserva una publicacion de respaldo. */ });
})();
