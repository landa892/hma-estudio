/* ============================================================================
   scroll.js — arma el guion de cada pagina.

   Es el unico modulo que consulta el DOM. Busca las secciones que existen y
   le pide a animations.js la timeline que corresponde a cada una. Si una
   seccion no esta en la pagina, no pasa nada: el sitio comparte plantilla
   entre el home, las fichas de obra y las paginas internas.

   Con prefers-reduced-motion no arma ninguna timeline y sale enseguida; el
   CSS deja todo visible y en su lugar.
   ========================================================================= */

(function (window, document) {
  'use strict';

  var gsap = window.gsap;
  var HMA = window.HMA && window.HMA.gsap;
  var A = window.HMA && window.HMA.animations;
  if (!gsap || !HMA || !A) return;
  if (HMA.reduced) return;

  var q = function (sel, ctx) {
    return Array.prototype.slice.call((ctx || document).querySelectorAll(sel));
  };

  /* Un bloque esta "sobre el pliegue" si ya se ve al cargar. Esos entran con
     una animacion de una pasada; el resto va atado al scroll. */
  var aboveFold = function (el) {
    return el.getBoundingClientRect().top < window.innerHeight * 0.85;
  };

  /* gsap.matchMedia limpia solo las timelines cuando cambia el breakpoint,
     asi que el guion de escritorio y el de mobile no se pisan al rotar el
     telefono o al redimensionar la ventana. */
  var mm = gsap.matchMedia();

  /* ------------------------------------------------------------------------
     Guion comun a todos los anchos.
     ------------------------------------------------------------------------ */
  mm.add('(prefers-reduced-motion: no-preference)', function () {

    /* --- 1. Hero ---------------------------------------------------------
       La portada del home: foto con parallax, titulo por palabras y el
       achicado hacia abajo-izquierda al salir. */
    q('.hero-home--photo').forEach(function (el) {
      A.cover(el, {
        wrap: '.hero-content-wrap',
        minScale: 0.66,
        skipEnter: aboveFold(el)
      });
      if (aboveFold(el)) A.intro(el.querySelector('.hero-content-wrap'));
    });

    /* Hero de texto (fichas de obra y paginas internas): sin foto, el titulo
       entra por palabras y la ficha tecnica se escalona debajo. */
    q('.hero-home').forEach(function (el) {
      if (aboveFold(el)) { A.intro(el.querySelector('.container') || el); return; }
      var h1 = el.querySelector('h1');
      if (h1) A.heading(h1, { scope: el });
      var eyebrow = el.querySelector('.eyebrow');
      if (eyebrow) A.wipe(eyebrow);
      var lede = el.querySelector('.lede');
      if (lede) A.block(lede);
      var specs = el.querySelector('.project-specs');
      if (specs) A.stagger(specs, '.spec-row', { each: 0.05, distance: 18 });
      var meta = el.querySelector('.project-meta-row');
      if (meta) A.block(meta, { distance: 18 });
    });

    /* --- 2. Banners de proyecto del home --------------------------------- */
    q('.project-banner').forEach(function (el) {
      A.cover(el, { wrap: '.project-banner__content', inner: '.pb-content-inner', minScale: 0.58 });
    });

    /* --- 3. Interludios --------------------------------------------------- */
    q('.banner-interlude').forEach(function (el) {
      var p = el.querySelector('p');
      A.block(p || el);
    });

    /* --- 4. Encabezados de seccion ---------------------------------------- */
    q('.section-head').forEach(function (el) {
      var eyebrow = el.querySelector('.eyebrow');
      if (eyebrow) A.wipe(eyebrow);
      var h = el.querySelector('h1, h2, h3');
      if (h) A.heading(h, { scope: el });
      var cta = el.querySelector('.btn');
      if (cta) A.block(cta, { distance: 16 });
    });

    /* --- 5. Filas foto / texto de las fichas de obra ----------------------- */
    q('.project-row').forEach(function (el) {
      var text = el.querySelector('.project-row__text');
      if (text) A.block(text);
      var img = el.querySelector('.project-row__photo img');
      if (img) A.parallax(img, { scope: el, amount: 70 });
    });

    /* --- 6. Grillas ------------------------------------------------------- */
    q('.project-grid').forEach(function (el) { A.stagger(el, '.project-card'); });
    q('.project-list').forEach(function (el) { A.stagger(el, '.project-list-row', { each: 0.03, distance: 18 }); });
    q('.gallery-grid').forEach(function (el) { A.stagger(el, '.gallery-grid__item', { each: 0.05 }); });
    q('.press-featured').forEach(function (el) { A.stagger(el, '.press-card', { each: 0.04 }); });
    q('.related-projects').forEach(function (el) { A.stagger(el, '.project-card', { each: 0.08 }); });
    q('.footer-awards__row').forEach(function (el) { A.stagger(el, '.footer-award', { each: 0.03, distance: 16 }); });
    q('.award-bar__logos').forEach(function (el) { A.stagger(el, '.award-bar__item', { each: 0.06, distance: 18 }); });
    q('.press-feed').forEach(function (el) { A.stagger(el, '.press-row', { each: 0.02, distance: 16 }); });
    q('.award-feed').forEach(function (el) { A.stagger(el, '.award-row', { each: 0.03, distance: 16 }); });

    /* --- 7. Cifras -------------------------------------------------------- */
    q('.stat-row').forEach(function (el) { A.stagger(el, '.stat-cell', { each: 0.1 }); });

    /* --- 8. Bloques sueltos que quedaron con .reveal ----------------------
       Todo lo que lleva .reveal en el HTML y no cayo en ninguna regla de
       arriba entra con el fade generico, para que no quede nada invisible. */
    q('.reveal').forEach(function (el) {
      if (el.dataset.gsap === 'done') return;
      if (el.closest('.hero-home--photo, .project-banner')) return;
      if (el.matches('.project-grid, .project-list, .gallery-grid, .press-featured, .related-projects, .stat-row, .banner-interlude, .project-row')) return;
      A.block(el);
    });

    /* Marca los tratados para no duplicar si alguna vez se recarga el guion. */
    q('.reveal').forEach(function (el) { el.dataset.gsap = 'done'; });

    return function cleanup() {
      /* matchMedia revierte solas las tweens; solo devolvemos los flags. */
      q('[data-gsap]').forEach(function (el) { delete el.dataset.gsap; });
    };
  });

  /* ------------------------------------------------------------------------
     Refresh: las fotos que cargan tarde cambian el alto del documento y
     corren los puntos de disparo. Recalculamos cuando termina de cargar todo
     y cada vez que una imagen diferida entra.
     ------------------------------------------------------------------------ */
  window.addEventListener('load', function () { ScrollTrigger.refresh(); });

  q('img[loading="lazy"]').forEach(function (img) {
    if (img.complete) return;
    img.addEventListener('load', ScrollTrigger.refresh, { once: true });
  });

  /* Asentar lo que ya se ve.

     Una aparicion atada al scroll supone que el bloque va a entrar desde
     abajo. Si el bloque ya esta en pantalla —al cargar la pagina, o despues
     de filtrar, que reacomoda todo hacia arriba— ese scroll no va a ocurrir y
     el contenido se quedaria apagado esperandolo. Para esos casos dejamos la
     animacion en su estado final y retiramos el disparador.

     Solo alcanza a los disparadores de entrada (id "in:"). El parallax y la
     salida de las portadas siguen ligados al scroll, que es su razon de ser. */
  var settle = function () {
    ScrollTrigger.getAll().forEach(function (st) {
      if (!st.vars.id || st.vars.id.indexOf('in:') !== 0 || !st.animation) return;
      var el = st.trigger;
      if (!el) return;
      var r = el.getBoundingClientRect();
      var enPantalla = r.bottom > 0 && r.top < window.innerHeight * 0.9;
      if (enPantalla && st.progress < 1) {
        st.animation.progress(1);
        st.kill(false);          // retira el disparador, deja los valores puestos
      }
    });
  };

  /* Los filtros de Proyectos, Prensa y Premios y el cambio grilla/lista
     esconden y muestran bloques, asi que mueven todo lo que viene despues. */
  var relayout = function () {
    requestAnimationFrame(function () {
      ScrollTrigger.refresh();
      settle();
    });
  };

  /* Al terminar de cargar, y de nuevo cuando entra la ultima foto diferida. */
  window.addEventListener('load', settle);
  requestAnimationFrame(settle);
  q('.filter-btn, .view-toggle button').forEach(function (btn) {
    btn.addEventListener('click', relayout);
  });

  /* Buscador: los resultados se dibujan al escribir. */
  var buscador = document.getElementById('searchPageInput');
  if (buscador) buscador.addEventListener('input', relayout);
})(window, document);
