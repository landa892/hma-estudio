/* Actualiza Instagram y YouTube sin borrar el respaldo editorial del panel si
   alguno de los servicios externos deja de responder. */
(function () {
  'use strict';

  var instagram = document.getElementById('section-1');
  if (instagram) {
    // Las colaboraciones visibles en la grilla no aparecen en /me/media. El
    // estudio puede fijarlas desde el panel sin que la API vuelva a pisarlas.
    if (instagram.dataset.instagramMode !== 'manual') {
      fetch('/api/instagram-latest').then(function (respuesta) {
      if (!respuesta.ok) throw new Error();
      return respuesta.json();
    }).then(function (nota) {
      // automatic:false deja intactos texto, foto y enlace generados desde el
      // panel. Asi una falla de Meta nunca restaura una publicacion vieja.
      if (!nota || nota.automatic !== true || !nota.url) return;
      instagram.querySelectorAll('[data-instagram-link]').forEach(function (enlace) {
        enlace.href = nota.url;
      });
      var imagenInstagram = instagram.querySelector('[data-instagram-image]');
      if (imagenInstagram && nota.image) {
        imagenInstagram.src = nota.image;
        imagenInstagram.alt = document.documentElement.lang.toLowerCase().startsWith('es')
          ? nota.title : (nota.titleEn || 'Instagram — Hitzig Militello Arquitectos');
        var ajustarEncuadre = function () {
          // Instagram entrega muchas portadas cuadradas con placas o sellos en
          // el borde inferior. El bloque del Inicio es apaisado: se recorta la
          // portada desde arriba para conservar la obra y ocultar ese pie.
          imagenInstagram.style.objectFit = 'cover';
          imagenInstagram.style.objectPosition = 'center top';
          imagenInstagram.style.backgroundColor = '';
        };
        if (imagenInstagram.complete) ajustarEncuadre();
        else imagenInstagram.addEventListener('load', ajustarEncuadre, { once: true });
      }
      var es = document.documentElement.lang.toLowerCase().startsWith('es');
      var tituloInstagram = instagram.querySelector('[data-instagram-title]');
      var textoInstagram = instagram.querySelector('[data-instagram-text]');
      var tituloNota = es ? nota.title : nota.titleEn;
      var textoNota = es ? nota.text : nota.textEn;
      if (tituloInstagram && tituloNota) tituloInstagram.textContent = tituloNota;
      if (textoInstagram && textoNota) textoInstagram.textContent = textoNota;
      }).catch(function () { /* El HTML conserva la publicacion del panel. */ });
    }
  }

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
