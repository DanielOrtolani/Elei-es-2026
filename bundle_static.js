const fs = require('fs');
const path = require('path');

async function bundle() {
  const repo = __dirname;
  const brain = 'C:\\Users\\ortol\\.gemini\\antigravity\\brain\\217781a3-1ac8-4982-a57b-100af633710e';

  const stripBom = s => s.replace(/^\uFEFF/, '');
  const htmlRaw = stripBom(fs.readFileSync(path.join(repo, 'public', 'index.html'), 'utf8'));
  const cssRaw = stripBom(fs.readFileSync(path.join(repo, 'public', 'css', 'liquid-glass.css'), 'utf8'));
  const jsRaw = stripBom(fs.readFileSync(path.join(repo, 'public', 'js', 'app.js'), 'utf8'));

  const [pollsRes, backtestRes, projRes, rfRes] = await Promise.all([
    fetch('http://localhost:3000/api/polls-sabado-2022').then(r => r.json()),
    fetch('http://localhost:3000/api/backtest-2022').then(r => r.json()),
    fetch('http://localhost:3000/api/projections-2026').then(r => r.json()),
    fetch('http://localhost:3000/api/rf-coefficients').then(r => r.json())
  ]);

  const inlineBlock = [
    '    // Embedded directly from localhost:3000 APIs',
    `    const pollsRes = ${JSON.stringify(pollsRes)};`,
    `    const backtestRes = ${JSON.stringify(backtestRes)};`,
    `    const projRes = ${JSON.stringify(projRes)};`,
    `    const rfRes = ${JSON.stringify(rfRes)};`
  ].join('\n');

  const jsBundled = jsRaw.replace(
    /\/\/ Fetch all endpoints in parallel[\s\S]*?\]\);/,
    inlineBlock
  );

  if (jsBundled === jsRaw) {
    throw new Error('Failed to replace fetch block in app.js');
  }

  const finalHtml = htmlRaw
    .replace('<link rel="stylesheet" href="/css/liquid-glass.css" />', `<style>\n${cssRaw}\n</style>`)
    .replace('<script src="/js/app.js"></script>', `<script>\n${jsBundled}\n</script>`);

  const targets = [
    path.join(brain, 'painel_eleicoes_apple_ui.html'),
    path.join(repo, 'index.html'),
    path.join(repo, 'docs', 'index.html')
  ];

  for (const t of targets) {
    fs.mkdirSync(path.dirname(t), { recursive: true });
    fs.writeFileSync(t, finalHtml, 'utf8');
    console.log('Successfully bundled:', t, `(${fs.statSync(t).size} bytes)`);
  }
}

bundle().catch(err => {
  console.error(err);
  process.exit(1);
});
