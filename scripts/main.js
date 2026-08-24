/* ---------- IDIOMA ----------
   El sitio se sirve en dos idiomas desde archivos distintos, pero el
   JavaScript es uno solo. Los textos que arma el script en caliente —estados
   de formulario, resultados de busqueda, rotulos de botones— no pasan por el
   generador del espejo, asi que salen de aca, elegidos por el lang del
   documento. Si se agrega un texto nuevo al script, va con T(). */
const HMA_EN = document.documentElement.lang === 'en';
const T = (es, en) => (HMA_EN ? en : es);

try {
  /* Algunos navegadores móviles dejan el video pausado al restaurar la pestaña
     aunque cumpla las reglas de autoplay. Reafirmar sus propiedades y volver
     a pedir play cubre ese caso sin interferir con reduced-motion. */
  const heroVideo = document.querySelector('.hero-video[autoplay]');
  if (heroVideo) {
    const startHeroVideo = () => {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      heroVideo.muted = true;
      heroVideo.defaultMuted = true;
      heroVideo.playsInline = true;
      const playback = heroVideo.play();
      if (playback && typeof playback.catch === 'function') playback.catch(() => {});
    };

    if (heroVideo.readyState >= 2) startHeroVideo();
    else heroVideo.addEventListener('canplay', startHeroVideo, { once: true });

    window.addEventListener('pageshow', startHeroVideo);
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) startHeroVideo();
    });
  }
} catch (e) { console.error('hero-video-autoplay', e); }

try {
  /* ---------- TODOS LOS TEXTOS DEL HOME SE ACHICAN HACIA ABAJO-IZQUIERDA AL
     SCROLLEAR (referencia mvrdv.com: transform-origin left bottom, ligado al
     scroll en vivo dentro del rango de CADA seccion, no a una sola aparicion).
     Aplica al hero y a los 6 project-banner. ---------- */
  /* Este bloque es el respaldo para cuando GSAP no esta: si cargo, el mismo
     efecto lo hace scroll.js con ScrollTrigger y scrub, que es mas preciso y
     no compite con este rAF. */
  if (!document.documentElement.classList.contains('gsap-active')) {
    const shrinkTargets = [];
    const heroSection = document.querySelector('.hero-home--photo');
    const heroWrap = document.querySelector('.hero-content-wrap');
    if (heroSection && heroWrap) {
      shrinkTargets.push({ section: heroSection, wrap: heroWrap, varName: '--hero-scale' });
    }

    document.querySelectorAll('.project-banner:not(.project-banner--split)').forEach(banner => {
      const content = banner.querySelector('.project-banner__content');
      if (content) shrinkTargets.push({ section: banner, wrap: content, varName: '--pb-scale' });
    });

    if (shrinkTargets.length) {
      const MIN_SCALE = 0.55;
      const updateShrink = () => {
        shrinkTargets.forEach(({ section, wrap, varName }) => {
          const top = section.offsetTop;
          const height = section.offsetHeight || 1;
          const progress = Math.min(Math.max((window.scrollY - top) / height, 0), 1);
          const scale = 1 - progress * (1 - MIN_SCALE);
          wrap.style.setProperty(varName, scale.toFixed(3));
        });
      };
      window.addEventListener('scroll', () => requestAnimationFrame(updateShrink), { passive: true });
      window.addEventListener('resize', updateShrink);
      updateShrink();
    }
  }
} catch (e) { console.error('shrink-on-scroll', e); }

try {
  /* ---------- HEADER TRANSPARENTE SOBRE EL HERO (referencia mvrdv.com) ---------- */
  const overlayHeader = document.querySelector('header.site-header.is-overlay');
  const heroPhoto = document.querySelector('.hero-home--photo');
  if (overlayHeader && heroPhoto) {
    const headerIo = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        overlayHeader.classList.toggle('scrolled', !entry.isIntersecting);
      });
    }, { rootMargin: `-${overlayHeader.offsetHeight}px 0px 0px 0px`, threshold: 0 });
    headerIo.observe(heroPhoto);
  }
} catch (e) { console.error('overlay-header', e); }

try {
  /* ---------- PUNTOS DE NAVEGACION A LA DERECHA (referencia mvrdv.com) ---------- */
  const dotsNav = document.getElementById('scrollDots');
  if (dotsNav) {
    const dots = Array.from(dotsNav.querySelectorAll('button'));
    const targets = dots.map(btn => ({ btn, el: document.getElementById(btn.dataset.target) }))
      .filter(item => item.el);

    const setActive = (btn) => {
      dots.forEach(d => d.classList.toggle('active', d === btn));
    };

    const updateActiveDot = () => {
      if (!targets.length) return;
      const centerY = window.innerHeight / 2;
      const nearBottom = window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4;

      let active = nearBottom ? targets[targets.length - 1] : targets[0];
      let best = Infinity;
      targets.forEach(item => {
        const r = item.el.getBoundingClientRect();
        const sectionCenter = r.top + r.height / 2;
        const crossesCenter = r.top <= centerY && r.bottom >= centerY;
        const distance = crossesCenter ? 0 : Math.abs(sectionCenter - centerY);
        if (distance < best) {
          best = distance;
          active = item;
        }
      });
      setActive(active.btn);
    };

    let raf = 0;
    const requestDotUpdate = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        updateActiveDot();
      });
    };

    dots.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = document.getElementById(btn.dataset.target);
        /* Con Lenis manejando el scroll, scrollIntoView pelea con su
           posicion interpolada: hay que pedirle el viaje a el. */
        if (!target) return;
        setActive(btn);
        const lenis = window.HMA && window.HMA.config && window.HMA.config.lenis;
        if (lenis) lenis.scrollTo(target, { duration: 1.2 });
        else target.scrollIntoView({ behavior: 'smooth' });
      });
    });

    updateActiveDot();
    window.addEventListener('scroll', requestDotUpdate, { passive: true });
    window.addEventListener('resize', requestDotUpdate);
    window.addEventListener('load', requestDotUpdate);

    /* Los puntos van en negro sobre fondo blanco y en blanco cuando quedan
       sobre una foto. rootMargin -50%/-50% deja una franja de altura cero
       justo en el centro vertical de la pantalla, que es donde estan los
       puntos: si ahi hay una foto, se activa .on-dark. */
    /* El pie tambien es fondo negro: si no entra en la cuenta, al llegar
       abajo los puntos y su etiqueta quedan negros sobre negro. */
    const darkSections = document.querySelectorAll('.hero-home--photo, .project-banner:not(.project-banner--split), .site-footer');
    if (darkSections.length) {
      const overDark = new Set();
      const darkIo = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) overDark.add(entry.target);
          else overDark.delete(entry.target);
        });
        dotsNav.classList.toggle('on-dark', overDark.size > 0);
      }, { rootMargin: '-50% 0px -50% 0px', threshold: 0 });
      darkSections.forEach(s => darkIo.observe(s));
    }
  }
} catch (e) { console.error('scroll-dots', e); }

