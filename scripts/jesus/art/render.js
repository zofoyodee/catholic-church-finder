// Rasterize the painted SVG scenes to PNG with headless Chromium.
// usage: node scripts/jesus/art/render.js <svg dir> <png dir> [scale]
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
(async () => {
  const [src, dst, scale = '1'] = process.argv.slice(2);
  fs.mkdirSync(dst, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 600, height: 750 }, deviceScaleFactor: +scale });
  for (const f of fs.readdirSync(src).filter(f => f.endsWith('.svg')).sort()) {
    const svg = fs.readFileSync(path.join(src, f), 'utf8');
    await page.setContent(`<html><body style="margin:0">${svg}</body></html>`);
    await page.locator('svg').first().screenshot({ path: path.join(dst, f.replace('.svg', '.png')) });
  }
  await browser.close();
})();
