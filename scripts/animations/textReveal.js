/* ============================================================================
   animations/textReveal.js — como aparece el texto.

   Tres primitivas, ninguna sabe de scroll ni de secciones: reciben un elemento
   y devuelven tweens o timelines que otro modulo coloca donde quiere.

     splitLines   parte un titulo en lineas dentro de una mascara
     emerge       la aparicion de una linea desde la mascara
     wipe         revelado lateral con clip-path, para lineas cortas

   La idea detras de "emerge": un fade no alcanza para que un texto parezca
   nacer. Lo que lo consigue es que el glifo este fisicamente fuera de su
   renglon y entre empujando, recortado por el borde de la mascara, con un
   desenfoque minimo que se va justo antes de que termine. El ojo lee eso como
   materia que toma forma, no como algo que se enciende.
   ========================================================================= */

(function (window, document) {
  'use strict';

  var gsap = window.gsap;
  var CFG = window.HMA && window.HMA.config;
  if (!gsap || !CFG) return;

  var EASE = CFG.EASE;

  /* --- Partido en lineas ---------------------------------------------------
     Se parte por palabra y despues se agrupan las palabras que quedaron en el
     mismo renglon, midiendo su offsetTop. Se agrupa por linea y no por palabra
     porque una mascara por palabra deja huecos verticales visibles cuando el
     titulo ocupa media pantalla: la linea entera subiendo como un bloque es lo
     que se lee como una sola pieza.

     Devuelve null si el elemento tiene hijos (un enlace, un <span> de cifra):
     ahi conviene animar el bloque entero antes que romperle el marcado. */
  function splitLines(el) {
    if (!el) return null;
    if (el.dataset.lines === 'done') {
      return Array.prototype.slice.call(el.querySelectorAll('.line > span'));
    }
    if (el.children.length) return null;

    /* Se parte por espacio comun y no por \s, que en JavaScript tambien
       alcanza al espacio duro. Un &nbsp; en el marcado existe justamente para
       que dos palabras no se separen nunca —"Creando &" en el home— y partir
       ahi lo anularia: el & terminaba solo en su propio renglon. */
    var palabras = el.textContent.trim().split(/[^\S\u00A0]+/);
    if (!palabras.length) return null;

    /* Paso 1: cada palabra en su span, para poder medir donde cae. */
    el.textContent = '';
    var spans = palabras.map(function (p, i) {
      var s = document.createElement('span');
      s.textContent = p;
      s.style.display = 'inline-block';
      el.appendChild(s);
      if (i < palabras.length - 1) el.appendChild(document.createTextNode(' '));
      return s;
    });

    /* Paso 2: agrupar por renglon. */
    var lineas = [];
    var actual = null;
    var topAnterior = null;
    spans.forEach(function (s) {
      var top = s.offsetTop;
      if (topAnterior === null || Math.abs(top - topAnterior) > 4) {
        actual = [];
        lineas.push(actual);
        topAnterior = top;
      }
      actual.push(s.textContent);
    });

    /* Paso 3: rearmar con una mascara por linea. */
    el.textContent = '';
    var interiores = [];
    lineas.forEach(function (palabrasDeLinea) {
      var mascara = document.createElement('span');
      mascara.className = 'line';
      var interior = document.createElement('span');
      interior.textContent = palabrasDeLinea.join(' ');
      mascara.appendChild(interior);
      el.appendChild(mascara);
      interiores.push(interior);
    });

    el.dataset.lines = 'done';
    return interiores;
  }

  /* --- Aparicion desde la mascara -----------------------------------------
     Estado de partida: la linea esta un 118% por debajo de su renglon, o sea
     completamente fuera de la mascara, invisible y desenfocada. El blur se
     resuelve en el primer 60% del tramo para que el texto termine de llegar ya
     nitido: si el desenfoque acompaña hasta el final, se lee como un error de
     foco en vez de como materia formandose.

     Devuelve una timeline sin ScrollTrigger. La coloca quien la llama. */
  function emerge(lineas, opts) {
    opts = opts || {};
    var blur = opts.blur === undefined ? 8 : opts.blur;
    var tl = gsap.timeline();

    gsap.set(lineas, {
      yPercent: 118,
      opacity: 0,
      filter: 'blur(' + blur + 'px)'
    });

    tl.to(lineas, {
      yPercent: 0,
      opacity: 1,
      duration: 1,
      ease: EASE.reveal,
      stagger: opts.stagger === undefined ? 0.12 : opts.stagger
    }, 0);

    tl.to(lineas, {
      filter: 'blur(0px)',
      duration: 0.6,
      ease: 'power2.out',
      stagger: opts.stagger === undefined ? 0.12 : opts.stagger
    }, 0);

    return tl;
  }

  /* --- Revelado lateral ---------------------------------------------------
     Para antetitulos y lineas de una sola palabra, donde una mascara vertical
     no se llega a percibir. */
  function wipe(el, opts) {
    opts = opts || {};
    return gsap.fromTo(el,
      { clipPath: 'inset(0 100% 0 0)', opacity: 0 },
      {
        clipPath: 'inset(0 0% 0 0)',
        opacity: 1,
        duration: opts.duration || 1,
        ease: EASE.settle
      });
  }

  window.HMA.textReveal = {
    splitLines: splitLines,
    emerge: emerge,
    wipe: wipe
  };
})(window, document);
