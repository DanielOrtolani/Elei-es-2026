/**
 * ==========================================================================
 * APPLE LIQUID GLASS ELECTORAL INTELLIGENCE WEB APP
 * Client-Side Application Logic • Vanilla JS + Chart.js
 * ==========================================================================
 */

const state = {
  polls: [],
  references: [],
  groundTruth: null,
  backtest: null,
  projections: null,
  rfCoefs: [],
  charts: {
    polls: null,
    rf: null
  }
};

// ==========================================
// FORMATTING HELPERS
// ==========================================
function fmtInt(val) {
  const n = Number(val) || 0;
  return Math.round(n).toLocaleString('pt-BR');
}

function fmtDec(val, decimals = 2) {
  if (val === null || val === undefined || isNaN(Number(val))) return '—';
  return Number(val).toFixed(decimals).replace('.', ',');
}

function fmtSign(val, decimals = 2) {
  if (val === null || val === undefined || isNaN(Number(val))) return '—';
  const n = Number(val);
  const prefix = n > 0 ? '+' : '';
  return prefix + n.toFixed(decimals).replace('.', ',');
}

// ==========================================
// TAB NAVIGATION
// ==========================================
function switchTab(tabId) {
  const tabs = ['tab-backtest', 'tab-projections', 'tab-rf'];
  tabs.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden');
  });

  const target = document.getElementById(tabId);
  if (target) target.classList.remove('hidden');

  // Update nav buttons
  document.querySelectorAll('.nav-tab').forEach(btn => btn.classList.remove('active'));
  if (tabId === 'tab-backtest') document.getElementById('tab-btn-backtest').classList.add('active');
  if (tabId === 'tab-projections') document.getElementById('tab-btn-projections').classList.add('active');
  if (tabId === 'tab-rf') document.getElementById('tab-btn-rf').classList.add('active');

  // Re-render / resize charts
  if (tabId === 'tab-backtest' && state.charts.polls) {
    state.charts.polls.resize();
  } else if (tabId === 'tab-rf' && !state.charts.rf) {
    renderRfChart();
  } else if (tabId === 'tab-rf' && state.charts.rf) {
    state.charts.rf.resize();
  }
}

// ==========================================
// DATA INITIALIZATION
// ==========================================
async function initApp() {
  try {
    console.log('[Liquid Glass] Fetching dynamic API datasets...');
    
    // Fetch all endpoints in parallel
    const [pollsRes, backtestRes, projRes, rfRes] = await Promise.all([
      fetch('/api/polls-sabado-2022').then(r => r.json()),
      fetch('/api/backtest-2022').then(r => r.json()),
      fetch('/api/projections-2026').then(r => r.json()),
      fetch('/api/rf-coefficients').then(r => r.json())
    ]);

    if (pollsRes.success) {
      state.polls = pollsRes.polls;
      state.references = pollsRes.references;
      state.groundTruth = pollsRes.ground_truth_tse;
    }

    if (backtestRes.success) {
      state.backtest = backtestRes;
    }

    if (projRes.success) {
      state.projections = projRes;
    }

    if (rfRes.success) {
      state.rfCoefs = rfRes.coefficients;
    }

    // Render Views
    renderBacktestTab();
    renderProjectionsTab();
    renderRfTab();

    console.log('[Liquid Glass] App successfully rendered.');
  } catch (err) {
    console.error('[Liquid Glass] Initialization error:', err);
  }
}

// ==========================================
// TAB 1: BACKTEST & POLLS RENDERING
// ==========================================
function renderBacktestTab() {
  renderBacktestThermometers();
  renderPollsRankingChart();
  renderPollsTable();
  renderBacktestStatesTable();
}

