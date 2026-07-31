/* ============================================================================
   animations/heroAnimation.js — la portada, en cuatro fases.

   Toda la secuencia cuelga de una sola timeline con scrub, anclada al recorrido
   de la seccion (top top -> bottom top). No hay nada corriendo contra el reloj:
   si el usuario suelta la rueda, la animacion se queda donde esta.

   COMO ESTA ARMADO EL ESPACIO

   La seccion mide mas que la pantalla (la "pista": 240vh en escritorio) y
   adentro lleva un escenario sticky de 100vh. Mientras la pista se recorre, el
   escenario queda fijo y la secuencia ocurre a la vista; cuando la pista se
   agota, el escenario se despega y se va con el scroll.

   Sticky en vez de pin: ScrollTrigger sabe fijar elementos, pero inserta un
   espaciador y reescribe posiciones, y eso con Lenis encima suele dar un salto
   al entrar y al salir. position: sticky lo resuelve el compositor, sin tocar
   el layout.

   EL REPARTO

   S es la fraccion de la timeline durante la cual el escenario sigue pegado:
   (pista - 100vh) / pista. Todas las fases se ubican dentro de ese tramo, para
   que ninguna ocurra con la portada ya saliendo de pantalla.

     0.00 - 0.34 S   FASE 1  el titulo emerge desde la mascara, a escala 1.4
     0.34 - 0.46 S   FASE 2  sostiene el tamaño maximo: el golpe visual
     0.46 - 0.92 S   FASE 3  la camara se aleja, 1.4 -> 1
     0.60 - 0.90 S   FASE 4  entra el subtitulo, ya empezado el achique
     0.92 S - 1.00   salida  el bloque se va hacia abajo-izquierda

   La fase 4 arranca despues de la 3 a proposito: el dato secundario aparece
   cuando el impacto principal ya ocurrio.
   ========================================================================= */

