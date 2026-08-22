const { chromium } = require('playwright');
const assert = require('assert');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe' });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const base = 'https://estudiohma.com';

  await page.goto(base + '/', { waitUntil: 'domcontentloaded' });
  assert.equal(await page.locator('.site-header .logo').count(), 0, 'el home no debe mostrar el logo de cabecera');
  for (const slug of ['indusparquet', 'parfumerie', 'hyatt-ziva']) {
    assert.equal(await page.locator(`main a[href="/proyectos/${slug}/"]`).count(), 0, `${slug} sigue en el home`);
  }
  assert.equal(await page.locator('#section-3 [data-linkedin-link]').count(), 2);
  assert.equal(await page.locator('#asociaciones .asociaciones li').count(), 5);

  await page.goto(base + '/estudio/', { waitUntil: 'domcontentloaded' });
  assert.equal((await page.locator('.estudio-fundadores h2').textContent()).trim(), 'Socios fundadores');
  assert.ok((await page.locator('img[src="/assets/estudio-equipo-2026.webp"]').getAttribute('width')) === '2560');
  assert.equal(await page.locator('#asociaciones .asociaciones li').count(), 5);

  await page.goto(base + '/prensa/', { waitUntil: 'domcontentloaded' });
  assert.equal(await page.locator('#prensaFeed .press-card').count(), 9);
  assert.equal(await page.locator('#youtubeEntrevistas .press-card').count(), 5);
  await page.locator('#prensaVisualYears [data-year="2023"]').click();
  assert.equal(await page.locator('#prensaFeed .press-card:visible').count(), 2);
  assert.equal(await page.getByText('Archivo', { exact: true }).count(), 0);

  await page.goto(base + '/proyectos/', { waitUntil: 'domcontentloaded' });
  assert.equal(await page.locator('.project-card').count(), 62);
  for (const slug of ['bienal-venecia', 'edificio-del-plata']) {
    const text = await page.locator(`.project-card[href="/proyectos/${slug}/"]`).innerText();
    assert.ok(/2024/.test(text), `${slug} no muestra 2024`);
    assert.ok(/m²/.test(text), `${slug} no muestra superficie`);
  }

  await page.goto(base + '/proyectos/tostado/', { waitUntil: 'domcontentloaded' });
  assert.ok((await page.locator('body').innerText()).includes('Buenos Aires · São Paulo · Montevideo · Miami · Madrid'));
  assert.equal(await page.getByRole('heading', { name: 'Galería', exact: true }).count(), 1);
  assert.equal(await page.getByRole('heading', { name: 'Todas las fotos', exact: true }).count(), 0);

  await page.goto(base + '/prensa/fogon-restaurante-y-bar-en-riad-arabia-saudi/', { waitUntil: 'domcontentloaded' });
  assert.equal(await page.locator('.gallery-grid--prensa .gallery-grid__item').count(), 13);
  assert.equal(await page.getByText('Ver noticia', { exact: true }).count(), 0);

  await page.goto(base + '/prensa/el-nuevo-restaurante-de-belgrano-en-un-patio-lleno/', { waitUntil: 'domcontentloaded' });
  assert.equal(await page.getByText('Ver noticia', { exact: true }).count(), 1);

  console.log('funciones publicas: OK');
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