try {
  /* ---------- MENU (toggle unico, referencia mvrdv.com) ---------- */
  const menuBtn = document.getElementById('menuBtn');
  const siteMenu = document.getElementById('site-menu');
  if (menuBtn && siteMenu) {
    const closeMenu = () => {
      siteMenu.classList.remove('open');
      menuBtn.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    };
    const openMenu = () => {
      siteMenu.classList.add('open');
      menuBtn.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
    };
    menuBtn.addEventListener('click', () => {
      if (siteMenu.classList.contains('open')) closeMenu(); else openMenu();
    });
    siteMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
    const closeBtn = document.getElementById('siteMenuClose');
    if (closeBtn) closeBtn.addEventListener('click', closeMenu);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && siteMenu.classList.contains('open')) closeMenu();
    });
  }
} catch (e) { console.error('nav', e); }

try {
  /* ---------- REVEAL ON SCROLL ---------- */
  /* Idem: si GSAP cargo, el reveal lo arma scroll.js con su propia timeline. */
  const revealEls = document.documentElement.classList.contains('gsap-active')
    ? [] : document.querySelectorAll('.reveal');
  revealEls.forEach((el, i) => { el.style.transitionDelay = (Math.min(i % 6, 5) * 60) + 'ms'; });
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('in'); io.unobserve(entry.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  revealEls.forEach(el => io.observe(el));
} catch (e) { console.error('reveal', e); }

try {
  /* ---------- COUNT-UP STATS (tiles + numeros dentro de frases) ---------- */
  document.querySelectorAll('[data-founded-year]').forEach(el => {
    el.dataset.count = Math.max(0, new Date().getFullYear() - parseInt(el.dataset.foundedYear, 10));
  });
  document.querySelectorAll('[data-countries]').forEach(el => {
    const countries = el.dataset.countries.split('|').filter(Boolean);
    el.dataset.count = new Set(countries).size;
  });
  const statEls = document.querySelectorAll('[data-count]');
  const statIo = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseInt(el.dataset.count, 10);
        const suffix = el.dataset.suffix || '';
        const duration = 1200;
        const start = performance.now();
        function tick(now) {
          const progress = Math.min((now - start) / duration, 1);
          const eased = 1 - Math.pow(1 - progress, 3);
          el.textContent = Math.round(eased * target) + suffix;
          if (progress < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
        statIo.unobserve(el);
      }
    });
  }, { threshold: 0.5 });
  statEls.forEach(el => statIo.observe(el));
} catch (e) { console.error('stats', e); }

try {
  /* ---------- PROJECT FILTER (grilla y lista) ----------
     Acotado a #filters: los botones de año de /prensa/ y /premios/ usan la
     misma clase .filter-btn, y sin acotar este bloque les sacaba el estado
     activo al filtrar por categoria. */
  const filterBtns = document.querySelectorAll('#filters .filter-btn');
  const estadoBtns = document.querySelectorAll('#estadoToggle button');
  if (filterBtns.length) {
    /* Dos filtros que se combinan, no uno que pisa al otro: el estudio
       distingue "obras" —construidas— de "proyectos" —concursos y obra en
       curso—, y eso es independiente del programa. Elegir Gastronómico y
       Obras tiene que dejar las gastronómicas construidas, no una u otra
       cosa. Por eso se aplican juntos en una sola pasada. */
    let cat = 'all';
    let estado = 'all';
    let texto = '';

    /* Sin tildes y en minusculas, para que "hoteleria" encuentre "Hotelería"
       y "uala" encuentre "Ualá". */
    const plano = t => (t || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');

    /* Se busca sobre todo lo que la tarjeta ya muestra: nombre, tipologia,
       ciudad, superficie, año y el rotulo de categoria. Se calcula una sola
       vez por tarjeta y queda guardado. */
    const textoDe = c => {
      if (!c.dataset.buscable) c.dataset.buscable = plano(c.textContent);
      return c.dataset.buscable;
    };

    const aplicar = () => {
      let visibles = 0;
      document.querySelectorAll('[data-cat]').forEach(c => {
        const categorias = (c.dataset.cats || c.dataset.cat || '').split(/\s+/);
        const fueraDeCat = cat !== 'all' && !categorias.includes(cat);
        const fueraDeEstado = estado !== 'all' && c.dataset.estado !== estado;
        const fueraDelTexto = texto !== '' && !textoDe(c).includes(texto);
        const fuera = fueraDeCat || fueraDeEstado || fueraDelTexto;
        c.classList.toggle('hidden', fuera);
        if (!fuera) visibles++;
      });
      const aviso = document.getElementById('sinResultados');
      /* La grilla y la lista tienen cada una su copia de las obras, asi que
         visibles viene contado dos veces cuando las dos existen. */
      if (aviso) aviso.hidden = visibles > 0;
    };

    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        cat = btn.dataset.filter;
        aplicar();
      });
    });

    estadoBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        estadoBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        estado = btn.dataset.estadoFiltro;
        aplicar();
      });
    });

    /* ---------- la lupa ---------- */
    const buscador = document.getElementById('buscadorObras');
    const campo = document.getElementById('buscadorObrasCampo');
    if (buscador && campo) {
      const lupa = buscador.querySelector('.buscador-obras__lupa');
      const abrir = () => {
        buscador.classList.add('is-open');
        lupa.setAttribute('aria-expanded', 'true');
        campo.focus();
      };
      const cerrar = () => {
        buscador.classList.remove('is-open');
        lupa.setAttribute('aria-expanded', 'false');
        if (campo.value) { campo.value = ''; texto = ''; aplicar(); }
      };
      lupa.addEventListener('click', () => {
        if (buscador.classList.contains('is-open')) cerrar(); else abrir();
      });
      campo.addEventListener('input', () => {
        texto = plano(campo.value.trim());
        aplicar();
      });
      campo.addEventListener('keydown', e => {
        if (e.key === 'Escape') { cerrar(); lupa.focus(); }
      });
      /* Al salir del campo sin nada escrito se cierra sola, para que la barra
         vuelva a su ancho. Con texto escrito queda abierta: si no, el usuario
         perderia el filtro al hacer clic en una tarjeta. */
      campo.addEventListener('blur', () => {
        if (!campo.value) cerrar();
      });
    }

    const params = new URLSearchParams(window.location.search);
    const catParam = params.get('cat');
    if (catParam) {
      const btn = document.querySelector(`#filters .filter-btn[data-filter="${CSS.escape(catParam)}"]`);
      if (btn) btn.click();
    }
    const estadoParam = params.get('estado');
    if (estadoParam) {
      const btn = document.querySelector(`#estadoToggle button[data-estado-filtro="${CSS.escape(estadoParam)}"]`);
      if (btn) btn.click();
    }
    /* ?q= es el mismo filtro, no uno aparte: antes tapaba tarjetas por su
       cuenta y el primer clic en cualquier boton lo borraba. */
    const q = (params.get('q') || '').trim();
    if (q) {
      texto = plano(q);
      if (campo) {
        campo.value = q;
        buscador.classList.add('is-open');
        buscador.querySelector('.buscador-obras__lupa')
          .setAttribute('aria-expanded', 'true');
      }
      aplicar();
    }
  }
} catch (e) { console.error('filter', e); }