function renderBacktestThermometers() {
  const box = document.getElementById('thermometer-backtest-box');
  if (!box) return;

  const gt = state.groundTruth || { lula_pct: 50.90, bolso_pct: 49.10 };
  const m1 = state.backtest?.summary?.national_method1_rf || { lula_pct: 52.30, bolso_pct: 47.70 };
  
  // Find top poll (Quaest)
  const quaest = state.polls.find(p => p.instituto.includes('Quaest')) || { lula_m2_pct: 50.93, bolso_m2_pct: 49.07, erro_placar_m2: 0.03 };

  // Calculate average of 6 presencial polls
  const presencialPolls = state.polls.filter(p => p.metodologia === 'Presencial');
  const avgPresencialLulaM2 = presencialPolls.length > 0
    ? presencialPolls.reduce((acc, p) => acc + p.lula_m2_pct, 0) / presencialPolls.length
    : 51.12;
  const avgPresencialBolsoM2 = 100 - avgPresencialLulaM2;

  const rows = [
    {
      title: '1. Resultado Oficial TSE 2022 (Urnas — Ground Truth)',
      badge: 'Placar Oficial: 50,90% x 49,10% (+1,80 p.p. Lula)',
      lula: gt.lula_pct,
      bolso: gt.bolso_pct,
      colorLula: 'var(--apple-green)',
      colorBolso: 'var(--apple-blue)',
      segLulaClass: 'seg-green',
      segBolsoClass: 'seg-blue'
    },
    {
      title: '2. Método 1: Random Forest Out-of-Time + Urnas 1ºT (Sem Entrevistas)',
      badge: 'RMSE Estadual: 1,58 p.p. • R² = 0,9887 • Acerto 26/27 UFs',
      lula: m1.lula_pct,
      bolso: m1.bolso_pct,
      colorLula: 'var(--apple-red)',
      colorBolso: 'var(--apple-blue)',
      segLulaClass: 'seg-red',
      segBolsoClass: 'seg-blue'
    },
    {
      title: '3. Genial/Quaest Véspera + Método 2 (Abstenção RF)',
      badge: 'Menor Erro de Todas as Pesquisas: 0,03 p.p. (50,93% x 49,07%)',
      lula: quaest.lula_m2_pct,
      bolso: quaest.bolso_m2_pct,
      colorLula: 'var(--apple-red)',
      colorBolso: 'var(--apple-blue)',
      segLulaClass: 'seg-red',
      segBolsoClass: 'seg-blue'
    },
    {
      title: '4. Média das Pesquisas Presenciais com Método 2 (Abstenção RF)',
      badge: 'Erro Médio Converge para Apenas +0,22 p.p. frente ao TSE',
      lula: Number(avgPresencialLulaM2.toFixed(2)),
      bolso: Number(avgPresencialBolsoM2.toFixed(2)),
      colorLula: 'var(--apple-red)',
      colorBolso: 'var(--apple-blue)',
      segLulaClass: 'seg-red',
      segBolsoClass: 'seg-blue'
    }
  ];

  box.innerHTML = rows.map(r => `
    <div class="thermometer-row">
      <div class="thermometer-meta">
        <span style="color: var(--text-primary);">${r.title}</span>
        <span class="mono">
          Lula <b>${fmtDec(r.lula)}%</b> vs. <b>${fmtDec(r.bolso)}%</b> Bolsonaro • <span class="glass-pill pill-neutral" style="padding: 2px 8px; font-size: 11px;">${r.badge}</span>
        </span>
      </div>
      <div class="thermometer-track">
        <div class="thermometer-segment ${r.segLulaClass}" style="width: ${r.lula}%;">
          Lula ${fmtDec(r.lula)}%
        </div>
        <div class="thermometer-segment ${r.segBolsoClass}" style="width: ${r.bolso}%;">
          Bolsonaro ${fmtDec(r.bolso)}%
        </div>
        <div class="majority-line" title="Linha de 50,0% Maioria Absoluta"></div>
      </div>
    </div>
  `).join('');
}

function renderPollsRankingChart() {
  const canvas = document.getElementById('chart-polls-ranking');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  if (state.charts.polls) {
    state.charts.polls.destroy();
  }

  // Combine polls and Method 1 reference for ranking
  const items = [
    ...state.polls.map(p => ({
      name: p.instituto,
      erroBruto: p.erro_placar_bruto,
      erroM2: p.erro_placar_m2
    })),
    {
      name: 'Método 1 (RF Urnas)',
      erroBruto: null,
      erroM2: 1.40
    }
  ];

  // Sort by erroM2 ascending
  items.sort((a, b) => a.erroM2 - b.erroM2);

  const labels = items.map(it => it.name);
  const dataBruto = items.map(it => it.erroBruto);
  const dataM2 = items.map(it => it.erroM2);

  state.charts.polls = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Erro Placar Bruto (29/10/2022)',
          data: dataBruto,
          backgroundColor: 'rgba(134, 134, 139, 0.45)',
          borderColor: 'rgba(134, 134, 139, 0.85)',
          borderWidth: 1.5,
          borderRadius: 6,
          barPercentage: 0.7,
          categoryPercentage: 0.8
        },
        {
          label: 'Erro Placar Método 2 (Com Abstenção RF)',
          data: dataM2,
          backgroundColor: 'rgba(0, 113, 227, 0.75)',
          borderColor: 'rgba(0, 113, 227, 1.0)',
          borderWidth: 1.5,
          borderRadius: 6,
          barPercentage: 0.7,
          categoryPercentage: 0.8
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            font: { family: '-apple-system, SF Pro Display, sans-serif', size: 12.5, weight: '600' },
            color: '#1D1D1F',
            usePointStyle: true,
            boxWidth: 8
          }
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          titleColor: '#1D1D1F',
          bodyColor: '#48484A',
          borderColor: 'rgba(0, 0, 0, 0.1)',
          borderWidth: 1,
          padding: 12,
          boxPadding: 6,
          usePointStyle: true,
          callbacks: {
            label: function(context) {
              const val = context.raw;
              if (val === null || val === undefined) return 'Não aplicável (sem pesquisa)';
              return `${context.dataset.label}: ${fmtDec(val)} p.p.`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            color: '#48484A',
            font: { family: '-apple-system, SF Pro Text, sans-serif', size: 11.5, weight: '500' }
          }
        },
        y: {
          beginAtZero: true,
          max: 4.5,
          grid: { color: 'rgba(0, 0, 0, 0.05)' },
          ticks: {
            color: '#6E6E73',
            font: { family: 'SF Mono, monospace', size: 11 },
            callback: value => value.toFixed(1) + ' p.p.'
          },
          title: {
            display: true,
            text: 'Erro Absoluto Frente ao TSE (pontos percentuais)',
            color: '#86868B',
            font: { size: 12, weight: '600' }
          }
        }
      }
    }
  });
}

