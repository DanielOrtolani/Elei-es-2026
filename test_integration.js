const http = require('http');
const assert = require('assert');
const app = require('./server');

const TEST_PORT = 3888;
const BASE_URL = `http://localhost:${TEST_PORT}`;

async function runTests() {
  console.log('=== STARTING AUTOMATED INTEGRATION SUITE (M3: LIQUID GLASS WEB APP) ===');

  const server = app.listen(TEST_PORT, async () => {
    try {
      // 1. Test Static Index
      console.log('\n[1/7] Testing GET / (Static HTML Serving)...');
      const htmlRes = await fetch(`${BASE_URL}/`);
      assert.strictEqual(htmlRes.status, 200, 'Index HTML should return HTTP 200');
      const htmlText = await htmlRes.text();
      assert(htmlText.includes('Apple Liquid Glass'), 'HTML must include Apple Liquid Glass title');
      assert(htmlText.includes('liquid-glass.css'), 'HTML must link liquid-glass.css');
      assert(htmlText.includes('app.js'), 'HTML must link app.js');
      console.log('      [PASS] Index HTML delivered properly with Liquid Glass elements.');

      // 2. Test Static CSS
      console.log('\n[2/7] Testing GET /css/liquid-glass.css...');
      const cssRes = await fetch(`${BASE_URL}/css/liquid-glass.css`);
      assert.strictEqual(cssRes.status, 200, 'CSS should return HTTP 200');
      const cssText = await cssRes.text();
      assert(cssText.includes('backdrop-filter: var(--glass-blur)'), 'CSS must include backdrop-filter');
      assert(cssText.includes('--glass-bg: rgba(255, 255, 255, 0.70)'), 'CSS must use translucent glass background');
      assert(cssText.includes('#F5F5F7'), 'CSS must use Apple canvas color #F5F5F7');
      console.log('      [PASS] Liquid Glass CSS delivered with signature frosted glass styling.');

      // 3. Test Static JS
      console.log('\n[3/7] Testing GET /js/app.js...');
      const jsRes = await fetch(`${BASE_URL}/js/app.js`);
      assert.strictEqual(jsRes.status, 200, 'JS should return HTTP 200');
      const jsText = await jsRes.text();
      assert(jsText.includes('renderPollsRankingChart'), 'JS must include Chart.js rendering logic');
      console.log('      [PASS] App JS delivered cleanly.');

      // 4. Test GET /api/health
      console.log('\n[4/7] Testing GET /api/health...');
      const healthRes = await fetch(`${BASE_URL}/api/health`);
      assert.strictEqual(healthRes.status, 200, 'Health endpoint should return HTTP 200');
      const healthData = await healthRes.json();
      assert.strictEqual(healthData.status, 'ok', 'Status must be ok');
      assert(healthData.timestamp, 'Timestamp must be present');
      console.log(`      [PASS] Health OK. Server: ${healthData.server}, Uptime: ${healthData.uptimeSeconds}s`);

      // 5. Test GET /api/polls-sabado-2022
      console.log('\n[5/7] Testing GET /api/polls-sabado-2022 (Dynamic CSV Parsing)...');
      const pollsRes = await fetch(`${BASE_URL}/api/polls-sabado-2022`);
      assert.strictEqual(pollsRes.status, 200, 'Polls endpoint should return HTTP 200');
      const pollsData = await pollsRes.json();
      assert(pollsData.success, 'Response must indicate success');
      assert.strictEqual(pollsData.count, 8, 'Must return exactly 8 Saturday eve polls');
      assert.strictEqual(pollsData.polls.length, 8, 'Polls array length must be 8');
      assert(pollsData.references.length >= 2, 'References array must contain TSE & Method 1');

      // Validate top poll (Genial/Quaest)
      const topPoll = pollsData.polls[0];
      assert.strictEqual(topPoll.instituto, 'Genial/Quaest', 'Top institute must be Genial/Quaest');
      assert.strictEqual(topPoll.lula_m2_pct, 50.93, 'Quaest Method 2 Lula must be 50.93%');
      assert.strictEqual(topPoll.erro_placar_m2, 0.03, 'Quaest Method 2 error must be 0.03 p.p.');
      console.log(`      [PASS] 8 Saturday polls parsed dynamically. Top poll: ${topPoll.instituto} (Erro M2: ${topPoll.erro_placar_m2} p.p.)`);

      // 6. Test GET /api/backtest-2022
      console.log('\n[6/7] Testing GET /api/backtest-2022 (27 UFs & Metrics)...');
      const btRes = await fetch(`${BASE_URL}/api/backtest-2022`);
      assert.strictEqual(btRes.status, 200, 'Backtest endpoint should return HTTP 200');
      const btData = await btRes.json();
      assert(btData.success, 'Response must indicate success');
      assert.strictEqual(btData.states.length, 27, 'Must return exactly 27 states');
      assert.strictEqual(btData.summary.national_real.lula_pct, 50.90, 'Real Lula pct must be 50.90%');
      assert.strictEqual(btData.summary.national_real.bolso_pct, 49.10, 'Real Bolso pct must be 49.10%');
      assert.strictEqual(btData.summary.national_method1_rf.rmse_estadual, 1.58, 'Method 1 RMSE must be 1.58 p.p.');
      console.log(`      [PASS] 27 states parsed. Method 1 RMSE: ${btData.summary.national_method1_rf.rmse_estadual} p.p., Winner accuracy: ${btData.summary.national_method1_rf.acertos_uf}`);

      // 7. Test GET /api/projections-2026 & /api/rf-coefficients
      console.log('\n[7/7] Testing GET /api/projections-2026 & /api/rf-coefficients...');
      const projRes = await fetch(`${BASE_URL}/api/projections-2026`);
      assert.strictEqual(projRes.status, 200, 'Projections endpoint should return HTTP 200');
      const projData = await projRes.json();
      assert.strictEqual(projData.states.length, 27, 'Must return 27 states for 2026');

      const rfRes = await fetch(`${BASE_URL}/api/rf-coefficients`);
      assert.strictEqual(rfRes.status, 200, 'RF Coefs endpoint should return HTTP 200');
      const rfData = await rfRes.json();
      assert.strictEqual(rfData.coefficients.length, 27, 'Must return 27 state coefficients');
      console.log('      [PASS] Projections and RF coefficients verified.');

      console.log('\n========================================================================');
      console.log('  ALL INTEGRATION TESTS PASSED CLEANLY (100% SPEC COMPLIANCE)');
      console.log('========================================================================\n');

      server.close();
      process.exit(0);
    } catch (testErr) {
      console.error('\n[FAIL] Test failure:', testErr);
      server.close();
      process.exit(1);
    }
  });
}

runTests();