try {
  /* ---------- VIEW TOGGLE (grilla / lista) ---------- */
  const viewBtns = document.querySelectorAll('.view-toggle button');
  const grid = document.querySelector('.project-grid');
  const list = document.querySelector('.project-list');
  if (viewBtns.length && grid && list) {
    viewBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        viewBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const view = btn.dataset.view;
        grid.classList.toggle('active', view === 'grid');
        list.classList.toggle('active', view === 'list');
      });
    });
  }
} catch (e) { console.error('view-toggle', e); }

try {
  /* ---------- PAGINA ACTIVA EN EL MENU ---------- */
  const navLinks = document.querySelectorAll('.site-menu__primary a[href]');
  const path = window.location.pathname.replace(/\/index\.html$/, '/');
  navLinks.forEach(a => {
    const href = a.getAttribute('href');
    if (href === path || (href !== '/' && path.startsWith(href))) {
      a.setAttribute('aria-current', 'page');
    }
  });
} catch (e) { console.error('active-page', e); }

try {
  /* ---------- FORMULARIO DE CONTACTO ---------- */
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    const cfSubmit = document.getElementById('cfSubmit');
    const cfStatus = document.getElementById('cfStatus');
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      cfStatus.textContent = ''; cfStatus.className = 'form-status';
      const data = {
        name: document.getElementById('cf-name').value.trim(),
        email: document.getElementById('cf-email').value.trim(),
        message: document.getElementById('cf-message').value.trim(),
        company: document.getElementById('cf-company').value,
      };
      if (!data.name || !data.email || !data.message) {
        cfStatus.textContent = T('Completá nombre, email y mensaje.', 'Please fill in your name, email and message.');
        cfStatus.classList.add('err');
        return;
      }
      cfSubmit.disabled = true; cfSubmit.textContent = T('Enviando…', 'Sending…');
      try {
        const res = await fetch('/api/contact', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data),
        });
        const result = await res.json().catch(() => ({}));
        if (res.ok && result.ok) {
          contactForm.reset();
          cfStatus.textContent = T('Gracias, te vamos a responder a la brevedad.', 'Thank you — we will get back to you shortly.');
          cfStatus.classList.add('ok');
        } else {
          cfStatus.textContent = result.error || T('No se pudo enviar. Escribinos a hma@estudiohma.com.', 'We could not send it. Write to us at hma@estudiohma.com.');
          cfStatus.classList.add('err');
        }
      } catch (err) {
        cfStatus.textContent = T('No se pudo enviar. Escribinos a hma@estudiohma.com.', 'We could not send it. Write to us at hma@estudiohma.com.');
        cfStatus.classList.add('err');
      } finally {
        cfSubmit.disabled = false; cfSubmit.textContent = T('Enviar mensaje', 'Send message');
      }
    });
  }
} catch (e) { console.error('contact-form', e); }

try {
  /* ---------- FILTRO POR AÑO (prensa y premios) ----------
     Cada barra filtra los bloques de su propia seccion, asi la misma logica
     sirve para /prensa/ y /premios/ sin duplicar codigo. */
  document.querySelectorAll('.press-filter-bar').forEach(bar => {
    const btns = Array.from(bar.querySelectorAll('button'));
    if (!btns.length) return;

    // .press-group primero: en /prensa/ conviven dos barras (Prensa y News)
    // dentro del mismo .container, y cada una debe filtrar solo lo suyo.
    const scope = bar.closest('.press-group') || bar.closest('.container') || document;
    const blocks = scope.querySelectorAll('.press-year-block, .award-year-block');
    if (!blocks.length) return;

    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        btns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const y = btn.dataset.year;
        blocks.forEach(block => {
          block.hidden = !(y === 'all' || block.dataset.year === y);
        });
      });
    });
  });
} catch (e) { console.error('year-filter', e); }

