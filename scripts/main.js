/* ---------- IDIOMA ----------
   El sitio se sirve en dos idiomas desde archivos distintos, pero el
   JavaScript es uno solo. Los textos que arma el script en caliente —estados
   de formulario, resultados de busqueda, rotulos de botones— no pasan por el
   generador del espejo, asi que salen de aca, elegidos por el lang del
   documento. Si se agrega un texto nuevo al script, va con T(). */
const HMA_EN = document.documentElement.lang === 'en';
const T = (es, en) => (HMA_EN ? en : es);

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

    document.querySelectorAll('.project-banner').forEach(banner => {
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
    const sections = dots.map(d => document.getElementById(d.dataset.target)).filter(Boolean);

    dots.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = document.getElementById(btn.dataset.target);
        /* Con Lenis manejando el scroll, scrollIntoView pelea con su
           posicion interpolada: hay que pedirle el viaje a el. */
        if (!target) return;
        const lenis = window.HMA && window.HMA.config && window.HMA.config.lenis;
        if (lenis) lenis.scrollTo(target, { duration: 1.2 });
        else target.scrollIntoView({ behavior: 'smooth' });
      });
    });

    /* Que seccion esta activa se decide por cual cruza el centro de la
       pantalla, no por cuanta parte de ella se ve. Con threshold 0.5 el punto
       quedaba pegado: las secciones del home miden dos pantallas y media, asi
       que ninguna llega nunca a tener la mitad visible, y el indicador no se
       movia al volver a subir. La franja de altura cero en el centro —igual
       que la que decide el color de los puntos— resuelve las dos cosas. */
    const dotsIo = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const idx = sections.indexOf(entry.target);
        if (idx === -1) return;
        dots.forEach(d => d.classList.remove('active'));
        dots[idx].classList.add('active');
      });
    }, { rootMargin: '-50% 0px -50% 0px', threshold: 0 });
    sections.forEach(s => dotsIo.observe(s));

    /* Los puntos van en negro sobre fondo blanco y en blanco cuando quedan
       sobre una foto. rootMargin -50%/-50% deja una franja de altura cero
       justo en el centro vertical de la pantalla, que es donde estan los
       puntos: si ahi hay una foto, se activa .on-dark. */
    /* El pie tambien es fondo negro: si no entra en la cuenta, al llegar
       abajo los puntos y su etiqueta quedan negros sobre negro. */
    const darkSections = document.querySelectorAll('.hero-home--photo, .project-banner, .site-footer');
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
  if (filterBtns.length) {
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const f = btn.dataset.filter;
        document.querySelectorAll('[data-cat]').forEach(c => {
          c.classList.toggle('hidden', f !== 'all' && c.dataset.cat !== f);
        });
      });
    });
    const params = new URLSearchParams(window.location.search);
    const cat = params.get('cat');
    if (cat) {
      const btn = document.querySelector(`#filters .filter-btn[data-filter="${CSS.escape(cat)}"]`);
      if (btn) btn.click();
    }
    const q = (params.get('q') || '').trim().toLowerCase();
    if (q) {
      document.querySelectorAll('[data-cat]').forEach(c => {
        const name = (c.querySelector('.p-name, .plr-name')?.textContent || '').toLowerCase();
        if (!name.includes(q)) c.classList.add('hidden');
      });
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
  /* ---------- ULTIMOS VIDEOS DE YOUTUBE (home) ----------
     La seccion arranca oculta (atributo "hidden" en el HTML) y solo se
     muestra si el feed devuelve videos reales — evita mostrar un cartel
     vacio mientras no este configurada la YOUTUBE_API_KEY. */
  const updatesSection = document.getElementById('updatesSection');
  const feedEl = document.getElementById('youtubeFeed');
  /* Los videos ya vienen escritos en el HTML, asi que la seccion funciona sin
     la YOUTUBE_API_KEY. Si la key esta configurada, el feed la reemplaza por
     la lista en vivo del canal. */
  if (updatesSection && feedEl) {
    fetch('/api/youtube-latest')
      .then(r => (r.ok && (r.headers.get('content-type') || '').includes('json')) ? r.json() : null)
      .then(data => {
        if (!data) return;              // sin API key configurada: quedan los del HTML
        const videos = data.videos || [];
        if (!videos.length) return;

        const fmt = new Intl.DateTimeFormat('es-AR', { day: 'numeric', month: 'short', year: 'numeric' });
        feedEl.innerHTML = videos.map(v => `
          <a class="press-card" href="${v.url}" target="_blank" rel="noopener">
            <div class="press-img"><img src="${v.thumbnail}" alt="${v.title.replace(/"/g, '&quot;')}" loading="lazy" decoding="async"></div>
            <div class="press-body">
              <div class="press-outlet">YouTube — ${v.published ? fmt.format(new Date(v.published)) : ''}</div>
              <div class="press-title">${v.title}</div>
            </div>
          </a>
        `).join('');
        updatesSection.hidden = false;
      })
      .catch(e => console.error('youtube-feed', e));
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

try {
  /* ---------- WHATSAPP CON CAPTURA DE DATOS ----------
     Antes del salto a WhatsApp se piden nombre y telefono y se mandan a
     /api/lead, para que el estudio pueda contactar aunque la persona nunca
     llegue a escribir el mensaje.

     >>> UNICO LUGAR A EDITAR cuando este el numero de WhatsApp del estudio:
     solo digitos, con codigo de pais y sin espacios ni signos.
     Ejemplo: '5491122334455'. Vacio = todavia no configurado. */
  const WHATSAPP_NUMBER = '';

  const waStart = document.getElementById('waStart');
  const waForm = document.getElementById('waForm');
  const waList = document.getElementById('contactPopList');

  if (waStart && waForm && waList) {
    const waStatus = document.getElementById('waStatus');
    const waSubmit = document.getElementById('waSubmit');
    const nameEl = document.getElementById('wa-name');
    const phoneEl = document.getElementById('wa-phone');
    const consentEl = document.getElementById('wa-consent');
    const companyEl = document.getElementById('wa-company');

    waStart.addEventListener('click', () => {
      waList.hidden = true;
      waForm.hidden = false;
      nameEl.focus();
    });

    waForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      waStatus.textContent = '';
      waStatus.className = 'form-status';

      const name = nameEl.value.trim();
      const phone = phoneEl.value.trim();

      if (!name || phone.replace(/\D/g, '').length < 6) {
        waStatus.textContent = T('Completá tu nombre y un teléfono válido.', 'Please enter your name and a valid phone number.');
        waStatus.classList.add('err');
        return;
      }
      if (!consentEl.checked) {
        waStatus.textContent = T('Necesitamos tu confirmación para poder contactarte.', 'We need your consent in order to contact you.');
        waStatus.classList.add('err');
        return;
      }

      waSubmit.disabled = true;
      waSubmit.textContent = T('Abriendo…', 'Opening…');

      // El aviso al estudio no debe frenar a la persona: si falla, sigue igual.
      try {
        await fetch('/api/lead', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, phone, company: companyEl ? companyEl.value : '' }),
        });
      } catch (err) {
        console.error('lead', err);
      }

      if (WHATSAPP_NUMBER) {
        const texto = encodeURIComponent('Hola, soy ' + name + '. Quiero consultar por un proyecto.');
        window.open('https://wa.me/' + WHATSAPP_NUMBER + '?text=' + texto, '_blank', 'noopener');
        waStatus.textContent = T('Listo, te abrimos WhatsApp.', 'Done — opening WhatsApp.');
        waStatus.classList.add('ok');
      } else {
        // Sin numero cargado todavia: al menos quedan los datos guardados.
        waStatus.textContent = T('Gracias, ', 'Thank you, ') + name + T('. Te vamos a contactar a la brevedad.', '. We will be in touch shortly.');
        waStatus.classList.add('ok');
      }

      waForm.reset();
      waSubmit.disabled = false;
      waSubmit.textContent = T('Iniciar conversación', 'Start a conversation');
    });
  }
} catch (e) { console.error('wa-lead', e); }

