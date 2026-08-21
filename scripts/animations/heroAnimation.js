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
      logo: '.hero-logo',
      pico: 1.4,
      obertura: true,
      escalaObertura: 1.58
    },
    {
      seccion: '.project-banner:not(.project-banner--split)',
      wrap: '.project-banner__content',
      inner: '.pb-content-inner',
      titulo: 'h2',
      sub: '.pb-content-inner p',
      pico: 1.25,
      obertura: true,
      escalaObertura: 1.35
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

  /* ==========================================================================
     LA OBERTURA DEL HOME

     Lo unico de todo el sitio que no depende del scroll. Al cargar, la
     portada se presenta sola:

       1. se ve la foto, nada mas
       2. el titulo emerge desde su mascara, enorme y centrado en pantalla
       3. sostiene ahi un par de segundos
       4. viaja hasta abajo a la izquierda y se achica a su tamaño de lectura
       5. recien entonces aparece la bajada, debajo del titulo

     El viaje se calcula, no se hardcodea. Con transformOrigin en el centro del
     propio titulo, llevarlo al centro de la pantalla es una traslacion que no
     depende de la escala: basta la diferencia entre el centro del titulo en su
     sitio final y el centro del escenario. Por eso el titulo aterriza exacto en
     su lugar sin importar el ancho de la ventana ni cuantas lineas ocupe.

     Se anima el titulo y no el bloque entero porque el bloque tambien contiene
     la bajada, que tiene que quedarse abajo esperando su turno. */
  /* Extension real de los glifos, no de la caja del elemento. Un h1 de bloque
     ocupa todo el ancho de su columna aunque el texto sea corto; para saber si
     entra hay que medir el texto. */
  function medirTexto(lineas, titulo) {
    var nodos = (lineas && lineas.length) ? lineas : [titulo];
    var l = Infinity, r = -Infinity, t = Infinity, b = -Infinity;
    nodos.forEach(function (n) {
      var rango = document.createRange();
      rango.selectNodeContents(n);
      var c = rango.getBoundingClientRect();
      if (!c.width && !c.height) return;
      l = Math.min(l, c.left); r = Math.max(r, c.right);
      t = Math.min(t, c.top); b = Math.max(b, c.bottom);
    });
    if (l === Infinity) {
      var f = titulo.getBoundingClientRect();
      return { ancho: f.width, alto: f.height, cx: f.left + f.width / 2, cy: f.top + f.height / 2 };
    }
    return { ancho: r - l, alto: b - t, cx: (l + r) / 2, cy: (t + b) / 2 };
  }

  function obertura(seccion, titulo, lineas, sub, eyebrow, opts) {
    opts = opts || {};
    var logo = opts.logo || null;
    var escenario = seccion.querySelector('.hero-stage') || seccion.querySelector('.banner-stage');
    var b = CFG.bp();
    /* Medido: a 1,7 el titulo se salia 27 px por la izquierda en 1440. El tope
       de escritorio lo deja ocupando cerca del 75% del ancho, sin tocar los
       bordes, y en pantallas chicas se achica proporcionalmente. */
    var tope = opts.escala || 1.58;
    var escala = b.mobile ? Math.min(tope, 1.3) : (b.tablet ? tope * 0.92 : tope);

    /* Y ademas se acota a lo que realmente entra. El tope de arriba es una
       intencion de diseño; esto es la restriccion fisica: el texto no puede
       salirse del escenario. Se mide el ancho y el alto reales de los glifos
       —no la caja del elemento, que ocupa toda la columna— y se calcula la
       escala maxima que los deja adentro con un margen del 14%. Asi cualquier
       titulo, en cualquier ventana, entra siempre. */
    /* Se mide con el titulo limpio. La obertura puede volver a lanzarse cuando
       el usuario sube y baja, y si midieramos con el transform de la vuelta
       anterior todavia puesto, la escala y el viaje irian acumulando error. */
    gsap.set(titulo, { clearProps: 'transform,scale,x,y' });
    var caja = medirTexto(lineas, titulo);
    var re1 = escenario.getBoundingClientRect();
    if (caja.ancho > 0 && caja.alto > 0) {
      escala = Math.min(escala,
        (re1.width * 0.86) / caja.ancho,
        (re1.height * 0.82) / caja.alto);
    }

    /* Medido con el titulo en su sitio final, antes de tocarlo, y sobre los
       glifos y no sobre la caja: un h1 es de bloque y ocupa todo el ancho de
       su columna aunque el texto sea corto, asi que centrar la caja dejaba el
       texto corrido a la izquierda y saliendose por ese lado. */
    var re = escenario.getBoundingClientRect();
    var viajeX = (re.left + re.width / 2) - caja.cx;
    var viajeY = (re.top + re.height / 2) - caja.cy;

    var tl = gsap.timeline({ delay: opts.delay === undefined ? 0.35 : opts.delay });

    /* Red de seguridad: si la timeline no llega a correr —pestaña en segundo
       plano, un error mas arriba— a los ocho segundos la portada queda en su
       estado final. Nunca vale la pena que una animacion se coma el titulo. */
    var guarda = setTimeout(function () { if (!tl.paused()) tl.progress(1); }, 9000);
    tl.eventCallback('onComplete', function () {
      clearTimeout(guarda);
      gsap.set(titulo, { willChange: 'auto' });
    });

    if (sub) gsap.set(sub, { clipPath: 'inset(0 0 100% 0)', opacity: 0, y: 18 });
    if (eyebrow) gsap.set(eyebrow, { clipPath: 'inset(0 100% 0 0)', opacity: 0 });
    if (logo) {
      /* En el home el gesto pertenece a la marca: HMA aparece grande en el
         centro, sostiene y viaja a su lugar definitivo. El claim entra recien
         despues. Antes hacia ese recorrido el titulo y el logo aparecia al
         final, que era exactamente el orden inverso al pedido. */
      gsap.set(logo, { clearProps: 'transform' });
      var cajaLogo = logo.getBoundingClientRect();
      var escalaLogo = Math.min(
        b.mobile ? 1.18 : 1.34,
        (re.width * (b.mobile ? 0.88 : 0.74)) / Math.max(cajaLogo.width, 1),
        (re.height * 0.38) / Math.max(cajaLogo.height, 1)
      );
      var viajeLogoX = (re.left + re.width / 2) - (cajaLogo.left + cajaLogo.width / 2);
      var viajeLogoY = (re.top + re.height / 2) - (cajaLogo.top + cajaLogo.height / 2);

      gsap.set(logo, {
        x: viajeLogoX, y: viajeLogoY, scale: escalaLogo,
        clipPath: 'inset(0 100% 0 0)', opacity: 0,
        transformOrigin: 'center center', willChange: 'transform'
      });
      tl.to(logo, {
        clipPath: 'inset(0 0% 0 0)', opacity: 1,
        duration: 1.25, ease: EASE.reveal
      }, 0);
      tl.to(logo, {
        x: 0, y: 0, scale: 1,
        duration: 1.5, ease: 'power3.inOut'
      }, 2.15);

      if (lineas) {
        var claim = TR.emerge(lineas, { blur: 10, stagger: 0.16 });
        claim.duration(1.15);
        tl.add(claim, 3.45);
      } else {
        gsap.set(titulo, { opacity: 0, filter: 'blur(10px)' });
        tl.to(titulo, { opacity: 1, filter: 'blur(0px)', duration: 1.15, ease: EASE.reveal }, 3.45);
      }
    } else {
      /* Los banners sin logo conservan su presentacion: el titulo es el que
         emerge en el centro y luego aterriza en su posicion. */
      gsap.set(titulo, {
        x: viajeX, y: viajeY, scale: escala,
        transformOrigin: 'center center',
        willChange: 'transform'
      });
      if (lineas) {
        var ap = TR.emerge(lineas, { blur: 10, stagger: 0.16 });
        ap.duration(1.5);
        tl.add(ap, 0);
      } else {
        gsap.set(titulo, { opacity: 0, filter: 'blur(10px)' });
        tl.to(titulo, { opacity: 1, filter: 'blur(0px)', duration: 1.5, ease: EASE.reveal }, 0);
      }
      tl.to(titulo, {
        x: 0, y: 0, scale: 1,
        duration: 1.5,
        ease: 'power3.inOut'
      }, 2.6);
    }

    /* La informacion secundaria entra cuando marca y titulo ya se leen. */
    if (eyebrow) {
      tl.to(eyebrow, { clipPath: 'inset(0 0% 0 0)', opacity: 1, duration: 0.7, ease: EASE.settle }, logo ? 4.2 : 3.7);
    }
    if (sub) {
      tl.to(sub, { clipPath: 'inset(0 0 0% 0)', opacity: 1, y: 0, duration: 0.9, ease: EASE.settle }, logo ? 4.45 : 3.9);
    }

    return tl;
  }

  function construir(seccion, cfg) {
    var bloque = seccion.querySelector(cfg.wrap);
    var interior = seccion.querySelector(cfg.inner);
    var titulo = seccion.querySelector(cfg.titulo);
    var eyebrow = seccion.querySelector('.eyebrow');
    var sub = seccion.querySelector(cfg.sub);
    /* En la portada el fondo pasa a ser un video; en los banners sigue siendo
       una foto. La secuencia los trata igual: solo escala el elemento. */
    var foto = seccion.querySelector('img, video');
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

    /* ------------------------------------------------------- que secuencia */

    if (cfg.obertura) {
      /* Las portadas del home se presentan solas: el titulo aparece grande y
         centrado, sostiene, y recien despues viaja a su sitio. No es una
         animacion ligada al scroll sino una entrada con su propio tiempo.

         El disparador la lanza cuando la seccion toma la pantalla, y la vuelve
         a lanzar si el usuario sube y baja de nuevo: la obertura es el momento
         en que la obra se presenta, y tiene que volver a ocurrir cada vez que
         se llega a ella. Al salir por arriba se rebobina, para que la proxima
         vez arranque desde cero y no desde el final. */
      var entrada = obertura(seccion, titulo, lineas, sub, eyebrow, {
        escala: cfg.escalaObertura,
        delay: 0.1,
        logo: cfg.logo ? seccion.querySelector(cfg.logo) : null
      });

      /* Callbacks explicitos en vez de toggleActions. Con toggleActions la
         portada del home no arrancaba nunca: nace con su punto de disparo ya
         atras —esta arriba de todo— asi que ScrollTrigger no registra ninguna
         entrada que disparar. Con onEnter/onEnterBack y un arranque manual
         para lo que ya se ve, los dos casos quedan cubiertos. */
      /* La obertura se reproduce una vez por visita a la seccion. La bandera
         es imprescindible: ScrollTrigger vuelve a evaluar sus disparadores en
         cada refresh, y el guion pide un refresh por cada imagen diferida que
         termina de cargar. Sin la bandera, cada una de esas decenas de cargas
         reiniciaba la obertura, y el titulo se quedaba emergiendo en un bucle
         sin llegar nunca a viajar a su sitio.

         Se rearma cuando el usuario abandona la seccion de verdad, y eso pasa
         en las dos direcciones: por arriba al volver hacia el principio, y por
         abajo al seguir de largo. El hero solo puede salir por arriba, pero un
         banner en el medio de la pagina se deja atras bajando, y ahi el que
         dispara es onLeave. Sin rearmar tambien en ese caso, la obertura de un
         banner se veia una sola vez por carga: se bajaba, se seguia de largo y
         al volver a subir ya no arrancaba nunca mas. */
      var pendiente = true;

      var lanzar = function () {
        if (!pendiente) return;
        pendiente = false;
        entrada.restart(true);
      };

      /* Rearmar no es lo mismo que rebobinar. Al salir por abajo la obertura
         queda como estaba —nadie la ve— y se rebobina recien al volver a
         entrar. Al salir por arriba se rebobina en el momento, porque la
         seccion sigue camino a la vista mientras se sube. */
      var rearmar = function () { pendiente = true; };

      ScrollTrigger.create({
        trigger: seccion,
        start: 'top 60%',
        end: 'bottom top',
        onEnter: lanzar,
        onEnterBack: lanzar,
        onLeave: rearmar,
        onLeaveBack: function () {
          rearmar();
          entrada.pause(0);
        }
      });

      /* Si la seccion ya esta a la vista cuando se arma el guion —siempre es
         el caso del hero— la obertura arranca sola. */
      if (seccion.getBoundingClientRect().top < window.innerHeight * 0.6) {
        lanzar();
      } else {
        entrada.pause(0);
      }

      if (foto) {
        gsap.set(foto, { scale: 1.18, transformOrigin: 'center center' });
        tl.to(foto, { scale: 1, yPercent: 6, duration: en(0.92), ease: EASE.linear }, 0);
      }

    } else {
      /* Los banners de proyecto si van por scroll, con las cuatro fases. */

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
    }

    /* -------------------------------------------------------------- salida */

    /* Cuando el escenario se despega, el bloque se va achicando hacia abajo a
       la izquierda. Es el mismo gesto que usan los banners de proyecto mas
       abajo, asi que el recorrido de la home se lee como una sola pieza. */
    /* La salida escala el bloque entero, no el titulo: en la portada el titulo
       lleva su propio transform, puesto por la obertura, y pisarlo lo sacaria
       de lugar. */
    gsap.set(bloque, { transformOrigin: 'left bottom' });
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

  window.HMA.hero = { construir: construir, obertura: obertura };
})(window, document);
