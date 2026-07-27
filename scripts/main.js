try {
  /* ---------- MENU MOBILE ---------- */
  const menuBtn = document.getElementById('menuBtn');
  const mobileMenu = document.getElementById('mobile-menu');
  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', () => {
      const open = mobileMenu.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      mobileMenu.classList.remove('open');
      menuBtn.setAttribute('aria-expanded', 'false');
    }));
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
  /* ---------- COUNT-UP STATS ---------- */
  const statEls = document.querySelectorAll('.stat-num[data-count]');
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
  /* ---------- LIGHTBOX ---------- */
  const lightbox = document.getElementById('lightbox');
  if (lightbox) {
    const lbImg = document.getElementById('lbImg');
    const lbName = document.getElementById('lbName');
    const lbMeta = document.getElementById('lbMeta');
    const lbThumbs = document.getElementById('lbThumbs');
    const lbClose = document.getElementById('lbClose');
    const lbPrev = document.getElementById('lbPrev');
    const lbNext = document.getElementById('lbNext');

    const PROJECTS = Array.from(document.querySelectorAll('[data-slug][data-cat], [data-slug][data-plr]')).reduce((acc, card) => {
      const slug = card.dataset.slug;
      if (acc.find(p => p.slug === slug)) return acc;
      const nameEl = card.querySelector('.p-name, .plr-name');
      const metaEl = card.querySelector('.p-meta, .plr-meta');
      acc.push({
        slug,
        name: nameEl ? nameEl.textContent.trim() : slug,
        metaHTML: metaEl ? metaEl.innerHTML : '',
        photos: parseInt(card.dataset.photos || '6', 10),
      });
      return acc;
    }, []);

    let currentIndex = 0, currentPhoto = 0;
    let lastFocused = null;

    function render() {
      const proj = PROJECTS[currentIndex];
      if (!proj) return;
      lbImg.src = `/assets/gallery/${proj.slug}/${currentPhoto + 1}.jpg`;
      lbImg.alt = proj.name;
      lbName.textContent = proj.name;
      lbMeta.innerHTML = proj.metaHTML;
      lbThumbs.innerHTML = '';
      for (let i = 1; i <= proj.photos; i++) {
        const t = document.createElement('img');
        t.src = `/assets/gallery/${proj.slug}/${i}.jpg`;
        t.alt = `${proj.name} — foto ${i}`;
        t.loading = 'lazy';
        t.tabIndex = 0;
        t.className = (i - 1 === currentPhoto) ? 'active' : '';
        t.addEventListener('click', () => { currentPhoto = i - 1; render(); });
        lbThumbs.appendChild(t);
      }
    }

    function openBySlug(slug, triggerEl) {
      const idx = PROJECTS.findIndex(p => p.slug === slug);
      if (idx === -1) return;
      lastFocused = triggerEl || document.activeElement;
      currentIndex = idx; currentPhoto = 0;
      render();
      lightbox.classList.add('open');
      document.body.style.overflow = 'hidden';
      lbClose.focus();
    }

    function close() {
      lightbox.classList.remove('open');
      document.body.style.overflow = '';
      if (lastFocused) { lastFocused.focus(); lastFocused = null; }
    }

    function next() { const p = PROJECTS[currentIndex]; currentPhoto = (currentPhoto + 1) % p.photos; render(); }
    function prev() { const p = PROJECTS[currentIndex]; currentPhoto = (currentPhoto - 1 + p.photos) % p.photos; render(); }

    document.querySelectorAll('[data-slug]').forEach(card => {
      card.setAttribute('tabindex', '0');
      card.setAttribute('role', 'button');
      card.addEventListener('click', () => openBySlug(card.dataset.slug, card));
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openBySlug(card.dataset.slug, card); }
      });
    });

    lbClose.addEventListener('click', close);
    lbNext.addEventListener('click', (e) => { e.stopPropagation(); next(); });
    lbPrev.addEventListener('click', (e) => { e.stopPropagation(); prev(); });
    lightbox.addEventListener('click', (e) => { if (e.target === lightbox) close(); });
    document.addEventListener('keydown', (e) => {
      if (!lightbox.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowRight') next();
      if (e.key === 'ArrowLeft') prev();
      if (e.key === 'Tab') {
        const focusables = lightbox.querySelectorAll('button, img[tabindex]');
        const list = Array.from(focusables);
        if (!list.length) return;
        const first = list[0], last = list[list.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
  }
} catch (e) { console.error('lightbox', e); }

try {
  /* ---------- SCROLLSPY ---------- */
  const navLinks = document.querySelectorAll('nav.primary-nav a[href]');
  const path = window.location.pathname.replace(/\/index\.html$/, '/');
  navLinks.forEach(a => {
    const href = a.getAttribute('href');
    if (href === path || (href !== '/' && path.startsWith(href))) {
      a.setAttribute('aria-current', 'page');
    }
  });
} catch (e) { console.error('scrollspy', e); }

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