function renderPollsTable() {
  const tbody = document.getElementById('polls-table-body');
  if (!tbody) return;

  const searchTerm = (document.getElementById('poll-search-input')?.value || '').toLowerCase().trim();
  const filterMet = document.getElementById('poll-filter-select')?.value || 'all';

  // Build combined rows: References + 8 Polls
  const rows = [];

  // Add TSE Ground Truth reference row
  if (state.references && state.references.length > 0) {
    const tse = state.references.find(r => r.id === 'tse_real');
    if (tse && (filterMet === 'all' || searchTerm === '')) {
      rows.push({
        ...tse,
        rank_badge_html: `<span class="rank-badge rank-ref">TSE</span>`,
        is_ref: true
      });
    }
  }

  // Add 8 Polls
  state.polls.forEach(poll => {
    // Check search filter
    const matchesSearch = !searchTerm || 
      poll.instituto.toLowerCase().includes(searchTerm) ||
      poll.contratante.toLowerCase().includes(searchTerm) ||
      poll.registro_tse.toLowerCase().includes(searchTerm);

    // Check methodology filter
    const matchesMet = filterMet === 'all' || poll.metodologia.includes(filterMet);

    if (matchesSearch && matchesMet) {
      let badgeClass = 'rank-def';
      if (poll.rank === 1) badgeClass = 'rank-1';
      else if (poll.rank === 2) badgeClass = 'rank-2';
      else if (poll.rank === 3) badgeClass = 'rank-3';

      rows.push({
        ...poll,
        rank_badge_html: `<span class="rank-badge ${badgeClass}">${poll.rank}</span>`,
        is_ref: false
      });
    }
  });

  // Add Method 1 RF Reference
  if (state.references && state.references.length > 0) {
    const m1 = state.references.find(r => r.id === 'metodo1_rf_urnas');
    if (m1 && (filterMet === 'all' || searchTerm === '')) {
      rows.push({
        ...m1,
        rank_badge_html: `<span class="rank-badge rank-ref">ML</span>`,
        is_ref: true
      });
    }
  }

  tbody.innerHTML = rows.map(r => {
    const isTse = r.id === 'tse_real';
    const isM1 = r.id === 'metodo1_rf_urnas';
    const rowBg = isTse ? 'background: rgba(24, 154, 56, 0.08); font-weight: 600;' :
                  isM1 ? 'background: rgba(0, 113, 227, 0.08); font-weight: 600;' : '';

    const errM2Abs = Number(r.erro_placar_m2) || 0;
    const pillClass = errM2Abs <= 0.95 ? 'pill-green' : (errM2Abs <= 1.80 ? 'pill-blue' : 'pill-amber');

    return `
      <tr style="${rowBg}">
        <td>${r.rank_badge_html}</td>
        <td>
          <div style="font-weight: 700; color: var(--text-primary);">${r.instituto}</div>
          <div style="font-size: 11.5px; color: var(--text-tertiary);">${r.contratante}</div>
        </td>
        <td class="mono">
          <div><b>${r.registro_tse}</b></div>
          <div style="font-size: 11.5px; color: var(--text-tertiary);">N = ${fmtInt(r.amostra)}</div>
        </td>
        <td><span class="glass-pill pill-neutral" style="font-size: 11px;">${r.metodologia}</span></td>
        <td class="mono">
          ${r.lula_bruto_pct !== null ? `<b>${fmtDec(r.lula_bruto_pct)}%</b> x <b>${fmtDec(r.bolso_bruto_pct)}%</b>` : '—'}
        </td>
        <td class="mono" style="color: ${r.erro_placar_bruto > 0 ? 'var(--apple-red)' : 'var(--text-secondary)'};">
          ${r.erro_placar_bruto !== null ? `${fmtDec(r.erro_placar_bruto)} p.p.` : '—'}
        </td>
        <td class="mono">
          <b>${fmtDec(r.lula_m2_pct)}%</b> x <b>${fmtDec(r.bolso_m2_pct)}%</b>
        </td>
        <td>
          <span class="glass-pill ${pillClass}">
            ${isTse ? 'Oficial' : `${fmtDec(r.erro_placar_m2)} p.p.`}
          </span>
        </td>
        <td class="mono">
          ${r.reducao_erro_pp !== null ? (
            r.reducao_erro_pp > 0 ? `<span style="color: var(--apple-green); font-weight:700;">+${fmtDec(r.reducao_erro_pp)} p.p.</span>` :
            `<span style="color: var(--text-tertiary);">${fmtDec(r.reducao_erro_pp)} p.p.</span>`
          ) : '—'}
        </td>
        <td class="mono">
          <span class="glass-pill pill-green" style="font-size: 11px;">
            +${fmtInt(r.efeito_2t_gov_lula_votos || 192267)} Lula (+${fmtDec(r.efeito_2t_gov_lula_pp || 0.16, 2)} p.p.)
          </span>
        </td>
        <td class="mono">
          ${isTse ? '0,00' : (r.rmse_estadual_m2 ? `${fmtDec(r.rmse_estadual_m2)} p.p.` : '—')}
        </td>
        <td class="mono">
          <span class="glass-pill pill-neutral" style="font-size: 11.5px;">${r.acertos_vencedor_uf_m2 || '—'}</span>
        </td>
      </tr>
    `;
  }).join('');
}

