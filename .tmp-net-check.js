const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe' });
  for (const path of ['/', '/prensa/']) {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    const bad = [];
    page.on('response', response => {
      if (response.status() >= 400) bad.push([response.status(), response.url()]);
    });
    await page.goto('http://127.0.0.1:4173' + path, { waitUntil: 'networkidle' });
    console.log(path, JSON.stringify(bad));
    await page.close();
  }
  await browser.close();
})();
