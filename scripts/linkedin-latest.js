/* Actualiza el bloque del home sin dejarlo vacio si LinkedIn no responde. */
(function () {
  'use strict';
  var bloque = document.getElementById('section-3');
  if (!bloque) return;
  fetch('/api/linkedin-latest').then(function (respuesta) {
    if (!respuesta.ok) throw new Error();
    return respuesta.json();
  }).then(function (nota) {
    // automatic:false significa que LinkedIn no esta conectado. En ese caso
    // manda el HTML que genero el panel: aplicar el respaldo fijo de la API
    // aca restauraba una noticia vieja despues de cada carga.
    if (!nota || nota.automatic !== true || !nota.url) return;
    bloque.querySelectorAll('[data-linkedin-link]').forEach(function (enlace) {
      enlace.href = nota.url;
    });
    var imagen = bloque.querySelector('[data-linkedin-image]');
    if (imagen && nota.image) imagen.src = nota.image;
    // La publicacion conserva su idioma original. En el espejo ingles se
    // actualiza enlace e imagen, pero no se inyecta castellano en el texto.
    if (!document.documentElement.lang.toLowerCase().startsWith('es')) return;
    var titulo = bloque.querySelector('[data-linkedin-title]');
    var texto = bloque.querySelector('[data-linkedin-text]');
    if (titulo && nota.title) titulo.textContent = nota.title;
    if (texto && nota.text) texto.textContent = nota.text;
  }).catch(function () { /* El HTML ya contiene la publicacion de respaldo. */ });
})();
