/* Genera tapas para las publicaciones que todavia no tienen una.

   Las notas digitales se capturan desde su pagina original. Las publicaciones
   sin enlace usan su ficha publica de HMA: no inventa una imagen ni mezcla una
   obra que podria no corresponder. Cada captura queda lista para las tarjetas,
   en WebP horizontal de 1200 x 675.

   NODE_PATH=<dependencias> node docs/capturar_tapas_prensa.js
*/
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const sharp = require('sharp');

const RAIZ = path.resolve(__dirname, '..');
const DATOS = path.join(RAIZ, 'docs', 'prensa_datos.json');
const DESTINO = path.join(RAIZ, 'assets', 'press');
const RESPALDOS_FORZADOS = new Set([
  // Estas paginas responden 200, pero solo muestran un control anti-bot o un
  // lienzo vacio. La ficha HMA comunica mejor de que publicacion se trata.
  'archidiaries-2024-11',
  'archidiaries-2024-12',
  'clarin-arq-2025-2',
  'diario-clarin-osten-2021',
]);

const selectoresMolestos = [
  '[class*="cookie"]', '[id*="cookie"]',
  '[class*="consent"]', '[id*="consent"]',
  '[class*="newsletter"]', '[id*="newsletter"]',
  '[class*="paywall"]', '[id*="paywall"]',
  '[class*="modal"]', '[role="dialog"]',
  'iframe[src*="doubleclick"]', 'iframe[src*="googlesyndication"]',
];

async function limpiarPagina(page) {
  await page.addStyleTag({ content: `
    ${selectoresMolestos.join(',')} { display: none !important; }
    html, body { scroll-behavior: auto !important; }
    * { animation: none !important; transition: none !important; }
  `}).catch(() => {});
  await page.evaluate((selectores) => {
    for (const selector of selectores) {
      document.querySelectorAll(selector).forEach((el) => el.remove());
    }
    document.documentElement.style.overflow = 'visible';
    document.body.style.overflow = 'visible';
    window.scrollTo(0, 0);
  }, selectoresMolestos).catch(() => {});
}

async function capturar(context, nota) {
  let page = await context.newPage();
  const forzarFicha = RESPALDOS_FORZADOS.has(nota.slug);
  const externa = forzarFicha ? '' : String(nota.link || '').trim();
  const ficha = `https://estudiohma.com/prensa/${nota.slug}/`;
  const salida = path.join(DESTINO, `${nota.slug}.webp`);
  if (fs.existsSync(salida) && !forzarFicha) {
    console.log(`YA  ${nota.slug}`);
    await page.close();
    return true;
  }
  try {
    let origen = externa ? 'pagina original' : 'ficha HMA';
    let url = externa || ficha;
    try {
      const respuesta = await page.goto(url, {
        waitUntil: 'domcontentloaded',
        timeout: 45000,
      });
      if (respuesta && respuesta.status() >= 400) {
        throw new Error(`HTTP ${respuesta.status()}`);
      }
    } catch (error) {
      if (!externa) throw error;
      console.warn(`RESPALDO  ${nota.slug}  ${error.message.split('\n')[0]}`);
      origen = 'ficha HMA';
      url = ficha;
      // Un error DNS deja a Chrome navegando hacia chrome-error://. Una pagina
      // nueva evita que esa navegacion tardia interrumpa el respaldo.
      await page.close();
      page = await context.newPage();
      const respuesta = await page.goto(url, {
        waitUntil: 'domcontentloaded',
        timeout: 45000,
      });
      if (respuesta && respuesta.status() >= 400) {
        throw new Error(`respaldo HTTP ${respuesta.status()}`);
      }
    }
    await page.waitForTimeout(3500);
    await limpiarPagina(page);
    await page.waitForTimeout(500);
    const png = await page.screenshot({
      type: 'png',
      fullPage: false,
      animations: 'disabled',
    });
    await sharp(png)
      .resize(1200, 675, { fit: 'cover', position: 'top' })
      .webp({ quality: 82, effort: 5 })
      .toFile(salida);
    console.log(`OK  ${nota.slug}  ${origen}`);
    return true;
  } catch (error) {
    console.error(`ERROR  ${nota.slug}  ${error.message}`);
    return false;
  } finally {
    await page.close();
  }
}

async function main() {
  const notas = JSON.parse(fs.readFileSync(DATOS, 'utf8'));
  const faltantes = notas.filter((nota) => !nota.tapa || RESPALDOS_FORZADOS.has(nota.slug));
  fs.mkdirSync(DESTINO, { recursive: true });

  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
    args: ['--disable-dev-shm-usage', '--disable-gpu'],
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 810 },
    deviceScaleFactor: 1,
    locale: 'es-AR',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      + '(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
  });

  let hechas = 0;
  for (const nota of faltantes) {
    if (await capturar(context, nota)) hechas += 1;
  }
  await context.close();
  await browser.close();

  let enlazadas = 0;
  for (const nota of notas) {
    if (nota.tapa) continue;
    const archivo = path.join(DESTINO, `${nota.slug}.webp`);
    if (!fs.existsSync(archivo)) continue;
    nota.tapa = `/assets/press/${nota.slug}.webp`;
    enlazadas += 1;
  }
  if (enlazadas) {
    fs.writeFileSync(DATOS, `${JSON.stringify(notas, null, 1)}\n`, 'utf8');
  }

  console.log(`\nCapturas: ${hechas} de ${faltantes.length}`);
  console.log(`Portadas enlazadas al archivo de Prensa: ${enlazadas}`);
  if (hechas !== faltantes.length) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
