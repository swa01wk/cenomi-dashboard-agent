const { chromium } = require('/opt/npm-tools/node_modules/playwright');
const fs = require('fs');
const canvas = JSON.parse(fs.readFileSync('boards/canvas.json', 'utf8'));
(async () => {
  const b = await chromium.launch();
  let md = '# DX1–DX6 design boards — extracted text\n\nGenerated 2026-10-22 from the local copy of the design canvas (published version 27, plus the DX5-GenUI wording fix). One section per board, in canvas order. Text only: layout, charts and interaction behaviour are preserved in renders/*.png and in the runnable boards/*.dc.html files.\n\n';
  const pages = Object.fromEntries(canvas.pages.map(p => [p.id, p.name]));
  let cur = null;
  for (const [file, meta] of Object.entries(canvas.boards)) {
    if (meta.page !== cur) { cur = meta.page; md += `\n# ${pages[cur]}\n`; }
    const p = await b.newPage({ viewport: { width: meta.w || 1440, height: 1000 } });
    await p.goto('http://localhost:8766/' + file, { waitUntil: 'load' }); await p.waitForTimeout(1500);
    let t = await p.evaluate(() => document.body.innerText);
    t = t.replace(/\n{3,}/g, '\n\n').trim();
    md += `\n## ${meta.title}\n\nFile: boards/${file} · Render: renders/${file.replace('.dc.html','.png')}${meta.is_interactive ? ' · interactive prototype' : ''}\n\n\`\`\`text\n${t}\n\`\`\`\n`;
    await p.close();
  }
  fs.writeFileSync('DESIGN_BOARDS_TEXT.md', md);
  await b.close();
})();
