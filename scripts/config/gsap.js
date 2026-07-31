/* ============================================================================
   config/gsap.js — motor de scroll y animacion.

   Monta las tres piezas y las hace hablar entre si:

     Lenis          interpola el scroll del navegador. Es lo que da la inercia:
                    la rueda del mouse deja de mover el documento de golpe y
                    pasa a empujar un valor que persigue su destino.
     GSAP           anima.
     ScrollTrigger  traduce posicion de scroll a progreso de timeline.

   El orden importa: Lenis tiene que correr dentro del ticker de GSAP y avisarle
   a ScrollTrigger en cada paso, si no quedan un frame desfasados y el scrub se
   ve tembloroso.

   Si algo de esto no cargo, el archivo no hace nada y el sitio queda con el
   reveal por CSS de main.js. La clase gsap-active es la que decide quien manda.
   ========================================================================= */

(function (window, document) {
  'use strict';

  var gsap = window.gsap;
  if (!gsap || !window.ScrollTrigger) return;

  gsap.registerPlugin(window.ScrollTrigger);

  var root = document.documentElement;
  var mq = window.matchMedia('(prefers-reduced-motion: reduce)');
  var reduced = mq.matches;

  root.classList.add('gsap-active');
  if (reduced) root.classList.add('gsap-reduced');

  var onPrefChange = function () {
    if (mq.matches !== reduced) window.location.reload();
  };
  if (mq.addEventListener) mq.addEventListener('change', onPrefChange);
  else if (mq.addListener) mq.addListener(onPrefChange);

  gsap.defaults({ overwrite: 'auto', force3D: true });
  gsap.config({ nullTargetWarn: false });
  ScrollTrigger.config({ ignoreMobileResize: true, limitCallbacks: true });

  /* --- Lenis ---------------------------------------------------------------
     lerp 0.09 da una inercia larga pero que responde: con valores mas altos se
     siente pegajoso y con mas bajos se pierde la sensacion de peso. El scroll
     tactil queda nativo a proposito: en un telefono la inercia del sistema es
     mejor que cualquier interpolacion y ademas evita pelearse con el rebote de
     iOS. Con prefers-reduced-motion no se instancia. */
  var lenis = null;
  if (!reduced && window.Lenis) {
    lenis = new window.Lenis({
      lerp: 0.09,
      wheelMultiplier: 1,
      smoothWheel: true,
      syncTouch: false,
      autoRaf: false
    });

    lenis.on('scroll', ScrollTrigger.update);

    gsap.ticker.add(function (time) {
      lenis.raf(time * 1000);
    });

    /* Con Lenis manejando el reloj, el suavizado de lag de GSAP sobra: seria
       una segunda interpolacion encima de la primera. */
    gsap.ticker.lagSmoothing(0);

    /* Los anclas internos tienen que pasar por Lenis; el scroll suave nativo
       del navegador no sabe de su posicion interpolada y pelea con ella. */
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href^="#"]');
      if (!a) return;
      var id = a.getAttribute('href');
      if (id.length < 2) return;
      var destino = document.querySelector(id);
      if (!destino) return;
      e.preventDefault();
      lenis.scrollTo(destino, { offset: -80, duration: 1.1 });
    });
  } else {
    gsap.ticker.lagSmoothing(500, 33);
  }

  /* --- Curvas --------------------------------------------------------------
     Con scrub el easing de cada tween sigue valiendo: define el reparto dentro
     de su tramo de la timeline, no contra el reloj. Por eso el titulo puede
     emerger despacio al principio y asentarse al final aunque el usuario
     scrollee a velocidad constante. */
  var EASE = {
    reveal: 'power3.inOut',   // la aparicion: entra pesada y frena
    /* El alejamiento de camara tiene que sentirse continuo: si se usa una
       curva out, el 90% del achique ocurre en el primer tramo y el resto del
       scroll no cambia nada. power1.inOut es casi lineal, con las puntas
       suaves, que es lo que hace una camara real al retroceder. */
    pull: 'power1.inOut',
    settle: 'power2.out',     // entradas secundarias
    linear: 'none'            // parallax
  };

  /* Puntos de corte. Se consultan por funcion y no se cachean para que el
     resize los vuelva a leer. */
  function bp() {
    var w = window.innerWidth;
    return { mobile: w < 700, tablet: w >= 700 && w < 1100, desktop: w >= 1100 };
  }

  window.HMA = window.HMA || {};
  window.HMA.config = {
    reduced: reduced,
    lenis: lenis,
    EASE: EASE,
    bp: bp,

    /* Rango de entrada: de que el bloque asoma por abajo a que sale por arriba. */
    ENTER: { start: 'top 80%', end: 'bottom 20%', scrub: true },

    /* Rango de recorrido, para parallax y escalados. */
    THROUGH: { start: 'top top', end: 'bottom top', scrub: true }
  };
})(window, document);
