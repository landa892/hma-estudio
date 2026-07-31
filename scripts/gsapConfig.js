/* ============================================================================
   gsapConfig.js — configuracion base de GSAP para el sitio.

   Se carga despues de gsap y ScrollTrigger y antes de animations.js y
   scroll.js. Registra el plugin, fija los defaults y publica en
   window.HMA un namespace chico con lo que comparten los otros modulos:
   easings, duraciones, helpers y el estado de accesibilidad.

   Si GSAP no cargo (bloqueo de red, CSP, JS desactivado) este archivo no
   hace nada y el sitio sigue funcionando con el reveal por CSS de main.js:
   la clase gsap-active es la que decide quien manda.
   ========================================================================= */

(function (window, document) {
  'use strict';

  var gsap = window.gsap;
  if (!gsap || !window.ScrollTrigger) return;

  gsap.registerPlugin(window.ScrollTrigger);

  var root = document.documentElement;

  /* --- Accesibilidad -------------------------------------------------------
     Con prefers-reduced-motion el sitio no anima nada: marcamos la clase para
     que el CSS deje todo visible y scroll.js no arme ninguna timeline. */
  var mq = window.matchMedia('(prefers-reduced-motion: reduce)');
  var reduced = mq.matches;

  root.classList.add('gsap-active');
  if (reduced) root.classList.add('gsap-reduced');

  /* Si el usuario cambia la preferencia, recargamos el estado sin recargar la
     pagina: matarlo todo es mas seguro que intentar revertir a mano. */
  var onChange = function () {
    if (mq.matches !== reduced) window.location.reload();
  };
  if (mq.addEventListener) mq.addEventListener('change', onChange);
  else if (mq.addListener) mq.addListener(onChange);

  /* --- Defaults ------------------------------------------------------------
     force3D deja todo en la capa del compositor. Solo animamos transform,
     opacity y clip-path, asi que nunca disparamos reflow. */
  gsap.defaults({ ease: 'none', overwrite: 'auto', force3D: true });

  gsap.config({ nullTargetWarn: false });

  /* lagSmoothing evita que un salto de frame (una pestana en segundo plano,
     una imagen pesada decodificando) haga saltar la animacion de golpe. */
  gsap.ticker.lagSmoothing(500, 33);

  ScrollTrigger.config({
    /* En iOS el resize por la barra de direcciones dispara refreshes
       constantes; ignorarlo evita saltos al scrollear. */
    ignoreMobileResize: true,
    limitCallbacks: true
  });

  /* --- Easings -------------------------------------------------------------
     Con scrub el easing de la tween se aplana, asi que las curvas viven en la
     posicion de cada tween dentro de la timeline y en las animaciones que no
     son de scrub. Estas son las dos que usa el sitio. */
  var EASE = {
    /* Entrada: arranca rapido y se asienta. Es la curva del CSS del sitio. */
    out: 'cubic-bezier(0.16, 0.6, 0.3, 1)',
    /* Recorridos largos ligados al scroll. */
    through: 'power1.inOut'
  };

  /* --- Helpers -------------------------------------------------------------- */

  /* Parte un titulo en palabras envueltas en <span>, para poder escalonarlas.
     Solo toca elementos de texto plano: si el titulo tiene un enlace u otro
     elemento adentro lo deja intacto y devuelve null, y quien llama anima el
     bloque entero. Sin plugins: SplitText no hace falta para esto. */
  function splitWords(el) {
    if (!el || el.dataset.split === 'done') {
      return el ? Array.prototype.slice.call(el.querySelectorAll('.word > span')) : null;
    }
    if (el.children.length) return null;

    var words = el.textContent.trim().split(/\s+/);
    if (words.length < 2 || words.length > 24) return null;

    var frag = document.createDocumentFragment();
    var inners = [];
    words.forEach(function (w, i) {
      /* Dos capas: la de afuera recorta, la de adentro se mueve. Asi el
         desplazamiento se ve como si la palabra subiera desde su renglon. */
      var outer = document.createElement('span');
      outer.className = 'word';
      var inner = document.createElement('span');
      inner.textContent = w;
      outer.appendChild(inner);
      frag.appendChild(outer);
      if (i < words.length - 1) frag.appendChild(document.createTextNode(' '));
      inners.push(inner);
    });

    el.textContent = '';
    el.appendChild(frag);
    el.dataset.split = 'done';
    return inners;
  }

  window.HMA = window.HMA || {};
  window.HMA.gsap = {
    reduced: reduced,
    EASE: EASE,
    splitWords: splitWords,

    /* Rango de entrada pedido: la animacion vive entre que el bloque asoma por
       abajo y que casi termina de salir por arriba, atada al scroll. */
    ENTER: { start: 'top 80%', end: 'bottom 20%', scrub: true },

    /* Rango de recorrido: para parallax y escalados, que necesitan el largo
       completo de la seccion para leerse bien. */
    THROUGH: { start: 'top top', end: 'bottom top', scrub: true }
  };
})(window, document);
