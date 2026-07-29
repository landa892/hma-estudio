/* ---------- GSAP + LENIS (smooth scroll), referencia Awwwards/mvrdv.com ----------
   Cargados por CDN (script tags, sin build step). Si el CDN no responde, el sitio
   sigue funcionando igual con las animaciones CSS de siempre — nunca se rompe por
   esto. Lenis queda desactivado en touch (el scroll nativo del celular ya es
   suave) y si el usuario pidio "reducir movimiento" en su sistema. */
const gsapReady = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const isTouchDevice = window.matchMedia('(pointer: coarse)').matches;
let lenis = null;

if (gsapReady) {
  try {
    gsap.registerPlugin(ScrollTrigger);
    document.documentElement.classList.add('gsap-active');

    if (typeof window.Lenis !== 'undefined' && !prefersReducedMotion && !isTouchDevice) {
      lenis = new Lenis({ duration: 1.1, smoothWheel: true });
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add((time) => lenis.raf(time * 1000));
      gsap.ticker.lagSmoothing(0);
    }
  } catch (e) { console.error('gsap-init', e); }
}

if (gsapReady && !prefersReducedMotion) {
  try {
    /* ---------- SCALE ON SCROLL: fotos de proyectos (hero, banners, galerias) ----------
       En .project-banner el target es el wrapper (no la img) porque la img tiene
       su propio scale al hover en CSS — si GSAP tocara la misma img, el transform
       inline pisaria el :hover. Dos elementos, dos transforms, sin pelearse. */
    const scaleImgs = document.querySelectorAll(
      '.hero-home--photo img, .project-banner__img-wrap, .project-gallery__item img, .project-row__photo img'
    );
    scaleImgs.forEach((img) => {
      const section = img.closest('.hero-home--photo, .project-banner, .project-gallery__item, .project-row');
      if (!section) return;
      gsap.fromTo(img,
        { scale: 1.15 },
        {
          scale: 1,
          ease: 'none',
          scrollTrigger: { trigger: section, start: 'top bottom', end: 'bottom top', scrub: 1 },
        }
      );
    });
  } catch (e) { console.error('scale-on-scroll', e); }

  try {
    /* ---------- PARALLAX: textos que acompanan a las fotos ---------- */
    const parallaxEls = document.querySelectorAll('.pb-content-inner p, .project-row__text p');
    parallaxEls.forEach((el) => {
      const section = el.closest('.project-banner, .project-row');
      if (!section) return;
      gsap.fromTo(el,
        { yPercent: -12 },
        {
          yPercent: 12,
          ease: 'none',
          scrollTrigger: { trigger: section, start: 'top bottom', end: 'bottom top', scrub: 1 },
        }
      );
    });
  } catch (e) { console.error('parallax', e); }

  try {
    /* ---------- MARQUEE: banda de categorias en movimiento continuo (home) ---------- */
    const track = document.querySelector('.marquee__track');
    if (track) {
      const marqueeTween = gsap.to(track, { xPercent: -50, ease: 'none', duration: 22, repeat: -1 });
      const boost = () => {
        gsap.to(marqueeTween, { timeScale: 2.2, duration: 0.3, overwrite: true });
        clearTimeout(track._marqueeTimeout);
        track._marqueeTimeout = setTimeout(() => {
          gsap.to(marqueeTween, { timeScale: 1, duration: 0.6 });
        }, 200);
      };
      if (lenis) lenis.on('scroll', boost);
      else window.addEventListener('scroll', boost, { passive: true });
    }
  } catch (e) { console.error('marquee', e); }
}

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
  /* ---------- BUSQUEDA (icono lupa dentro del menu, ref. mvrdv.com) ---------- */
  const searchBtn = document.getElementById('siteMenuSearchBtn');
  const searchForm = document.getElementById('siteMenuSearch');
  if (searchBtn && searchForm) {
    const searchInput = searchForm.querySelector('input');
    searchBtn.addEventListener('click', () => {
      const isOpen = searchForm.classList.toggle('open');
      searchBtn.setAttribute('aria-expanded', String(isOpen));
      if (isOpen && searchInput) searchInput.focus();
    });
  }
} catch (e) { console.error('search-toggle', e); }

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
