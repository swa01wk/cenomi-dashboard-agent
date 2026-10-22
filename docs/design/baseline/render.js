const { chromium } = require('/opt/npm-tools/node_modules/playwright');
const fs = require('fs');
const canvas = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = process.argv[3];
(async () => {
  const b = await chromium.launch();
  const results = [];
  for (const [file, meta] of Object.entries(canvas.boards)) {
    const p = await b.newPage({ viewport: { width: meta.w || 1440, height: 1000 } });
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    try {
      await p.goto('http://localhost:8766/' + file, { waitUntil: 'load', timeout: 30000 });
      await p.waitForTimeout(2500);
      const out = outDir + '/' + file.replace('.dc.html', '.png');
      await p.screenshot({ path: out, fullPage: true });
      results.push({ file, page: meta.page, title: meta.title, interactive: !!meta.is_interactive, png: out.split('/').pop(), errors: errs.slice(0, 3) });
    } catch (e) { results.push({ file, error: String(e) }); }
    await p.close();
  }
  fs.writeFileSync(outDir + '/render_report.json', JSON.stringify(results, null, 1));
  await b.close();
})();
