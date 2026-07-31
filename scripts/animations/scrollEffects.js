/* ============================================================================
   animations/scrollEffects.js — el resto de la pagina.

   Las portadas —el hero y los banners de proyecto— tienen su modulo aparte
   porque son una secuencia de autor. Todo lo demas responde a cuatro patrones
   repetidos, que es lo que hace que el sitio se lea como una sola pieza:

     block     un bloque aparece y despues deriva unos pixeles
     heading   un titulo emerge por lineas desde una mascara
     stagger   una grilla se arma, cada pieza con su propio disparador
     parallax  una foto que se mueve dentro de su marco

   Reparto de la ventana de scroll: el rango va de "top 80%" a "bottom 20%",
   pero la aparicion se resuelve en el primer 38% y el resto es deriva. Si la
   aparicion ocupara todo el rango, el texto estaria a media opacidad
   justamente mientras se lee.

   Solo se animan transform, opacity y clip-path. Nada que dispare reflow.
   ========================================================================= */

(function (window, document) {
  'use strict';

  var gsap = window.gsap;
  var CFG = window.HMA && window.HMA.config;
  var TR = window.HMA && window.HMA.textReveal;
  if (!gsap || !CFG || !TR) return;
  if (CFG.reduced) return;

  var EASE = CFG.EASE;
  var ENTER = CFG.ENTER;
  var THROUGH = CFG.THROUGH;

  var IN = 0.38;    // fin de la aparicion, en fraccion del recorrido
  var DERIVA = 10;  // px de parallax despues de aparecer
  var SUBE = 34;    // px que sube un bloque al entrar

  var q = function (sel, ctx) {
    return Array.prototype.slice.call((ctx || document).querySelectorAll(sel));
  };

  /* Los disparadores de aparicion llevan id "in:". Se usa mas abajo para
     asentarlos: si el bloque ya esta en pantalla, su aparicion espera un
     scroll que no va a ocurrir. Los de recorrido no llevan id. */
  var seq = 0;
  function inTrigger(el, cfg, extra) {
    var t = { trigger: el, start: cfg.start, end: cfg.end, scrub: 0.6, id: 'in:' + (seq++) };
    if (extra) for (var k in extra) t[k] = extra[k];
    return t;
  }
  function thruTrigger(el, cfg, extra) {
    var t = { trigger: el, start: cfg.start, end: cfg.end, scrub: true };
    if (extra) for (var k in extra) t[k] = extra[k];
    return t;
  }

  function drift(tl, target, amount) {
    return tl.to(target, { y: -(amount || DERIVA), duration: 1 - IN, ease: EASE.linear }, IN);
  }

  /* ------------------------------------------------------------------ base */

  function block(el, opts) {
    opts = opts || {};
    var tl = gsap.timeline({ scrollTrigger: inTrigger(el, ENTER) })
      .fromTo(el,
        { y: opts.distance || SUBE, opacity: 0 },
        { y: 0, opacity: 1, duration: IN, ease: EASE.settle }, 0);
    return drift(tl, el, opts.drift);
  }

  function heading(el, opts) {
    opts = opts || {};
    var lineas = TR.splitLines(el);
    var tl = gsap.timeline({ scrollTrigger: inTrigger(opts.scope || el, ENTER) });
    if (lineas) {
      var ap = TR.emerge(lineas, { blur: 4, stagger: 0.1 });
      ap.duration(IN);
      tl.add(ap, 0);
    } else {
      tl.fromTo(el, { y: SUBE, opacity: 0 },
        { y: 0, opacity: 1, duration: IN, ease: EASE.settle }, 0);
    }
    return drift(tl, el);
  }

  function wipe(el) {
    var tl = gsap.timeline({ scrollTrigger: inTrigger(el, ENTER) });
    tl.add(TR.wipe(el, { duration: IN }), 0);
    /* La deriva ademas rellena la timeline hasta duracion 1, para que el
       reparto se mida contra el recorrido completo. */
    return drift(tl, el, 6);
  }

  /* Grillas: un disparador por pieza, no el del contenedor. Con 47 proyectos o
     30 videos, el contenedor mide miles de pixeles y las piezas de abajo
     llegaban a pantalla todavia apagadas. El escalonado sale de agrupar por
     fila con offsetTop: dentro de cada fila, cada pieza arranca un poco
     despues que la anterior. */
  function stagger(el, selector, opts) {
    opts = opts || {};
    var items = q(selector, el);
    if (!items.length) return null;

    var filas = {};
    items.forEach(function (item) {
      (filas[item.offsetTop] = filas[item.offsetTop] || []).push(item);
    });

    var paso = (opts.each || 0.06) * 100;
    return items.map(function (item) {
      var col = filas[item.offsetTop].indexOf(item);
      var desfase = Math.min(col * paso, 12);
      return gsap.timeline({
        scrollTrigger: {
          trigger: item,
          start: 'top ' + (88 - desfase) + '%',
          end: 'top ' + (52 - desfase) + '%',
          scrub: 0.6,
          id: 'in:' + (seq++)
        }
      }).fromTo(item,
        { y: opts.distance || SUBE, opacity: 0 },
        { y: 0, opacity: 1, duration: 1, ease: EASE.settle }, 0);
    });
  }

  function parallax(el, opts) {
    opts = opts || {};
    var amount = opts.amount || 70;
    gsap.set(el, { scale: 1.14, transformOrigin: 'center center' });
    gsap.timeline({ scrollTrigger: thruTrigger(opts.scope || el, THROUGH, { start: 'top bottom' }) })
      .fromTo(el, { y: -amount / 2 }, { y: amount / 2, duration: 1, ease: EASE.linear }, 0);
  }

  /* --------------------------------------------------------------- el guion */

  /* El partido en lineas mide donde cae cada palabra, asi que depende de la
     fuente ya cargada: con la de reserva las metricas son mas anchas y el
     titulo se parte en una linea por palabra. Se espera a document.fonts. */
  function alEstarLista(fn) {
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () {
        fn();
        ScrollTrigger.refresh();
      });
    } else {
      fn();
    }
  }

  var mm = gsap.matchMedia();
  mm.add('(prefers-reduced-motion: no-preference)', function () {
    alEstarLista(function () {

    /* Las portadas —el hero y los seis banners de proyecto— las maneja
       heroAnimation.js con la secuencia de cuatro fases. */

    /* Portada de texto de las fichas de obra y paginas internas. */
    q('.hero-home').forEach(function (el) {
      var h1 = el.querySelector('h1');
      if (h1) heading(h1, { scope: el });
      var eyebrow = el.querySelector('.eyebrow');
      if (eyebrow) wipe(eyebrow);
      var lede = el.querySelector('.lede');
      if (lede) block(lede);
      var specs = el.querySelector('.project-specs');
      if (specs) stagger(specs, '.spec-row', { each: 0.05, distance: 18 });
      var meta = el.querySelector('.project-meta-row');
      if (meta) block(meta, { distance: 18 });
    });

    q('.banner-interlude').forEach(function (el) { block(el.querySelector('p') || el); });

    q('.section-head').forEach(function (el) {
      var eyebrow = el.querySelector('.eyebrow');
      if (eyebrow) wipe(eyebrow);
      var h = el.querySelector('h1, h2, h3');
      if (h) heading(h, { scope: el });
      var cta = el.querySelector('.btn');
      if (cta) block(cta, { distance: 16 });
    });

    q('.project-row').forEach(function (el) {
      var text = el.querySelector('.project-row__text');
      if (text) block(text);
      var img = el.querySelector('.project-row__photo img');
      if (img) parallax(img, { scope: el });
    });

    q('.project-grid').forEach(function (el) { stagger(el, '.project-card'); });
    q('.project-list').forEach(function (el) { stagger(el, '.project-list-row', { each: 0.03, distance: 18 }); });
    q('.gallery-grid').forEach(function (el) { stagger(el, '.gallery-grid__item', { each: 0.05 }); });
    q('.press-featured').forEach(function (el) { stagger(el, '.press-card', { each: 0.04 }); });
    q('.related-projects').forEach(function (el) { stagger(el, '.project-card', { each: 0.08 }); });
    /* Los sellos del pie no se animan: estan al final de la pagina, donde el
       disparador de entrada llega tarde, y encima el CSS los deja al 60% de
       opacidad. Sumar una aparicion encima los volvia invisibles. */
    q('.award-bar__logos').forEach(function (el) { stagger(el, '.award-bar__item', { each: 0.06, distance: 18 }); });
    q('.press-feed').forEach(function (el) { stagger(el, '.press-row', { each: 0.02, distance: 16 }); });
    q('.award-feed').forEach(function (el) { stagger(el, '.award-row', { each: 0.03, distance: 16 }); });
    q('.stat-row').forEach(function (el) { stagger(el, '.stat-cell', { each: 0.1 }); });

    /* Lo que quedo con .reveal y no cayo en ninguna regla anterior. */
    q('.reveal').forEach(function (el) {
      if (el.closest('.hero-home--photo, .project-banner')) return;
      if (el.matches('.project-grid, .project-list, .gallery-grid, .press-featured, .related-projects, .stat-row, .banner-interlude, .project-row')) return;
      block(el);
    });
    });
  });

  /* ------------------------------------------------------------- asentado */

  /* Una aparicion atada al scroll supone que el bloque va a entrar desde
     abajo. Si ya esta en pantalla —al cargar, o despues de filtrar, que
     reacomoda todo hacia arriba— ese scroll no va a ocurrir y el contenido se
     quedaria esperandolo. En ese caso se lo deja en su estado final y se
     retira el disparador. Solo alcanza a los de aparicion: el parallax y la
     salida de las portadas siguen ligados al scroll, que es su razon de ser. */
  function asentar() {
    ScrollTrigger.getAll().forEach(function (st) {
      if (!st.vars.id || st.vars.id.indexOf('in:') !== 0 || !st.animation) return;
      var el = st.trigger;
      if (!el) return;
      var r = el.getBoundingClientRect();
      if (r.bottom > 0 && r.top < window.innerHeight * 0.9 && st.progress < 1) {
        st.animation.progress(1);
        st.kill(false);
      }
    });
  }

  window.addEventListener('load', function () { ScrollTrigger.refresh(); asentar(); });
  requestAnimationFrame(asentar);

  /* Un refresh por imagen diferida es carisimo: la home tiene decenas y una
     ficha de obra puede tener cien. Cada refresh recalcula todos los
     disparadores de la pagina. Se agrupan: se espera a que dejen de llegar
     cargas por un cuarto de segundo y recien ahi se recalcula una sola vez. */
  var pendienteRefresco = null;
  var refrescarAgrupado = function () {
    clearTimeout(pendienteRefresco);
    pendienteRefresco = setTimeout(function () {
      ScrollTrigger.refresh();
      asentar();
    }, 250);
  };

  q('img[loading="lazy"]').forEach(function (img) {
    if (img.complete) return;
    img.addEventListener('load', refrescarAgrupado, { once: true });
  });

  /* Filtros, cambio grilla/lista y buscador mueven todo lo que viene despues. */
  var relayout = function () {
    requestAnimationFrame(function () { ScrollTrigger.refresh(); asentar(); });
  };
  q('.filter-btn, .view-toggle button').forEach(function (b) {
    b.addEventListener('click', relayout);
  });
  var buscador = document.getElementById('searchPageInput');
  if (buscador) buscador.addEventListener('input', relayout);
})(window, document);