try {
  /* ---------- PRENSA + NEWS: solapas y años combinados ----------
     Una sola lista cronologica (mas nuevo primero). Las solapas filtran por
     grupo y los botones por año; ambos filtros se aplican juntos. */
  const feed = document.getElementById('pressFeed');
  const tabs = document.querySelectorAll('#pressTabs .press-tab');
  const yearBtns = document.querySelectorAll('#pressYears .filter-btn');
  const count = document.getElementById('pressCount');

  if (feed && tabs.length && yearBtns.length) {
    const rows = Array.from(feed.querySelectorAll('.press-row'));
    let grupo = 'all';
    let anio = 'all';

    function aplicar() {
      let visibles = 0;
      rows.forEach(r => {
        const ok = (grupo === 'all' || r.dataset.group === grupo) &&
                   (anio === 'all' || r.dataset.year === anio);
        r.hidden = !ok;
        if (ok) visibles++;
      });

      // los años sin resultados dentro del grupo elegido se desactivan
      yearBtns.forEach(b => {
        const y = b.dataset.year;
        if (y === 'all') return;
        const hay = rows.some(r => r.dataset.year === y && (grupo === 'all' || r.dataset.group === grupo));
        b.disabled = !hay;
      });

      if (count) {
        const que = grupo === 'news' ? 'novedades' : (grupo === 'prensa' ? 'publicaciones' : 'entradas');
        count.textContent = visibles === 1 ? `1 ${que.replace(/s$/, '')}` : `${visibles} ${que}`;
      }
    }

    tabs.forEach(tab => tab.addEventListener('click', () => {
      tabs.forEach(x => x.classList.remove('active'));
      tab.classList.add('active');
      grupo = tab.dataset.group;
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
      aplicar();
    }));

    aplicar();
  }
} catch (e) { console.error('press-filters', e); }

try {
  /* ---------- VER TODO: GALERIAS DE OBRA Y GRILLA DE VIDEOS ----------
     Las dos muestran unas pocas y guardan el resto detras de un boton. Al
     abrirlas hay que avisarle a ScrollTrigger: aparecen decenas de figuras y
     todo lo que viene despues se corre hacia abajo, asi que sus puntos de
     disparo quedan viejos.

     Los rotulos vienen del HTML (data-mas / data-menos) porque el boton dice
     "fotos" en una ficha y "videos" en prensa. Las galerias viejas solo traen
     data-total, asi que se les arma el rotulo como antes. */
  document.querySelectorAll('.gallery-more').forEach(btn => {
    const grid = btn.previousElementSibling;
    if (!grid) return;
    const esGaleria = grid.classList.contains('gallery-grid');
    if (!esGaleria && !grid.classList.contains('press-featured')) return;

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