try {
  /* ---------- VIDEOS DE YOUTUBE SEPARADOS POR CATEGORIA (Entrevistas y Charlas) ---------- */
  const feedEntrevistas = document.getElementById('youtubeEntrevistas');
  const feedCharlas = document.getElementById('youtubeCharlas');

  if (feedEntrevistas || feedCharlas) {
    fetch('/api/youtube-latest')
      .then(r => (r.ok && (r.headers.get('content-type') || '').includes('json')) ? r.json() : null)
      .then(data => {
        if (!data) return;
        const videos = data.videos || [];
        if (!videos.length) return;

        const fmt = new Intl.DateTimeFormat(HMA_EN ? 'en-GB' : 'es-AR', { day: 'numeric', month: 'short', year: 'numeric' });

        const esc = (t) => String(t == null ? '' : t)
          .replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

        const urlSegura = (u, dominios) => {
          try {
            const x = new URL(u, location.origin);
            return x.protocol === 'https:' && dominios.some(d => x.hostname === d || x.hostname.endsWith('.' + d))
              ? x.href : null;
          } catch (e) { return null; }
        };


        const armarTarjetas = (lista) => lista.map(v => {
          const url = urlSegura(v.url, ['youtube.com', 'youtu.be']);
          if (!url || !/^[A-Za-z0-9_-]{11}$/.test(v.id || '')) return '';
          /* La facultad y varias redes corporativas bloquean i.ytimg.com. La
             imagen pasa por el mismo dominio del sitio para que no quede un
             rectangulo vacio aunque YouTube este filtrado en esa red. */
          const img = '/api/youtube-thumbnail?id=' + encodeURIComponent(v.id);
          const titulo = esc(v.title);
          const fecha = v.published ? esc(fmt.format(new Date(v.published))) : '';
          return `
          <a class="press-card" href="${esc(url)}" target="_blank" rel="noopener">
            <div class="press-img"><img src="${esc(img)}" alt="${titulo}" loading="lazy" decoding="async"></div>
            <div class="press-body">
              <div class="press-outlet">YouTube${fecha ? ' — ' + fecha : ''}</div>
              <div class="press-title">${titulo}</div>
            </div>
          </a>`;
        }).filter(Boolean).join('');

        /* Todos juntos y ordenados por fecha: la separacion entre entrevistas y
           charlas se hacia adivinando por el titulo, y ahora la decision de que
           video entra la toma el estudio agregandolo a una playlist.

           Si la lista viene vacia —sin clave de API, o las playlists caidas— la
           seccion se queda con las tarjetas que ya trae el HTML, que es mejor
           que dejarla en blanco. */
        const tarjetas = armarTarjetas(videos);
        if (!tarjetas) return;
        if (feedEntrevistas) feedEntrevistas.innerHTML = tarjetas;
        if (feedCharlas) feedCharlas.innerHTML = tarjetas;
      })
      .catch(e => console.error('youtube-feed-categories', e));
  }
} catch (e) { console.error('youtube-feed-init', e); }

try {
  /* ---------- PANEL DE CONTACTO FLOTANTE ---------- */
  const fab = document.getElementById('contactFab');
  const pop = document.getElementById('contactPop');
  if (fab && pop) {
    const close = () => {
      pop.classList.remove('open');
      fab.setAttribute('aria-expanded', 'false');
      fab.setAttribute('aria-label', 'Abrir opciones de contacto');

      // Al cerrar vuelve a la lista, para no reabrir con el formulario a medio
      // llenar de la vez anterior.
      const list = document.getElementById('contactPopList');
      const form = document.getElementById('waForm');
      if (list && form) {
        form.hidden = true;
        list.hidden = false;
        const st = document.getElementById('waStatus');
        if (st) { st.textContent = ''; st.className = 'form-status'; }
      }
    };
    fab.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = pop.classList.toggle('open');
      fab.setAttribute('aria-expanded', String(isOpen));
      fab.setAttribute('aria-label', isOpen ? 'Cerrar opciones de contacto' : 'Abrir opciones de contacto');
    });
    document.addEventListener('click', (e) => {
      if (pop.classList.contains('open') && !pop.contains(e.target)) close();
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && pop.classList.contains('open')) close();
    });
  }
} catch (e) { console.error('contact-fab', e); }