function filterPollsTable() {
  renderPollsTable();
}

function renderBacktestStatesTable() {
  const tbody = document.getElementById('backtest-states-table-body');
  if (!tbody || !state.backtest || !state.backtest.states) return;

  tbody.innerHTML = state.backtest.states.map(s => {
    const errM1 = Number(s.erro_pct_bolso_m1) || 0;
    const errM2 = Number(s.erro_pct_bolso_m2) || 0;
    const lulaRealPct = Number(s.lula_2t_real_pct);
    const bolsoRealPct = Number(s.bolso_2t_real_pct);
    const isLulaWon = lulaRealPct > bolsoRealPct;

    return `
      <tr>
        <td class="mono"><b>${s.uf}</b></td>
        <td>
          <div><b>${s.estado}</b></div>
          <div style="font-size: 11.5px; color: var(--text-tertiary);">${s.regiao}</div>
        </td>
        <td class="mono">${fmtDec(s.abst_2t_real_2022)}%</td>
        <td class="mono">${fmtDec(s.abst_2t_rf_oot)}%</td>
        <td class="mono" style="color: ${Math.abs(s.erro_abst_rf) > 2 ? 'var(--apple-amber)' : 'var(--text-secondary)'};">
          ${fmtSign(s.erro_abst_rf)} p.p.
        </td>
        <td class="mono" style="color: ${isLulaWon ? 'var(--apple-red)' : 'var(--text-primary)'}; font-weight: ${isLulaWon ? '700' : '400'};">
          ${fmtDec(lulaRealPct)}%
        </td>
        <td class="mono" style="color: ${!isLulaWon ? 'var(--apple-blue)' : 'var(--text-primary)'}; font-weight: ${!isLulaWon ? '700' : '400'};">
          ${fmtDec(bolsoRealPct)}%
        </td>
        <td class="mono">${fmtDec(s.lula_m1_pct)}%</td>
        <td class="mono">${fmtDec(s.bolso_m1_pct)}%</td>
        <td class="mono"><span class="glass-pill pill-neutral">${fmtSign(errM1)} p.p.</span></td>
        <td class="mono">${fmtDec(s.lula_m2_pct)}%</td>
        <td class="mono">${fmtDec(s.bolso_m2_pct)}%</td>
        <td class="mono"><span class="glass-pill pill-neutral">${fmtSign(errM2)} p.p.</span></td>
      </tr>
    `;
  }).join('');
}

// ==========================================
// TAB 2: PROJECTIONS 2026 RENDERING
// ==========================================
function renderProjectionsTab() {
  renderProjectionsThermometers();
  renderPolls2026Table();
  renderDivergingMargins();
  renderRegionalBreakdown();
  renderTopDivergences();
  renderProjectionsTable();
}

