/* ============================================================================
   animations.js — una fabrica de timeline por tipo de seccion.

   Cada funcion recibe un elemento y devuelve una timeline de GSAP con su
   propio ScrollTrigger. No consultan el DOM por su cuenta ni deciden cuando
   correr: de eso se ocupa scroll.js. Asi cada efecto se puede leer, ajustar o
   sacar por separado.

   Regla que respetan todas: solo transform, opacity y clip-path. Ninguna
   propiedad que dispare reflow (top, left, width, height, margin, filter).
   ========================================================================= */

(function (window) {
  'use strict';

  var gsap = window.gsap;
  var HMA = window.HMA && window.HMA.gsap;
  if (!gsap || !HMA) return;

  var EASE = HMA.EASE;
  var ENTER = HMA.ENTER;
  var THROUGH = HMA.THROUGH;
  var splitWords = HMA.splitWords;

  /* Distancias en px. Chicas a proposito: el movimiento tiene que sugerir
     profundidad, no llamar la atencion. */
  var D = {
    rise: 34,        // cuanto sube un bloque al entrar
    word: 44,        // cuanto sube cada palabra de un titulo
    parallax: 90,    // recorrido de la foto de fondo
    lift: 26,        // cuanto se va hacia arriba lo que sale
    scaleIn: 0.965,  // escala de entrada de un titulo
    scaleImg: 1.12   // escala inicial de una foto con parallax
  };

  /* Los disparadores de entrada llevan id "in:". scroll.js los usa para
     asentarlos: si el bloque ya esta en pantalla —al cargar, o despues de
     filtrar— no tiene sentido que su aparicion dependa de un scroll que ya
     ocurrio, asi que se lo deja en su estado final y se retira el disparador.
     Los de recorrido (parallax, salida de portada) no llevan id y siguen
     atados al scroll siempre. */
  var seq = 0;

  function trigger(el, cfg, extra) {
    var t = { trigger: el, start: cfg.start, end: cfg.end, scrub: cfg.scrub, id: 'in:' + (seq++) };
    if (extra) for (var k in extra) t[k] = extra[k];
    return t;
  }

  /* Version sin id, para lo que tiene que seguir ligado al scroll siempre. */
  function through(el, cfg, extra) {
    var t = trigger(el, cfg, extra);
    delete t.id;
    return t;
  }

  /* Reparto de la ventana de scroll.

     El rango va de "top 80%" a "bottom 20%": arranca cuando el bloque asoma
     por abajo y termina cuando esta por salir por arriba. Si la aparicion
     ocupara todo ese rango, el texto estaria a media opacidad justo mientras
     se lee, que es lo contrario de lo que queremos.

     Entonces la aparicion se resuelve en el primer 45% del recorrido — para
     cuando el bloque llega al centro de la pantalla ya esta entero — y el 55%
     restante lo ocupa una deriva de pocos pixeles: ese es el parallax. */
  var IN = 0.38;   // fin de la aparicion, en fraccion del recorrido
  var DRIFT = 10;  // px que sigue subiendo despues, muy despacio

  /* Cola de parallax comun a los bloques de texto. */
  function drift(tl, target, amount) {
    return tl.fromTo(target, { y: 0 },
      { y: -(amount || DRIFT), duration: 1 - IN, ease: 'none' }, IN);
  }

  /* ---------------------------------------------------------------- titulos */

  /* Entrada de un titulo: las palabras suben escalonadas detras de un recorte,
     el bloque gana un punto de escala y aparece. Legible desde el primer
     frame porque nunca baja de 0.965 ni se desplaza mas de un renglon. */
  function heading(el, opts) {
    opts = opts || {};
    var words = splitWords(el);
    var tl = gsap.timeline({
      scrollTrigger: trigger(opts.scope || el, ENTER, { scrub: 0.6 })
    });

    if (words) {
      gsap.set(el, { perspective: 600 });
      tl.fromTo(words,
        { yPercent: 110, opacity: 0 },
        { yPercent: 0, opacity: 1, duration: IN, stagger: IN / 8, ease: EASE.out },
        0);
      tl.fromTo(el,
        { scale: D.scaleIn, transformOrigin: 'left center' },
        { scale: 1, duration: IN, ease: EASE.out },
        0);
      drift(tl, el);
    } else {
      tl.fromTo(el,
        { y: D.rise, opacity: 0, scale: D.scaleIn, transformOrigin: 'left center' },
        { y: 0, opacity: 1, scale: 1, duration: IN, ease: EASE.out },
        0);
      drift(tl, el);
    }
    return tl;
  }

  /* Entrada de portada, sin scrub.

     Lo que ya esta en pantalla cuando carga la pagina no puede ir atado al
     scroll: su punto de disparo quedo atras antes del primer frame, asi que
     con scrub aparecería a mitad de camino, con el titulo medio transparente
     y corrido. Para esas piezas usamos una entrada de una sola pasada, con
     easing propio. Todo lo que esta abajo del pliegue si va con scrub. */
  function intro(el) {
    var h = el.querySelector('h1, h2');
    var words = h ? splitWords(h) : null;
    var rest = el.querySelectorAll('.eyebrow, .lede, p, .project-meta-row, .project-specs');
    var tl = gsap.timeline({ delay: 0.15 });

    /* Red de seguridad: si por lo que sea la timeline no llega a correr
       (pestana en segundo plano al cargar, un error mas arriba), a los dos
       segundos y medio dejamos la portada en su estado final. Nunca vale la
       pena que una animacion se coma el titulo de la home. */
    var guard = setTimeout(function () { tl.progress(1); }, 2500);
    tl.eventCallback('onComplete', function () { clearTimeout(guard); });

    if (words) {
      gsap.set(el, { perspective: 600 });
      tl.fromTo(words, { yPercent: 110, opacity: 0 },
        { yPercent: 0, opacity: 1, duration: 1, stagger: 0.075, ease: EASE.out }, 0);
    } else if (h) {
      tl.fromTo(h, { y: D.word, opacity: 0 },
        { y: 0, opacity: 1, duration: 1, ease: EASE.out }, 0);
    }
    if (rest.length) {
      tl.fromTo(rest, { y: D.rise, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.9, stagger: 0.09, ease: EASE.out }, 0.25);
    }
    return tl;
  }

  /* Bloque generico (parrafos, tarjetas sueltas, fichas). */
  function block(el, opts) {
    opts = opts || {};
    var tl = gsap.timeline({ scrollTrigger: trigger(el, ENTER, { scrub: 0.6 }) })
      .fromTo(el,
        { y: opts.distance || D.rise, opacity: 0 },
        { y: 0, opacity: 1, duration: IN, ease: EASE.out },
        0);
    return drift(tl, el, opts.drift);
  }

  /* Grupo de hijos que entran escalonados (grillas de tarjetas).

     Cada tarjeta lleva su propio disparador, no el del contenedor. En una
     grilla alta —los 47 proyectos, los 30 videos— usar el contenedor hace que
     las tarjetas de abajo lleguen a pantalla todavia apagadas, porque su
     progreso depende de donde esta el bloque entero y no de donde esta la
     tarjeta. Con disparador propio cada una aparece cuando le toca.

     El escalonado sale de agrupar por fila: las tarjetas que comparten
     offsetTop estan en la misma fila, y dentro de la fila cada una arranca un
     poco despues que la anterior. Asi la grilla se arma de izquierda a
     derecha y de arriba hacia abajo. */
  function stagger(el, selector, opts) {
    opts = opts || {};
    var items = Array.prototype.slice.call(el.querySelectorAll(selector));
    if (!items.length) return null;

    var filas = {};
    items.forEach(function (item) {
      var fila = item.offsetTop;
      filas[fila] = filas[fila] || [];
      filas[fila].push(item);
    });

    var step = (opts.each || 0.06) * 100;   // en % de viewport
    return items.map(function (item) {
      var col = filas[item.offsetTop].indexOf(item);
      /* Cuanto mas a la derecha, un poco mas tarde. Tope de 12% para que la
         ultima columna no quede demasiado rezagada. */
      var offset = Math.min(col * step, 12);
      return gsap.timeline({
        scrollTrigger: {
          trigger: item,
          start: 'top ' + (88 - offset) + '%',
          end: 'top ' + (52 - offset) + '%',
          scrub: 0.6,
          id: 'in:' + (seq++)
        }
      }).fromTo(item,
        { y: opts.distance || D.rise, opacity: 0 },
        { y: 0, opacity: 1, duration: 1, ease: EASE.out },
        0);
    });
  }

  /* Revelado con clip-path: la barra se abre de izquierda a derecha. Se usa
     poco, para los antetitulos, que son la linea mas corta de cada seccion. */
  function wipe(el) {
    var tl = gsap.timeline({ scrollTrigger: trigger(el, ENTER, { scrub: 0.6 }) })
      .fromTo(el,
        { clipPath: 'inset(0 100% 0 0)', opacity: 0 },
        { clipPath: 'inset(0 0% 0 0)', opacity: 1, duration: IN, ease: EASE.out },
        0);
    /* La deriva no es decorativa aca: rellena la timeline hasta duracion 1
       para que el reparto 38 / 62 se mida contra el recorrido completo. Sin
       ella el revelado se estiraria sobre toda la ventana de scroll. */
    return drift(tl, el, 6);
  }

  /* -------------------------------------------------------------- portadas */

  /* Hero y banners de proyecto comparten la misma coreografia:

       1. la foto entra escalada y se acomoda mientras se recorre la seccion
          (parallax vertical + desescalado): eso es la profundidad;
       2. el texto entra por palabras;
       3. al salir, el bloque de texto se achica hacia abajo-izquierda y se
          desvanece, para cederle el protagonismo a la seccion siguiente.

     El punto 3 es el gesto de mvrdv: transform-origin left bottom. Antes lo
     hacia un listener de scroll a mano en main.js; ahora lo maneja
     ScrollTrigger con scrub, que es mas preciso y no compite con el rAF. */
  function cover(section, opts) {
    opts = opts || {};
    var img = section.querySelector('img');
    var wrap = section.querySelector(opts.wrap);
    var inner = opts.inner ? section.querySelector(opts.inner) : wrap;
    var tls = [];

    if (img) {
      gsap.set(img, { scale: D.scaleImg, transformOrigin: 'center center' });
      tls.push(
        gsap.timeline({ scrollTrigger: through(section, THROUGH, { start: 'top bottom' }) })
          .to(img, { yPercent: 8, scale: 1, duration: 1, ease: EASE.through }, 0)
      );
    }

    if (inner && !opts.skipEnter) {
      var h = inner.querySelector('h1, h2');
      var words = h ? splitWords(h) : null;
      var rest = inner.querySelectorAll('.eyebrow, p');

      var enter = gsap.timeline({
        scrollTrigger: trigger(section, { start: 'top 85%', end: 'top 35%', scrub: 0.6 })
      });
      if (words) {
        enter.fromTo(words, { yPercent: 110, opacity: 0 },
          { yPercent: 0, opacity: 1, duration: 0.6, stagger: 0.07, ease: EASE.out }, 0);
      } else if (h) {
        enter.fromTo(h, { y: D.word, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.7, ease: EASE.out }, 0);
      }
      if (rest.length) {
        enter.fromTo(rest, { y: D.rise, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6, stagger: 0.08, ease: EASE.out }, 0.1);
      }
      tls.push(enter);
    }

    if (wrap) {
      /* La salida: escala hacia abajo-izquierda + un leve desplazamiento
         hacia arriba. Arranca justo cuando la seccion toca el borde superior
         de la pantalla, o sea recien cuando empezas a dejarla atras: hasta
         ahi el texto se lee entero, a escala 1 y opacidad 1. */
      tls.push(
        gsap.timeline({
          scrollTrigger: through(section, THROUGH)
        }).to(wrap, {
          scale: opts.minScale || 0.62,
          y: -D.lift,
          opacity: opts.fade === false ? 1 : 0.15,
          transformOrigin: 'left bottom',
          duration: 1,
          ease: EASE.through
        }, 0)
      );
    }

    return tls;
  }

  /* ------------------------------------------------------------- parallax */

  /* Parallax suelto para fotos dentro del flujo (las filas de las fichas de
     obra). Mueve la imagen dentro de su contenedor con overflow hidden. */
  function parallax(el, opts) {
    opts = opts || {};
    var amount = opts.amount || D.parallax;
    gsap.set(el, { scale: 1.14, transformOrigin: 'center center' });
    return gsap.timeline({ scrollTrigger: through(opts.scope || el, THROUGH, { start: 'top bottom' }) })
      .fromTo(el, { y: -amount / 2 }, { y: amount / 2, duration: 1, ease: 'none' }, 0);
  }

  window.HMA.animations = {
    D: D,
    intro: intro,
    heading: heading,
    block: block,
    stagger: stagger,
    wipe: wipe,
    cover: cover,
    parallax: parallax
  };
})(window);
