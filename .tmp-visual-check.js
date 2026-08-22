const { chromium } = require('playwright');
const fs = require('fs');

const base = 'https://estudiohma.com';
const pages = [
  ['inicio', '/'],
  ['estudio', '/estudio/'],
  ['prensa', '/prensa/'],
  ['premios', '/premios/'],
  ['trabajos', '/proyectos/'],
  ['tostado', '/proyectos/tostado/'],
  ['hyatt', '/proyectos/hyatt-ziva/'],
  ['osten-foa', '/proyectos/osten-foa/'],
  ['prensa-fogon', '/prensa/fogon-restaurante-y-bar-en-riad-arabia-saudi/'],
  ['prensa-nim', '/prensa/the-nim-bar-fotografia-de-federico-kulekdjian/'],
];
const sizes = [
  ['desktop', { width: 1440, height: 900 }],
  ['tablet', { width: 820, height: 1180 }],
  ['mobile', { width: 390, height: 844 }],
];

(async () => {
  fs.mkdirSync('.tmp-visual', { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  });
  const report = [];
  for (const [sizeName, viewport] of sizes) {
    const context = await browser.newContext({ viewport, deviceScaleFactor: 1 });
    for (const [name, path] of pages) {
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push('page: ' + error.message));
      page.on('console', msg => {
        if (msg.type() === 'error' && !/favicon|linkedin/i.test(msg.text())) {
          errors.push('console: ' + msg.text());
        }
      });
      const response = await page.goto(base + path, { waitUntil: 'networkidle', timeout: 30000 });
      await page.addStyleTag({ content: '*{transition:none!important;animation:none!important}' });
      await page.evaluate(() => {
        if (window.gsap) window.gsap.globalTimeline.progress(1);
      });
      await page.waitForTimeout(250);
      const audit = await page.evaluate(() => {
        const broken = [...document.images]
          .filter(img => img.complete && img.naturalWidth === 0)
          .map(img => img.getAttribute('src'));
        const visibleOverflow = [...document.querySelectorAll('body *')]
          .filter(el => {
            const s = getComputedStyle(el);
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.right > innerWidth + 2 && s.position !== 'fixed';
          })
          .slice(0, 8)
          .map(el => `${el.tagName}.${el.className}`);
        return {
          title: document.title,
          viewport: innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          broken,
          visibleOverflow,
          h1: document.querySelector('h1')?.textContent.trim() || '',
        };
      });
      if (['inicio', 'estudio', 'prensa', 'trabajos', 'tostado', 'prensa-fogon'].includes(name)) {
        await page.screenshot({ path: `.tmp-visual/${sizeName}-${name}.png`, fullPage: false });
      }
      report.push({ sizeName, name, status: response && response.status(), errors, ...audit });
      await page.close();
    }
    await context.close();
  }
  await browser.close();
  fs.writeFileSync('.tmp-visual/report.json', JSON.stringify(report, null, 2));
  const failures = report.filter(r => r.status !== 200 || r.errors.length || r.broken.length || r.scrollWidth > r.viewport + 2);
  console.log(JSON.stringify({ checked: report.length, failures }, null, 2));
})();