function renderProjectionsThermometers() {
  const box = document.getElementById('thermometer-2026-box');
  if (!box || !state.projections || !state.projections.summary) return;

  const m1 = state.projections.summary.method1_rf;
  const m2 = state.projections.summary.method2_atlas;

  box.innerHTML = `
    <div class="thermometer-row">
      <div class="thermometer-meta">
        <span style="color: var(--apple-blue); font-weight: 700;">1. Método 1: Random Forest (Machine Learning de Urnas 1ºT)</span>
        <span class="mono">
          Flávio <b>${fmtDec(m1.flavio_pct)}%</b> (${fmtInt(m1.flavio_votes)}) vs. Lula <b>${fmtDec(m1.lula_pct)}%</b> (${fmtInt(m1.lula_votes)}) • Vantagem: <b>+${fmtDec(m1.vantagem_pp)} p.p.</b> (+${fmtInt(m1.vantagem_votos)} votos)
        </span>
      </div>
      <div class="thermometer-track">
        <div class="thermometer-segment seg-blue" style="width: ${m1.flavio_pct}%;">
          Flávio Bolsonaro ${fmtDec(m1.flavio_pct)}%
        </div>
        <div class="thermometer-segment seg-red" style="width: ${m1.lula_pct}%;">
          Lula ${fmtDec(m1.lula_pct)}%
        </div>
        <div class="majority-line" title="50% Maioria Absoluta"></div>
      </div>
    </div>

    <div class="thermometer-row">
      <div class="thermometer-meta">
        <span style="color: var(--apple-green); font-weight: 700;">2. Consenso (Média dos 5 Institutos Elegíveis de 24/10) + Coef. UF & 2ºT Gov</span>
        <span class="mono">
          Flávio <b>50,91%</b> (62.045.321) vs. Lula <b>49,09%</b> (59.827.710) • Vantagem: <b>+1,82 p.p.</b> (+2.217.611 votos)
        </span>
      </div>
      <div class="thermometer-track">
        <div class="thermometer-segment seg-blue" style="width: 50.91%;">
          Flávio Bolsonaro 50,91%
        </div>
        <div class="thermometer-segment seg-red" style="width: 49.09%;">
          Lula 49,09%
        </div>
        <div class="majority-line" title="50% Maioria Absoluta"></div>
      </div>
    </div>

    <div class="thermometer-row">
      <div class="thermometer-meta">
        <span style="color: var(--apple-indigo); font-weight: 700;">3. Datafolha / Quaest (24/10/2026) c/ Coef. Estadual & 2ºT Gov</span>
        <span class="mono">
          Flávio <b>50,89%</b> (62.015.742) vs. Lula <b>49,11%</b> (59.857.289) • Vantagem: <b>+1,78 p.p.</b> (+2.158.453 votos)
        </span>
      </div>
      <div class="thermometer-track">
        <div class="thermometer-segment seg-blue" style="width: 50.89%;">
          Flávio Bolsonaro 50,89%
        </div>
        <div class="thermometer-segment seg-red" style="width: 49.11%;">
          Lula 49,11%
        </div>
        <div class="majority-line" title="50% Maioria Absoluta"></div>
      </div>
    </div>

    <div class="thermometer-row">
      <div class="thermometer-meta">
        <span style="color: var(--apple-amber); font-weight: 700;">4. AtlasIntel (Referência) c/ Coef. Estadual & 2ºT Gov</span>
        <span class="mono">
          Flávio <b>51,23%</b> (62.431.173) vs. Lula <b>48,77%</b> (59.441.858) • Vantagem: <b>+2,46 p.p.</b> (+2.989.315 votos)
        </span>
      </div>
      <div class="thermometer-track">
        <div class="thermometer-segment seg-blue" style="width: 51.23%;">
          Flávio Bolsonaro 51,23%
        </div>
        <div class="thermometer-segment seg-red" style="width: 48.77%;">
          Lula 48,77%
        </div>
        <div class="majority-line" title="50% Maioria Absoluta"></div>
      </div>
    </div>
  `;
}

