try {
  /* ---------- TODOS LOS TEXTOS DEL HOME SE ACHICAN HACIA ABAJO-IZQUIERDA AL
     SCROLLEAR (referencia mvrdv.com: transform-origin left bottom, ligado al
     scroll en vivo dentro del rango de CADA seccion, no a una sola aparicion).
     Aplica al hero y a los 6 project-banner. ---------- */
  const shrinkTargets = [];
  const heroSection = document.querySelector('.hero-home--photo');
  const heroWrap = document.querySelector('.hero-content-wrap');
  if (heroSection && heroWrap) shrinkTargets.push({ section: heroSection, wrap: heroWrap, varName: '--hero-scale' });

  document.querySelectorAll('.project-banner').forEach(banner => {
    const content = banner.querySelector('.project-banner__content');
    if (content) shrinkTargets.push({ section: banner, wrap: content, varName: '--pb-scale' });
  });

  if (shrinkTargets.length) {
    const MIN_SCALE = 0.55;
    function updateShrink() {
      shrinkTargets.forEach(({ section, wrap, varName }) => {
        const top = section.offsetTop;
        const height = section.offsetHeight || 1;
        const progress = Math.min(Math.max((window.scrollY - top) / height, 0), 1);
        const scale = 1 - progress * (1 - MIN_SCALE);
        wrap.style.setProperty(varName, scale.toFixed(3));
      });
    }
    window.addEventListener('scroll', () => requestAnimationFrame(updateShrink), { passive: true });
    window.addEventListener('resize', updateShrink);
    updateShrink();
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
        if (target) target.scrollIntoView({ behavior: 'smooth' });
      });
    });

    const dotsIo = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const idx = sections.indexOf(entry.target);
          if (idx === -1) return;
          dots.forEach(d => d.classList.remove('active'));
          dots[idx].classList.add('active');
        }
      });
    }, { threshold: 0.5 });
    sections.forEach(s => dotsIo.observe(s));

    /* Los puntos van en negro sobre fondo blanco y en blanco cuando quedan
       sobre una foto. rootMargin -50%/-50% deja una franja de altura cero
       justo en el centro vertical de la pantalla, que es donde estan los
       puntos: si ahi hay una foto, se activa .on-dark. */
    const darkSections = document.querySelectorAll('.hero-home--photo, .project-banner');
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
  const revealEls = document.querySelectorAll('.reveal');
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
  /* ---------- PROJECT FILTER (grilla y lista) ---------- */
  const filterBtns = document.querySelectorAll('.filter-btn');
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
      const btn = document.querySelector(`.filter-btn[data-filter="${CSS.escape(cat)}"]`);
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
        cfStatus.textContent = 'Completá nombre, email y mensaje.';
        cfStatus.classList.add('err');
        return;
      }
      cfSubmit.disabled = true; cfSubmit.textContent = 'Enviando…';
      try {
        const res = await fetch('/api/contact', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data),
        });
        const result = await res.json().catch(() => ({}));
        if (res.ok && result.ok) {
          contactForm.reset();
          cfStatus.textContent = 'Gracias, te vamos a responder a la brevedad.';
          cfStatus.classList.add('ok');
        } else {
          cfStatus.textContent = result.error || 'No se pudo enviar. Escribinos a hma@estudiohma.com.';
          cfStatus.classList.add('err');
        }
      } catch (err) {
        cfStatus.textContent = 'No se pudo enviar. Escribinos a hma@estudiohma.com.';
        cfStatus.classList.add('err');
      } finally {
        cfSubmit.disabled = false; cfSubmit.textContent = 'Enviar mensaje';
      }
    });
  }
} catch (e) { console.error('contact-form', e); }

try {
  /* ---------- FILTRO DE PRENSA POR AÑO ---------- */
  const pressFilterBtns = document.querySelectorAll('.press-filter-bar button');
  if (pressFilterBtns.length) {
    pressFilterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        pressFilterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const y = btn.dataset.year;
        document.querySelectorAll('.press-year-block').forEach(block => {
          block.style.display = (y === 'all' || block.dataset.year === y) ? '' : 'none';
        });
      });
    });
  }
} catch (e) { console.error('press-filter', e); }

try {
  /* ---------- ULTIMOS VIDEOS DE YOUTUBE (home) ----------
     La seccion arranca oculta (atributo "hidden" en el HTML) y solo se
     muestra si el feed devuelve videos reales — evita mostrar un cartel
     vacio mientras no este configurada la YOUTUBE_API_KEY. */
  const updatesSection = document.getElementById('updatesSection');
  const feedEl = document.getElementById('youtubeFeed');
  if (updatesSection && feedEl) {
    fetch('/api/youtube-latest')
      .then(r => r.json())
      .then(data => {
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
        ? '1 resultado para <b>' + escapeHtml(q) + '</b>'
        : hits.length + ' resultados para <b>' + escapeHtml(q) + '</b>';

      if (!hits.length) {
        spResults.innerHTML = '<p class="search-empty">No encontramos nada con ese término. Probá con el nombre de un proyecto, una categoría o un medio.</p>';
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