(function (window, document) {
  'use strict';

  var gsap = window.gsap;
  var CFG = window.HMA && window.HMA.config;
  var TR = window.HMA && window.HMA.textReveal;
  if (!gsap || !CFG || !TR) return;
  if (CFG.reduced) return;

  var EASE = CFG.EASE;

  /* --- Perillas ------------------------------------------------------------

     REVELAR_AL_CARGAR: en false, que es lo pedido, el titulo no existe hasta
     que el usuario scrollea. Tiene un costo: la home abre con la portada
     vacia. Poniendolo en true, la fase 1 corre sola al cargar y el scroll
     arranca directamente en la fase 2, con el titulo ya grande. Es el unico
     cambio que hay que hacer para tener las dos cosas. */
  var REVELAR_AL_CARGAR = false;

  var ESCALA_FIN = 1;      // FASE 3

  /* Cada tipo de portada declara sus selectores y su escala de pico. La
     secuencia es la misma; lo que cambia es que la del hero pega mas fuerte
     (1,4) y la de los banners de proyecto un poco menos (1,25), porque se
     repite seis veces seguidas y a 1,4 cansaria. */
  var PORTADAS = [
    {
      seccion: '.hero-home--photo',
      wrap: '.hero-content-wrap',
      inner: '.hero-content-wrap',
      titulo: 'h1',
      sub: '.lede',
      pico: 1.4
    },
    {
      seccion: '.project-banner',
      wrap: '.project-banner__content',
      inner: '.pb-content-inner',
      titulo: 'h2',
      sub: '.pb-content-inner p',
      pico: 1.25
    }
  ];

  /* Recorridos verticales por punto de corte. En una pantalla chica el mismo
     desplazamiento en pixeles se come media pantalla, asi que se achica. */
  function metrica() {
    var b = CFG.bp();
    if (b.mobile) return { subeTitulo: 26, subeSub: 18, salida: 30, escalaSalida: 0.78 };
    if (b.tablet) return { subeTitulo: 40, subeSub: 24, salida: 44, escalaSalida: 0.72 };
    return { subeTitulo: 56, subeSub: 30, salida: 60, escalaSalida: 0.66 };
  }

  function construir(seccion, cfg) {
    var bloque = seccion.querySelector(cfg.wrap);
    var interior = seccion.querySelector(cfg.inner);
    var titulo = seccion.querySelector(cfg.titulo);
    var eyebrow = seccion.querySelector('.eyebrow');
    var sub = seccion.querySelector(cfg.sub);
    var foto = seccion.querySelector('img');
    if (!bloque || !titulo) return;
    var ESCALA_PICO = cfg.pico;

    var m = metrica();
    var lineas = TR.splitLines(titulo);

    /* Cuanto dura el tramo pegado, en fraccion de la timeline. Si por lo que
       sea la pista quedo mas corta que la pantalla, se cae a 0.6 para no
       dividir por cero ni amontonar todo al principio. */
    var pista = seccion.offsetHeight;
    var S = pista > window.innerHeight ? (pista - window.innerHeight) / pista : 0.6;

    var en = function (f) { return f * S; };

    var tl = gsap.timeline({
      scrollTrigger: {
        trigger: seccion,
        start: 'top top',
        end: 'bottom top',
        scrub: true,
        markers: false,
        invalidateOnRefresh: true
      }
    });

    /* ---------------------------------------------------------- FASE 1 y 2 */

    /* El titulo arranca en su tamaño maximo y ahi se queda hasta la fase 3: lo
       que cambia durante la aparicion no es el tamaño sino la existencia. */
    gsap.set(bloque, { scale: ESCALA_PICO, transformOrigin: 'left bottom' });

    var aparicion;
    if (lineas) {
      aparicion = TR.emerge(lineas, { blur: 8, stagger: 0.14 });
    } else {
      /* Titulo con marcado adentro: se anima el bloque, sin partirlo. */
      gsap.set(titulo, { yPercent: 40, opacity: 0, filter: 'blur(8px)' });
      aparicion = gsap.timeline().to(titulo,
        { yPercent: 0, opacity: 1, filter: 'blur(0px)', duration: 1, ease: EASE.reveal });
    }

    if (REVELAR_AL_CARGAR && cfg.pico === 1.4) {
      /* Corre sola al cargar; el scroll arranca en la fase 2. */
      aparicion.duration(1.6);
    } else {
      /* La fase 1 ocupa hasta 0.34 S. Se ajusta la duracion de la sub-timeline,
         no la de la padre, para no reescalar las fases que vienen despues.
         La fase 2 es el hueco que sigue, sin tweens: el titulo sostiene su
         tamaño maximo mientras el usuario sigue bajando. */
      aparicion.duration(en(0.34));
      tl.add(aparicion, 0);
    }

    /* La foto arranca su propio alejamiento desde el primer pixel: es lo que
       da la profundidad, porque se mueve a otra velocidad que el texto. */
    if (foto) {
      gsap.set(foto, { scale: 1.18, transformOrigin: 'center center' });
      tl.to(foto, {
        scale: 1,
        yPercent: 6,
        duration: en(0.92),
        ease: EASE.linear
      }, 0);
    }

    /* ------------------------------------------------------------- FASE 3 */

    tl.to(bloque, {
      scale: ESCALA_FIN,
      y: -m.subeTitulo,
      opacity: 0.92,
      duration: en(0.92) - en(0.46),
      ease: EASE.pull
    }, en(0.46));

    /* ------------------------------------------------------------- FASE 4 */

    /* El subtitulo entra recien pasada la mitad del achique. Mascara propia:
       el bloque se recorta y el texto sube desde adentro, mas corto que el del
       titulo porque es informacion secundaria y no tiene que competir. */
    if (sub) {
      gsap.set(sub, { clipPath: 'inset(0 0 100% 0)', opacity: 0, y: m.subeSub });
      tl.to(sub, {
        clipPath: 'inset(0 0 0% 0)',
        opacity: 1,
        y: 0,
        duration: en(0.90) - en(0.60),
        ease: EASE.settle
      }, en(0.60));
    }

    if (eyebrow) {
      gsap.set(eyebrow, { clipPath: 'inset(0 100% 0 0)', opacity: 0 });
      tl.to(eyebrow, {
        clipPath: 'inset(0 0% 0 0)',
        opacity: 1,
        duration: en(0.72) - en(0.50),
        ease: EASE.settle
      }, en(0.50));
    }

    /* -------------------------------------------------------------- salida */

    /* Cuando el escenario se despega, el bloque se va achicando hacia abajo a
       la izquierda. Es el mismo gesto que usan los banners de proyecto mas
       abajo, asi que el recorrido de la home se lee como una sola pieza. */
    tl.to(bloque, {
      scale: m.escalaSalida,
      y: -m.salida,
      opacity: 0.12,
      duration: 1 - en(0.92),
      ease: EASE.linear
    }, en(0.92));

    return tl;
  }

  /* matchMedia rearma la secuencia al cruzar un punto de corte y limpia sola
     las timelines viejas: sin esto, al rotar el telefono quedarian dos juegos
     de tweens peleando por el mismo transform. */
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
    PORTADAS.forEach(function (cfg) {
      Array.prototype.forEach.call(document.querySelectorAll(cfg.seccion), function (sec) {
        construir(sec, cfg);
      });
    });
    });
  });

  window.HMA.hero = { construir: construir };
})(window, document);