function renderPolls2026Table() {
  const tbody = document.getElementById('polls-2026-table-body');
  if (!tbody || !state.projections || !state.projections.polls2026) return;

  const polls = state.projections.polls2026;
  const rowsHtml = polls.map(p => {
    const isAtlas = p.poll_id === 'atlasintel';
    const rowStyle = isAtlas ? 'background: rgba(217, 119, 6, 0.06);' : '';
    return `
      <tr style="${rowStyle}">
        <td>
          <div style="font-weight: 700; color: var(--text-primary);">${p.instituto}</div>
          <div style="font-size: 11.5px; color: var(--text-tertiary);">${p.contratante} • ${p.data_divulgacao}</div>
        </td>
        <td class="mono">
          <div><b>${p.registro_tse}</b></div>
          <div style="font-size: 11.5px; color: var(--text-tertiary);">N = ${fmtInt(p.amostra)} (±${fmtDec(p.margem_erro, 1)} p.p.)</div>
        </td>
        <td><span class="glass-pill pill-neutral" style="font-size: 11px;">${p.metodologia}</span></td>
        <td class="mono">
          <b style="color: var(--apple-blue);">${fmtDec(p.flavio_headline_valid, 1)}%</b> x <b style="color: var(--apple-red);">${fmtDec(p.lula_headline_valid, 1)}%</b>
        </td>
        <td class="mono">
          <b style="color: var(--apple-blue);">${fmtDec(p.pct_flavio_abst_rf, 2)}%</b> x <b style="color: var(--apple-red);">${fmtDec(p.pct_lula_abst_rf, 2)}%</b>
        </td>
        <td class="mono" style="color: var(--apple-blue); font-weight: 600;">${fmtInt(p.votos_flavio_abst_rf)}</td>
        <td class="mono" style="color: var(--apple-red); font-weight: 600;">${fmtInt(p.votos_lula_abst_rf)}</td>
        <td class="mono">
          <span class="glass-pill pill-blue">+${fmtInt(p.vantagem_flavio_abst_rf_votos)} (+${fmtDec(p.vantagem_flavio_abst_rf_pp, 2)} p.p.)</span>
        </td>
        <td class="mono">
          <span class="glass-pill pill-indigo">+${fmtInt(p.saldo_flavio_6ufs_com_2t_gov || 320941)} Flávio</span>
        </td>
        <td class="mono">
          <span class="glass-pill pill-green">+${fmtInt(p.efeito_2t_gov_flavio_votos || 191030)} Flávio (+${fmtDec(p.efeito_2t_gov_flavio_pp || 0.16, 2)} p.p.)</span>
        </td>
      </tr>
    `;
  });

  // Add Consensus Average Row (5 Eligible Polls)
  rowsHtml.push(`
    <tr style="background: rgba(24, 154, 56, 0.08); font-weight: 700;">
      <td>
        <div style="font-weight: 800; color: var(--apple-green);">MÉDIA / CONSENSO (5 Institutos Elegíveis)</div>
        <div style="font-size: 11.5px; color: var(--text-secondary);">Apenas pesquisas com recorte por estado e efeito 2ºT Gov</div>
      </td>
      <td class="mono"><b>CONSENSO 24/10</b><div style="font-size: 11.5px; color: var(--text-tertiary);">N = 19.608</div></td>
      <td><span class="glass-pill pill-green" style="font-size: 11px;">Ensemble 5 Elegíveis</span></td>
      <td class="mono"><b style="color: var(--apple-blue);">50,98%</b> x <b style="color: var(--apple-red);">49,02%</b></td>
      <td class="mono"><b style="color: var(--apple-blue);">50,91%</b> x <b style="color: var(--apple-red);">49,09%</b></td>
      <td class="mono" style="color: var(--apple-blue);">62.045.321</td>
      <td class="mono" style="color: var(--apple-red);">59.827.710</td>
      <td class="mono"><span class="glass-pill pill-green">+2.217.611 (+1,82 p.p.)</span></td>
      <td class="mono"><span class="glass-pill pill-indigo">+320.941 Flávio</span></td>
      <td class="mono"><span class="glass-pill pill-green">+191.030 Flávio (+0,16 p.p.)</span></td>
    </tr>
  `);

  tbody.innerHTML = rowsHtml.join('');
}

function renderDivergingMargins() {
  const container = document.getElementById('diverging-margins-container');
  if (!container || !state.projections || !state.projections.states) return;

  const mode = document.getElementById('select-method-diverging')?.value || 'm1';
  const marginKey = mode === 'm1' ? 'margem_m1' : 'margem_m2';

  // Sort states by margin descending
  const sorted = [...state.projections.states].sort((a, b) => b[marginKey] - a[marginKey]);

  container.innerHTML = sorted.map(s => {
    const m = Number(s[marginKey]);
    const isFlavio = m >= 0;
    const widthPct = Math.min(48, Math.abs(m) * 0.95);

    return `
      <div class="bar-row">
        <div class="bar-label"><b>${s.uf}</b> — ${s.estado}</div>
        <div class="bar-track-diverging">
          <div class="bar-zero-axis"></div>
          ${isFlavio
            ? `<div class="bar-fill-right" style="margin-left: 50%; width: ${widthPct}%;"></div>`
            : `<div class="bar-fill-left" style="margin-left: ${50 - widthPct}%; width: ${widthPct}%;"></div>`
          }
        </div>
        <div class="bar-val" style="color: ${isFlavio ? 'var(--apple-blue)' : 'var(--apple-red)'};">
          ${fmtSign(m, 1)} p.p.
        </div>
      </div>
    `;
  }).join('');
}