try {
  /* ---------- BUSCADOR EN VIVO (/buscar/) ----------
     Filtra sobre window.HMA_SEARCH_INDEX (scripts/search-index.js) a medida
     que se escribe, sin recargar la pagina ni pegarle a ningun servidor. */
  const spInput = document.getElementById('searchPageInput');
  const spResults = document.getElementById('searchResults');
  const spCount = document.getElementById('searchCount');
  const spForm = document.getElementById('searchPageForm');

  if (spInput && spResults && spCount) {
    const INDEX = window.HMA_SEARCH_INDEX || [];

    // Sin acentos y en minusculas, para que "uala" encuentre "Ualá".
    const norm = (s) => (s || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');

    const escapeHtml = (s) => (s || '').replace(/[&<>"]/g, c => (
      { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]
    ));

    // Resalta el tramo que coincide, respetando el texto original con acentos.
    function highlight(text, q) {
      const safe = escapeHtml(text);
      if (!q) return safe;
      const i = norm(safe).indexOf(norm(q));
      if (i === -1) return safe;
      return safe.slice(0, i) + '<mark>' + safe.slice(i, i + q.length) + '</mark>' + safe.slice(i + q.length);
    }

    function render(q) {
      const nq = norm(q).trim();

      if (!nq) {
        spResults.innerHTML = '';
        spCount.textContent = '';
        return;
      }

      const hits = INDEX.filter(item =>
        norm(item.titulo).includes(nq) ||
        norm(item.sub).includes(nq) ||
        norm(item.desc).includes(nq) ||
        norm(item.tipo).includes(nq)
      );

      spCount.innerHTML = hits.length === 1
        ? T('1 resultado para <b>', '1 result for <b>') + escapeHtml(q) + '</b>'
        : hits.length + T(' resultados para <b>', ' results for <b>') + escapeHtml(q) + '</b>';

      if (!hits.length) {
        spResults.innerHTML = '<p class="search-empty">' + T('No encontramos nada con ese término. Probá con el nombre de un proyecto, una categoría o un medio.', 'We found nothing for that term. Try the name of a project, a category or a publication.') + '</p>';
        return;
      }

      spResults.innerHTML = hits.map(item => {
        const thumb = item.img
          ? '<div class="search-result__thumb"><img src="' + item.img + '" alt="" loading="lazy" decoding="async"></div>'
          : '<div class="search-result__thumb"></div>';
        return '<a class="search-result" href="' + item.url + '">' +
          thumb +
          '<div>' +
          '<div class="search-result__tipo">' + escapeHtml(item.tipo) + (item.sub ? ' · ' + highlight(item.sub, q) : '') + '</div>' +
          '<div class="search-result__title">' + highlight(item.titulo, q) + '</div>' +
          (item.desc ? '<div class="search-result__desc">' + highlight(item.desc, q) + '</div>' : '') +
          '</div>' +
          '</a>';
      }).join('');
    }

    spInput.addEventListener('input', () => render(spInput.value));
    if (spForm) spForm.addEventListener('submit', (e) => { e.preventDefault(); render(spInput.value); });

    // Si se llega con ?q= (por ejemplo desde la lupa del menu), busca solo.
    const initial = new URLSearchParams(window.location.search).get('q');
    if (initial) { spInput.value = initial; render(initial); }
  }
} catch (e) { console.error('search-page', e); }

/* El estudio no tiene WhatsApp: usan solo una linea telefonica. Hasta el
   12/08/2026 el popup de contacto ofrecia "WhatsApp - Chatear ahora" y un
   formulario que prometia "seguimos la charla por WhatsApp", que era una
   promesa que el sitio no podia cumplir.

   Se saco el boton y el formulario de todas las paginas. El endpoint
   /api/lead.js queda en pie y sin usar: capturaba nombre y telefono y se los
   mandaba por mail al estudio, asi que sirve tal cual si algun dia quieren un
   "dejanos tu telefono y te llamamos". Borrarlo seria tirar algo que funciona
   y habria que rehacerlo igual. */

try {
  /* ---------- PRENSA + NEWS: solapas y años combinados ----------
     Una sola lista cronologica (mas nuevo primero). Las solapas filtran por
     grupo y los botones por año; ambos filtros se aplican juntos. */
  const feed = document.getElementById('pressFeed');
  const tabs = document.querySelectorAll('#pressTabs .press-tab');
  const yearBtns = document.querySelectorAll('#pressYears .filter-btn');
  const count = document.getElementById('pressCount');
  const loadMore = document.getElementById('pressLoadMore');

  /* Sin tabs tambien tiene que andar. Desde que las publicaciones pasaron a
     tarjetas -Word del 21/08/2026- la lista quedo con clases y conferencias
     solas y las solapas Todos/Prensa/News dejaron de tener sentido. Cuando se
     sacaron, este bloque pedia tabs.length y se apagaba entero: la lista se
     quedaba sin filtro por año, sin buscador, sin contador y sin "Seguir
     viendo". */
  if (feed && yearBtns.length) {
    const rows = Array.from(feed.querySelectorAll('.press-row'));
    let grupo = 'all';
    let anio = 'all';
    let texto = '';
    let limite = loadMore ? 12 : Number.POSITIVE_INFINITY;

    const plano = t => (t || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');

    /* Cada fila trae el titular, la obra, el medio y el pais, asi que buscar
       sobre su texto alcanza para encontrar por cualquiera de los cuatro. */
    const textoDe = r => {
      if (!r.dataset.buscable) r.dataset.buscable = plano(r.textContent);
      return r.dataset.buscable;
    };

    function aplicar() {
      let coincidencias = 0;
      rows.forEach(r => {
        const ok = (grupo === 'all' || r.dataset.group === grupo) &&
          (anio === 'all' || r.dataset.year === anio) &&
          (texto === '' || textoDe(r).includes(texto));
        if (ok) coincidencias++;
        r.hidden = !ok || coincidencias > limite;
      });

      // los años sin resultados dentro del grupo elegido se desactivan
      yearBtns.forEach(b => {
        const y = b.dataset.year;
        if (y === 'all') return;
        const hay = rows.some(r => r.dataset.year === y && (grupo === 'all' || r.dataset.group === grupo));
        b.disabled = !hay;
      });

      if (count) {
        const ingles = document.documentElement.lang === 'en';
        /* Sin solapas la lista es una sola cosa -clases y conferencias-, asi
           que "entradas", que servia cuando convivia con las publicaciones,
           pasa a ser "novedades". */
        const todo = tabs.length ? 'all' : 'news';
        const cual = grupo === 'all' ? todo : grupo;
        const que = ingles
          ? (cual === 'news' ? 'news items' : (cual === 'prensa' ? 'publications' : 'entries'))
          : (cual === 'news' ? 'novedades' : (cual === 'prensa' ? 'publicaciones' : 'entradas'));
        const singular = ingles
          ? (grupo === 'news' ? 'news item' : (grupo === 'prensa' ? 'publication' : 'entry'))
          : que.replace(/s$/, '');
        count.textContent = coincidencias === 1 ? `1 ${singular}` : `${coincidencias} ${que}`;
      }
      if (loadMore) loadMore.hidden = coincidencias <= limite;
    }

    const buscador = document.getElementById('buscadorPrensa');
    const campo = document.getElementById('buscadorPrensaCampo');
    if (buscador && campo) {
      const lupa = buscador.querySelector('.buscador-obras__lupa');
      const abrir = () => {
        buscador.classList.add('is-open');
        lupa.setAttribute('aria-expanded', 'true');
        campo.focus();
      };
      const cerrar = () => {
        buscador.classList.remove('is-open');
        lupa.setAttribute('aria-expanded', 'false');
        if (campo.value) { campo.value = ''; texto = ''; limite = 12; aplicar(); }
      };
      lupa.addEventListener('click', () => {
        if (buscador.classList.contains('is-open')) cerrar(); else abrir();
      });
      campo.addEventListener('input', () => {
        texto = plano(campo.value.trim());
        /* Buscando se muestran todas las coincidencias, sin el tope de doce:
           el boton de "ver mas" tiene sentido para recorrer el archivo entero,
           no para una busqueda que ya devuelve poco. */
        limite = texto ? Number.POSITIVE_INFINITY : 12;
        aplicar();
      });
      campo.addEventListener('keydown', e => {
        if (e.key === 'Escape') { cerrar(); lupa.focus(); }
      });
      campo.addEventListener('blur', () => {
        if (!campo.value) cerrar();
      });
    }

    tabs.forEach(tab => tab.addEventListener('click', () => {
      tabs.forEach(x => x.classList.remove('active'));
      tab.classList.add('active');
      grupo = tab.dataset.group;
      limite = 12;
      // si el año elegido no existe en el grupo nuevo, se vuelve a todos
      const sigue = rows.some(r => r.dataset.year === anio && (grupo === 'all' || r.dataset.group === grupo));
      if (anio !== 'all' && !sigue) {
        anio = 'all';
        yearBtns.forEach(b => b.classList.toggle('active', b.dataset.year === 'all'));
      }
      aplicar();
    }));

    yearBtns.forEach(btn => btn.addEventListener('click', () => {
      if (btn.disabled) return;
      yearBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      anio = btn.dataset.year;
      limite = 12;
      aplicar();
    }));

    if (loadMore) loadMore.addEventListener('click', () => {
      limite += 12;
      aplicar();
    });

    aplicar();
  }
} catch (e) { console.error('press-filters', e); }

try {
  /* Las tapas de Prensa usan el mismo criterio temporal que el archivo
     completo. El filtro vive aca porque estas nueve tarjetas tambien se
     regeneran desde docs/prensa_datos.json en cada publicacion. */
  const visualYears = document.querySelectorAll('#prensaVisualYears .filter-btn');
  const visualFeed = document.getElementById('prensaFeed');
  if (visualYears.length && visualFeed) {
    const cards = Array.from(visualFeed.querySelectorAll('.press-card[data-year]'));
    const more = document.getElementById('prensaVisualMas');
    const previous = document.getElementById('prensaVisualAnterior');
    const status = document.getElementById('prensaVisualPagina');
    const POR_PAGINA = 6;
    let pagina = 0;
    let anioVisual = 'all';
    let busqueda = '';

    const plano = t => (t || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');

    /* La tarjeta trae el medio, el pais, el titulo, la obra y el año, asi que
       buscar sobre su texto encuentra por cualquiera de los cinco. */
    const textoDe = c => {
      if (!c.dataset.buscable) c.dataset.buscable = plano(c.textContent);
      return c.dataset.buscable;
    };

    /* La pagina reemplaza seis tarjetas por las seis siguientes. No acumula
       filas: aun con doscientas publicaciones, Prensa conserva siempre la
       misma altura y cada filtro arranca en su primera pagina. */
    const aplicarVisual = () => {
      const coincidencias = cards.filter(card =>
        (anioVisual === 'all' || card.dataset.year === anioVisual) &&
        (busqueda === '' || textoDe(card).includes(busqueda)));
      const paginas = Math.max(1, Math.ceil(coincidencias.length / POR_PAGINA));
      pagina = Math.min(pagina, paginas - 1);
      const desde = pagina * POR_PAGINA;
      const visibles = new Set(coincidencias.slice(desde, desde + POR_PAGINA));
      cards.forEach(card => { card.hidden = !visibles.has(card); });

      // Un año sin ninguna publicacion no se puede elegir.
      visualYears.forEach(b => {
        const y = b.dataset.year;
        if (y === 'all') return;
        b.disabled = !cards.some(c => c.dataset.year === y);
      });

      if (previous) previous.disabled = pagina === 0;
      if (more) more.disabled = pagina >= paginas - 1 || coincidencias.length === 0;
      if (status) {
        const ingles = document.documentElement.lang === 'en';
        status.textContent = ingles
          ? `Page ${pagina + 1} of ${paginas}`
          : `Pagina ${pagina + 1} de ${paginas}`;
      }
      if (window.ScrollTrigger) requestAnimationFrame(() => ScrollTrigger.refresh());
    };

    visualYears.forEach(btn => btn.addEventListener('click', () => {
      if (btn.disabled) return;
      visualYears.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      anioVisual = btn.dataset.year;
      pagina = 0;
      aplicarVisual();
    }));

    const buscador = document.getElementById('buscadorTarjetas');
    const campo = document.getElementById('buscadorTarjetasCampo');
    if (buscador && campo) {
      const lupa = buscador.querySelector('.buscador-obras__lupa');
      const abrir = () => {
        buscador.classList.add('is-open');
        lupa.setAttribute('aria-expanded', 'true');
        campo.focus();
      };
      const cerrar = () => {
        buscador.classList.remove('is-open');
        lupa.setAttribute('aria-expanded', 'false');
        if (campo.value) {
          campo.value = '';
          busqueda = '';
          pagina = 0;
          aplicarVisual();
        }
      };
      lupa.addEventListener('click', () => {
        if (buscador.classList.contains('is-open')) cerrar(); else abrir();
      });
      campo.addEventListener('input', () => {
        busqueda = plano(campo.value.trim());
        pagina = 0;
        aplicarVisual();
      });
      campo.addEventListener('keydown', e => {
        if (e.key === 'Escape') { cerrar(); lupa.focus(); }
      });
      campo.addEventListener('blur', () => { if (!campo.value) cerrar(); });
    }

    if (previous) previous.addEventListener('click', () => {
      pagina = Math.max(0, pagina - 1);
      aplicarVisual();
    });
    if (more) more.addEventListener('click', () => {
      pagina++;
      aplicarVisual();
    });
    aplicarVisual();
  }
} catch (e) { console.error('press-visual-filters', e); }

try {
  /* ---------- MEMORIA DE OBRA CON FILAS EDITORIALES ----------
     La memoria real ya existe en cada ficha. Las filas que venian despues
     repetian textos institucionales, asi que usamos solamente sus fotos y
     armamos pares equilibrados de texto e imagen. La portada es siempre la
     primera foto porque el build la coloca al comienzo de project-gallery. */
  const memoria = document.querySelector('.project-memoria .memoria-cuerpo');
  const galeriaEditorial = document.querySelector('.project-gallery');

  let memoriaArmada = false;

  if (memoria && galeriaEditorial) {
    const parrafos = Array.from(memoria.children).filter(el => el.matches('p'));
    /* La memoria lleva como maximo cinco fotos, igual que las demas fichas:
       alcanza para cortar un texto largo sin duplicar dentro de la memoria
       toda la galeria que el visitante encuentra inmediatamente despues. */
    const fotosGaleria = Array.from(document.querySelectorAll(
      '#galeria .gallery-grid__item:not(.gallery-grid__item--plano)')).slice(0, 5);
    const fotos = fotosGaleria.length
      ? fotosGaleria
      : Array.from(galeriaEditorial.querySelectorAll('.project-row__photo'));

    /* Una memoria pegada de un Word en un solo bloque deja un unico <p>, y
       como el reparto de abajo es min(parrafos, fotos), la ficha sale con una
       sola fila -un ladrillo de texto al lado de una foto- y las demas fotos
       abajo, sueltas y sin texto. Es lo que le pasa a Bienal de Venecia: 1548
       caracteres en un parrafo contra tres fotos. Nadie lo avisa, porque el
       dato esta bien cargado; lo que falta son los saltos.

       Antes de repartir, entonces, se parten los parrafos mas largos por el
       final de oracion mas cercano a la mitad, hasta llegar a la cantidad de
       fotos. Solo se parte lo que tiene cuerpo para dar: un parrafo corto
       cortado al medio se lee peor que entero. Con estos dos topes, de las 61
       fichas publicadas esto solo toca las cuatro que tienen menos parrafos
       que fotos y texto de sobra -bienal-venecia, casa-olmo, nim-bar y
       people-; malita, con 468 y 325, queda como esta. */
    const LARGO_MINIMO = 500;
    const MITAD_MINIMA = 200;

    const partirEnDos = (parrafo) => {
      const texto = parrafo.textContent.trim();
      if (texto.length < LARGO_MINIMO) return null;
      const medio = texto.length / 2;
      const fin = /[.!?…]\s/g;
      let corte = -1;
      let m = fin.exec(texto);
      while (m) {
        const pos = m.index + m[0].length;
        if (corte < 0 || Math.abs(pos - medio) < Math.abs(corte - medio)) corte = pos;
        m = fin.exec(texto);
      }
      if (corte < MITAD_MINIMA || texto.length - corte < MITAD_MINIMA) return null;
      return [texto.slice(0, corte).trim(), texto.slice(corte).trim()]
        .map((t) => {
          const p = document.createElement('p');
          p.textContent = t;
          return p;
        });
    };

    while (parrafos.length < fotos.length) {
      let indice = -1;
      parrafos.forEach((p, i) => {
        if (indice < 0 || p.textContent.length > parrafos[indice].textContent.length) {
          indice = i;
        }
      });
      const mitades = indice < 0 ? null : partirEnDos(parrafos[indice]);
      if (!mitades) break;
      parrafos[indice].replaceWith(mitades[0], mitades[1]);
      parrafos.splice(indice, 1, mitades[0], mitades[1]);
    }

    const cantidad = Math.min(parrafos.length, fotos.length);

    if (cantidad) {
      const fragmento = document.createDocumentFragment();
      for (let i = 0; i < cantidad; i += 1) {
        const inicio = Math.floor((i * parrafos.length) / cantidad);
        const fin = Math.floor(((i + 1) * parrafos.length) / cantidad);
        const fila = document.createElement('div');
        fila.className = 'memoria-editorial-row' + (i % 2 ? ' memoria-editorial-row--reverse' : '');
        if (i >= 2) fila.classList.add('memoria-editorial-row--extra');

        const texto = document.createElement('div');
        texto.className = 'memoria-editorial-row__text';
        parrafos.slice(inicio, Math.max(inicio + 1, fin)).forEach(p => texto.appendChild(p));

        const foto = fotos[i].cloneNode(true);
        foto.className = 'memoria-editorial-row__photo';
        foto.removeAttribute('style');
        const imagen = foto.querySelector('img');
        if (imagen) {
          imagen.removeAttribute('style');
          imagen.loading = i === 0 ? 'eager' : 'lazy';
          if (i === 0) imagen.fetchPriority = 'high';
        }

        fila.append(texto, foto);
        fragmento.appendChild(fila);
      }
      memoria.replaceChildren(fragmento);
      memoria.classList.add('memoria-cuerpo--intercalada');
      memoria.classList.remove('reveal');
      memoria.removeAttribute('style');
      memoriaArmada = true;
    }
  }

  if (galeriaEditorial && memoriaArmada) {
    galeriaEditorial.hidden = true;
  } else if (galeriaEditorial) {
    /* Una obra cargada sin memoria conserva una presentacion util: portada y
       bajada. Se retiran las filas institucionales repetidas hasta que el
       estudio complete la memoria desde el panel. */
    const primeraFila = galeriaEditorial.querySelector('.project-row');
    if (primeraFila) {
      primeraFila.classList.add('project-row--cover-only');
      galeriaEditorial.replaceChildren(primeraFila);
    }
  }

  /* El cierre conserva el titulo y el acceso al indice general. Las tarjetas
     sugeridas se retiraron a pedido del estudio. */
  document.querySelectorAll('.related-projects').forEach(grid => grid.remove());
} catch (e) { console.error('memoria-intercalada', e); }

try {
  /* ---------- VER TODO: GALERIAS DE OBRA Y GRILLA DE VIDEOS ----------
     Las dos muestran unas pocas y guardan el resto detras de un boton. Al
     abrirlas hay que avisarle a ScrollTrigger: aparecen decenas de figuras y
     todo lo que viene despues se corre hacia abajo, asi que sus puntos de
     disparo quedan viejos.

     Los rotulos vienen del HTML (data-mas / data-menos) porque el boton dice
     "fotos" en una ficha y "videos" en prensa. Las galerias viejas solo traen
     data-total, asi que se les arma el rotulo como antes. */
  document.querySelectorAll('.gallery-more, .pub-more').forEach(btn => {
    const grid = btn.previousElementSibling;
    if (!grid) return;
    const esGaleria = grid.classList.contains('gallery-grid');
    if (!esGaleria && !grid.classList.contains('press-featured')
      && !grid.classList.contains('memoria-cuerpo')
      && !grid.classList.contains('pub-lista')) return;

    const rotuloMas = btn.dataset.mas ||
      T('Ver las ' + btn.dataset.total + ' fotos', 'See all ' + btn.dataset.total + ' photos');
    const rotuloMenos = btn.dataset.menos || T('Ver menos fotos', 'See fewer photos');

    btn.addEventListener('click', () => {
      const abierta = grid.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', abierta ? 'true' : 'false');
      btn.textContent = abierta ? rotuloMenos : rotuloMas;
      if (!abierta) grid.scrollIntoView({ block: 'start' });
      if (window.ScrollTrigger) requestAnimationFrame(() => ScrollTrigger.refresh());
    });
  });
} catch (e) { console.error('galeria', e); }

try {
  /* ---------- VISOR DE FOTOS ----------
     "Revisar todas las fotos del catálogo: En todos los proyectos/obras, al
     hacer clic debería poder abrirse la imagen en mayor tamaño/hacer zoom"
     (19/08/2026). El mismo pedido vuelve para la página de cada noticia:
     "que sean clickeables y poder verlas amplificadas".

     Se arma desde acá y no en el HTML para que valga en las 61 fichas sin
     tocar página por página, y para que una obra nueva lo tenga sin hacer
     nada. Las fotos siguen siendo <img> comunes: si este script no corre, la
     página se ve igual, sólo que sin ampliar. */
  const fotos = Array.from(document.querySelectorAll(
    '.gallery-grid__item img, .project-row__photo img, .memoria-editorial-row__photo img'));

  if (fotos.length) {
    const visor = document.createElement('div');
    visor.className = 'visor';
    visor.setAttribute('role', 'dialog');
    visor.setAttribute('aria-modal', 'true');
    visor.setAttribute('aria-label', T('Foto ampliada', 'Enlarged photo'));
    visor.hidden = true;
    visor.innerHTML =
      '<button class="visor__cerrar" type="button" aria-label="' +
      T('Cerrar', 'Close') + '">&times;</button>' +
      '<button class="visor__paso visor__paso--antes" type="button" aria-label="' +
      T('Foto anterior', 'Previous photo') + '">&#8249;</button>' +
      '<figure class="visor__marco"><img alt=""><figcaption class="visor__pie"></figcaption></figure>' +
      '<button class="visor__paso visor__paso--despues" type="button" aria-label="' +
      T('Foto siguiente', 'Next photo') + '">&#8250;</button>';
    document.body.appendChild(visor);

    const imagen = visor.querySelector('img');
    const pie = visor.querySelector('.visor__pie');
    const antes = visor.querySelector('.visor__paso--antes');
    const despues = visor.querySelector('.visor__paso--despues');
    let actual = 0;
    let devolverFoco = null;

    const mostrar = (i) => {
      actual = (i + fotos.length) % fotos.length;
      const foto = fotos[actual];
      imagen.src = foto.currentSrc || foto.src;
      imagen.alt = foto.alt || '';
      pie.textContent = fotos.length > 1
        ? (actual + 1) + ' / ' + fotos.length
        : '';
      // Con una sola foto los pasos no tienen a dónde ir.
      antes.hidden = despues.hidden = fotos.length < 2;
    };

    const abrir = (i, origen) => {
      devolverFoco = origen || null;
      mostrar(i);
      visor.hidden = false;
      document.documentElement.classList.add('visor-abierto');
      visor.querySelector('.visor__cerrar').focus();
    };

    const cerrar = () => {
      visor.hidden = true;
      document.documentElement.classList.remove('visor-abierto');
      // La imagen queda en memoria si no se limpia el src.
      imagen.removeAttribute('src');
      if (devolverFoco) devolverFoco.focus();
    };

    fotos.forEach((foto, i) => {
      foto.classList.add('foto-ampliable');
      const disparo = foto.closest('figure') || foto;
      // Las fotos de la memoria van dentro de un enlace en algunas fichas:
      // ahí manda el enlace y el visor no se mete.
      if (foto.closest('a')) return;
      disparo.setAttribute('tabindex', '0');
      disparo.setAttribute('role', 'button');
      disparo.setAttribute('aria-label', T('Ampliar foto', 'Enlarge photo'));
      disparo.addEventListener('click', () => abrir(i, disparo));
      disparo.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); abrir(i, disparo); }
      });
    });

    visor.querySelector('.visor__cerrar').addEventListener('click', cerrar);
    antes.addEventListener('click', () => mostrar(actual - 1));
    despues.addEventListener('click', () => mostrar(actual + 1));
    visor.addEventListener('click', (e) => { if (e.target === visor) cerrar(); });

    document.addEventListener('keydown', (e) => {
      if (visor.hidden) return;
      if (e.key === 'Escape') cerrar();
      else if (e.key === 'ArrowLeft') mostrar(actual - 1);
      else if (e.key === 'ArrowRight') mostrar(actual + 1);
    });
  }
} catch (e) { console.error('visor', e); }