function renderRegionalBreakdown() {
  const box = document.getElementById('regional-summary-box');
  if (!box || !state.projections || !state.projections.states) return;

  const regions = ['Sudeste', 'Nordeste', 'Sul', 'Norte', 'Centro-Oeste'];
  const maxVolume = 32000000;

  box.innerHTML = regions.map(reg => {
    const statesInReg = state.projections.states.filter(s => s.regiao === reg);
    const flavioVotes = statesInReg.reduce((acc, s) => acc + s.votos_flavio_m1, 0);
    const lulaVotes = statesInReg.reduce((acc, s) => acc + s.votos_lula_m1, 0);
    const flavioM = flavioVotes / 1e6;
    const lulaM = lulaVotes / 1e6;

    const pctBarFlavio = Math.min(100, (flavioVotes / maxVolume) * 100);
    const pctBarLula = Math.min(100, (lulaVotes / maxVolume) * 100);

    return `
      <div style="margin-bottom: 14px;">
        <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:13px; font-weight:600;">
          <span>${reg}</span>
          <span class="mono">Flávio ${fmtDec(flavioM, 2)}M x ${fmtDec(lulaM, 2)}M Lula</span>
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 8px;">
          <div style="height: 10px; background: rgba(0, 113, 227, 0.15); border-radius: 4px; overflow:hidden;">
            <div style="height:100%; width:${pctBarFlavio}%; background: var(--apple-blue);"></div>
          </div>
          <div style="height: 10px; background: rgba(227, 36, 43, 0.15); border-radius: 4px; overflow:hidden;">
            <div style="height:100%; width:${pctBarLula}%; background: var(--apple-red);"></div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function renderTopDivergences() {
  const box = document.getElementById('top-divergences-box');
  if (!box || !state.projections || !state.projections.states) return;

  const topDiv = [...state.projections.states]
    .sort((a, b) => Math.abs(b.diff_margem) - Math.abs(a.diff_margem))
    .slice(0, 6);

  box.innerHTML = topDiv.map(s => {
    const diff = Number(s.diff_margem);
    const isPos = diff >= 0;
    const widthPct = Math.min(48, Math.abs(diff) * 5.5);

    return `
      <div class="bar-row">
        <div class="bar-label"><b>${s.uf}</b> — ${s.estado}</div>
        <div class="bar-track-diverging">
          <div class="bar-zero-axis"></div>
          ${isPos
            ? `<div class="bar-fill-right" style="margin-left: 50%; width: ${widthPct}%;"></div>`
            : `<div class="bar-fill-left" style="margin-left: ${50 - widthPct}%; width: ${widthPct}%;"></div>`
          }
        </div>
        <div class="bar-val" style="color: ${isPos ? 'var(--apple-blue)' : 'var(--apple-red)'};">
          ${fmtSign(diff, 1)} p.p.
        </div>
      </div>
    `;
  }).join('');
}

function renderProjectionsTable() {
  const tbody = document.getElementById('projections-2026-table-body');
  if (!tbody || !state.projections || !state.projections.states) return;

  const selectedPollId = document.getElementById('select-poll-2026-uf')?.value || 'atlasintel';
  const ufLookup = {};
  if (state.projections.polls2026ByUf) {
    state.projections.polls2026ByUf
      .filter(r => r.poll_id === selectedPollId)
      .forEach(r => { ufLookup[r.uf] = r; });
  }

  tbody.innerHTML = state.projections.states.map(s => {
    const pUf = ufLookup[s.uf];
    const pctFlavioM2 = pUf ? Number(pUf.pct_flavio_poll) : Number(s.pct_flavio_m2);
    const pctLulaM2 = pUf ? Number(pUf.pct_lula_poll) : Number(s.pct_lula_m2);
    const margemM2 = Number((pctFlavioM2 - pctLulaM2).toFixed(2));
    const diffMargem = Number((Number(s.margem_m1) - margemM2).toFixed(2));

    const hasGov2t = s.teve_2t_gov === 'Sim';
    const govBadge = hasGov2t
      ? `<span class="glass-pill pill-green" style="font-size: 11px;">Sim (-0,71 p.p.)</span>`
      : `<span class="glass-pill pill-neutral" style="font-size: 11px;">Não</span>`;

    return `
      <tr>
        <td class="mono"><b>${s.uf}</b></td>
        <td>
          <div><b>${s.estado}</b></div>
          <div style="font-size: 11.5px; color: var(--text-tertiary);">${s.regiao}</div>
        </td>
        <td>${govBadge}</td>
        <td class="mono">${fmtDec(s.abst_1t)}%</td>
        <td class="mono">${fmtDec(s.abst_2t_rf)}%</td>
        <td class="mono">${fmtSign(s.delta_rf)} p.p.</td>
        <td class="mono" style="color: var(--apple-blue); font-weight: 700;">${fmtDec(s.pct_flavio_m1)}%</td>
        <td class="mono" style="color: var(--apple-red); font-weight: 700;">${fmtDec(s.pct_lula_m1)}%</td>
        <td class="mono"><span class="glass-pill pill-blue">${fmtSign(s.margem_m1)} p.p.</span></td>
        <td class="mono" style="color: var(--apple-blue);">${fmtDec(pctFlavioM2)}%</td>
        <td class="mono" style="color: var(--apple-red);">${fmtDec(pctLulaM2)}%</td>
        <td class="mono"><span class="glass-pill pill-amber">${fmtSign(margemM2)} p.p.</span></td>
        <td class="mono">${fmtSign(diffMargem)} p.p.</td>
      </tr>
    `;
  }).join('');
}

// ==========================================
// TAB 3: RANDOM FOREST COEFFICIENTS
// ==========================================
function renderRfTab() {
  renderRfChart();
  renderRfTable();
}

function renderRfChart() {
  const canvas = document.getElementById('chart-rf-shap');
  if (!canvas || state.rfCoefs.length === 0) return;

  const ctx = canvas.getContext('2d');
  if (state.charts.rf) {
    state.charts.rf.destroy();
  }

  // Sort by rf_importance_pct descending (Top 12 states)
  const sorted = [...state.rfCoefs]
    .sort((a, b) => (Number(b.rf_importance_pct) || 0) - (Number(a.rf_importance_pct) || 0))
    .slice(0, 12);

  const labels = sorted.map(s => `${s.uf} — ${s.estado}`);
  const importances = sorted.map(s => Number(s.rf_importance_pct));
  const shapValues = sorted.map(s => Number(s.rf_shap_coef));

  state.charts.rf = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Importância no Modelo RF (%)',
          data: importances,
          backgroundColor: 'rgba(0, 113, 227, 0.75)',
          borderColor: 'rgba(0, 113, 227, 1.0)',
          borderWidth: 1.5,
          borderRadius: 6
        },
        {
          label: 'Coeficiente Marginal SHAP (p.p.)',
          data: shapValues,
          backgroundColor: 'rgba(88, 86, 214, 0.75)',
          borderColor: 'rgba(88, 86, 214, 1.0)',
          borderWidth: 1.5,
          borderRadius: 6
        }
      ]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            font: { family: '-apple-system, SF Pro Display, sans-serif', size: 12.5, weight: '600' },
            color: '#1D1D1F',
            usePointStyle: true
          }
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          titleColor: '#1D1D1F',
          bodyColor: '#48484A',
          borderColor: 'rgba(0, 0, 0, 0.1)',
          borderWidth: 1,
          padding: 12
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(0, 0, 0, 0.05)' },
          ticks: { font: { family: 'SF Mono, monospace', size: 11 } }
        },
        y: {
          grid: { display: false },
          ticks: { font: { family: '-apple-system, SF Pro Text, sans-serif', size: 12, weight: '500' } }
        }
      }
    }
  });
}

function renderRfTable() {
  const tbody = document.getElementById('rf-coefs-table-body');
  if (!tbody || state.rfCoefs.length === 0) return;

  tbody.innerHTML = state.rfCoefs.map(c => {
    const imp = Number(c.rf_importance_pct) || 0;
    const shap = Number(c.rf_shap_coef) || 0;
    let sensPill = 'pill-neutral';
    let sensText = 'Baixa';

    if (imp >= 10.0 || shap >= 2.0) {
      sensPill = 'pill-red';
      sensText = 'Crítica (Alta Sensibilidade)';
    } else if (imp >= 1.0 || shap >= 0.5) {
      sensPill = 'pill-amber';
      sensText = 'Moderada';
    }

    return `
      <tr>
        <td class="mono"><b>${c.uf}</b></td>
        <td>
          <div><b>${c.estado}</b></div>
          <div style="font-size: 11.5px; color: var(--text-tertiary);">${c.regiao}</div>
        </td>
        <td class="mono"><b>${fmtSign(c.rf_shap_coef, 3)}</b></td>
        <td class="mono">${fmtDec(c.rf_importance_pct, 2)}%</td>
        <td class="mono">${fmtSign(c.historico_delta_medio, 2)} p.p.</td>
        <td class="mono">${fmtSign(c.ols_fe_coef, 3)}</td>
        <td><span class="glass-pill ${sensPill}">${sensText}</span></td>
      </tr>
    `;
  }).join('');
}

// Start application upon DOM load
document.addEventListener('DOMContentLoaded', initApp);
