const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Path to authoritative electoral datasets (portable local ./data folder with fallback)
const LOCAL_DATA_DIR = path.join(__dirname, 'data');
const FALLBACK_DATA_DIR = path.resolve('C:\\Users\\ortol\\.gemini\\antigravity\\brain\\217781a3-1ac8-4982-a57b-100af633710e\\scratch');
const DATA_DIR = fs.existsSync(LOCAL_DATA_DIR) ? LOCAL_DATA_DIR : FALLBACK_DATA_DIR;
const PUBLIC_DIR = path.join(__dirname, 'public');

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(PUBLIC_DIR));

/**
 * Robust CSV parser that handles quoted strings and comma delimiters
 */
function parseCSV(filePath) {
  if (!fs.existsSync(filePath)) {
    console.warn(`[CSV Parser] File not found: ${filePath}`);
    return [];
  }
  const rawText = fs.readFileSync(filePath, 'utf-8').trim();
  if (!rawText) return [];

  const lines = rawText.split(/\r?\n/).filter(line => line.trim().length > 0);
  if (lines.length < 2) return [];

  // Parse header
  const headers = parseCSVLine(lines[0]);

  // Parse rows
  return lines.slice(1).map(line => {
    const values = parseCSVLine(line);
    const row = {};
    headers.forEach((header, index) => {
      const rawVal = values[index] !== undefined ? values[index].trim() : '';
      const numVal = Number(rawVal);
      if (rawVal !== '' && !isNaN(numVal) && !rawVal.includes('/') && !rawVal.includes('-') && !rawVal.includes(':')) {
        row[header] = numVal;
      } else {
        row[header] = rawVal;
      }
    });
    return row;
  });
}

function parseCSVLine(text) {
  const result = [];
  let cur = '';
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (char === '"') {
      if (inQuotes && text[i + 1] === '"') {
        cur += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === ',' && !inQuotes) {
      result.push(cur.trim());
      cur = '';
    } else {
      cur += char;
    }
  }
  result.push(cur.trim());
  return result;
}

// ==========================================
// API ENDPOINTS
// ==========================================

/**
 * Health check endpoint
 */
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptimeSeconds: Math.round(process.uptime()),
    server: 'Liquid Glass Express API'
  });
});

/**
 * Saturday Polls 2022 Comparative Dataset (8 Eve Polls + References)
 * Reads pesquisas_sabado_2022_comparativo.csv dynamically
 */
app.get('/api/polls-sabado-2022', (req, res) => {
  try {
    const csvPath = path.join(DATA_DIR, 'pesquisas_sabado_2022_comparativo.csv');
    const rawData = parseCSV(csvPath);

    // Ground Truth References
    const references = [
      {
        id: 'tse_real',
        instituto: 'Resultado Oficial TSE',
        contratante: 'Justiça Eleitoral (100% das Urnas)',
        registro_tse: 'TSE Oficial 30/10/22',
        amostra: 118254184,
        margem_erro: 0.0,
        data_divulgacao: '30/10/2022',
        metodologia: 'Totalização Oficial das Urnas Eletrônicas',
        lula_bruto_pct: 50.90,
        bolso_bruto_pct: 49.10,
        margem_bruta: 1.80,
        erro_placar_bruto: 0.00,
        erro_margem_bruta: 0.00,
        vies_direcional_bruto: 'Ground Truth Oficial',
        lula_m2_pct: 50.90,
        bolso_m2_pct: 49.10,
        margem_m2: 1.80,
        erro_placar_m2: 0.00,
        erro_margem_m2: 0.00,
        reducao_erro_pp: 0.00,
        rmse_estadual_m2: 0.00,
        mae_estadual_m2: 0.00,
        acertos_vencedor_uf_m2: '27/27 (100.0%)',
        is_reference: true,
        rank_label: 'REF'
      },
      {
        id: 'metodo1_rf_urnas',
        instituto: 'Método 1 (RF Out-of-Time + Urnas 1ºT)',
        contratante: 'Modelo Preditivo Autônomo',
        registro_tse: 'OOT 2014-2018 (Sem Entrevistas)',
        amostra: 116591823,
        margem_erro: 0.0,
        data_divulgacao: '29/10/2022',
        metodologia: 'Random Forest OOT + Microdados de Urna',
        lula_bruto_pct: null,
        bolso_bruto_pct: null,
        margem_bruta: null,
        erro_placar_bruto: null,
        erro_margem_bruta: null,
        vies_direcional_bruto: 'Modelo Machine Learning',
        lula_m2_pct: 52.30,
        bolso_m2_pct: 47.70,
        margem_m2: 4.60,
        erro_placar_m2: 1.40,
        erro_margem_m2: 2.80,
        reducao_erro_pp: null,
        rmse_estadual_m2: 1.58,
        mae_estadual_m2: 1.45,
        acertos_vencedor_uf_m2: '26/27 (96.3%)',
        is_reference: true,
        rank_label: 'REF'
      }
    ];

    // Combine and sort polls by erro_placar_m2
    const sortedPolls = [...rawData].sort((a, b) => (Number(a.erro_placar_m2) || 0) - (Number(b.erro_placar_m2) || 0));
    
    // Add ranking and identifiers
    const enrichedPolls = sortedPolls.map((poll, idx) => ({
      ...poll,
      rank: idx + 1,
      rank_label: String(idx + 1),
      is_reference: false,
      lula_bruto_pct: Number(poll.lula_bruto_pct),
      bolso_bruto_pct: Number(poll.bolso_bruto_pct),
      lula_m2_pct: Number(poll.lula_m2_pct),
      bolso_m2_pct: Number(poll.bolso_m2_pct),
      erro_placar_bruto: Number(poll.erro_placar_bruto),
      erro_placar_m2: Number(poll.erro_placar_m2),
      reducao_erro_pp: Number(poll.reducao_erro_pp),
      rmse_estadual_m2: Number(poll.rmse_estadual_m2),
      mae_estadual_m2: Number(poll.mae_estadual_m2)
    }));

    res.json({
      success: true,
      count: enrichedPolls.length,
      ground_truth_tse: {
        lula_pct: 50.90,
        bolso_pct: 49.10,
        margem_pp: 1.80,
        votos_validos_total: 118254184
      },
      references,
      polls: enrichedPolls
    });
  } catch (error) {
    console.error('[API /polls-sabado-2022] Error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Backtest 2022 Detailed Results (27 UFs & Metrics)
 * Reads backtest_2022_results.csv dynamically
 */
app.get('/api/backtest-2022', (req, res) => {
  try {
    const csvPath = path.join(DATA_DIR, 'backtest_2022_results.csv');
    const states = parseCSV(csvPath);

    if (states.length === 0) {
      return res.status(404).json({ success: false, message: 'Backtest data not found.' });
    }

    // Compute Summary Statistics
    let sumRealLula = 0;
    let sumRealBolso = 0;
    let sumM1Lula = 0;
    let sumM1Bolso = 0;
    let sumM2Lula = 0;
    let sumM2Bolso = 0;
    let sumElectorate = 0;

    let sqErrAbstRF = 0;
    let absErrAbstRF = 0;
    let sqErrBolsoM1 = 0;
    let absErrBolsoM1 = 0;
    let sqErrBolsoM2 = 0;
    let absErrBolsoM2 = 0;

    let m1CorrectWinner = 0;
    let m2CorrectWinner = 0;

    states.forEach(s => {
      const el = Number(s.eleitorado_2022) || 0;
      sumElectorate += el;

      const rLula = Number(s.lula_2t_real_votos) || 0;
      const rBolso = Number(s.bolso_2t_real_votos) || 0;
      sumRealLula += rLula;
      sumRealBolso += rBolso;

      const m1Lula = Number(s.lula_m1_votos) || 0;
      const m1Bolso = Number(s.bolso_m1_votos) || 0;
      sumM1Lula += m1Lula;
      sumM1Bolso += m1Bolso;

      const m2Lula = Number(s.lula_m2_votos) || 0;
      const m2Bolso = Number(s.bolso_m2_votos) || 0;
      sumM2Lula += m2Lula;
      sumM2Bolso += m2Bolso;

      // Errors
      const errAbst = Number(s.erro_abst_rf) || 0;
      sqErrAbstRF += errAbst * errAbst;
      absErrAbstRF += Math.abs(errAbst);

      const errM1 = Number(s.erro_pct_bolso_m1) || 0;
      sqErrBolsoM1 += errM1 * errM1;
      absErrBolsoM1 += Math.abs(errM1);

      const errM2 = Number(s.erro_pct_bolso_m2) || 0;
      sqErrBolsoM2 += errM2 * errM2;
      absErrBolsoM2 += Math.abs(errM2);

      // Winner accuracy
      const realWinner = rLula > rBolso ? 'LULA' : 'BOLSO';
      const m1Winner = m1Lula > m1Bolso ? 'LULA' : 'BOLSO';
      const m2Winner = m2Lula > m2Bolso ? 'LULA' : 'BOLSO';

      if (realWinner === m1Winner) m1CorrectWinner++;
      if (realWinner === m2Winner) m2CorrectWinner++;
    });

    const N = states.length;
    const totReal = sumRealLula + sumRealBolso;
    const totM1 = sumM1Lula + sumM1Bolso;
    const totM2 = sumM2Lula + sumM2Bolso;

    const summary = {
      total_electorate: sumElectorate,
      total_valid_real: totReal,
      national_real: {
        lula_pct: Number(((sumRealLula / totReal) * 100).toFixed(2)),
        bolso_pct: Number(((sumRealBolso / totReal) * 100).toFixed(2)),
        lula_votes: sumRealLula,
        bolso_votes: sumRealBolso
      },
      national_method1_rf: {
        lula_pct: Number(((sumM1Lula / totM1) * 100).toFixed(2)),
        bolso_pct: Number(((sumM1Bolso / totM1) * 100).toFixed(2)),
        lula_votes: sumM1Lula,
        bolso_votes: sumM1Bolso,
        erro_placar_pp: Number((Math.abs((sumM1Lula / totM1) * 100 - (sumRealLula / totReal) * 100)).toFixed(2)),
        rmse_estadual: Number(Math.sqrt(sqErrBolsoM1 / N).toFixed(2)),
        mae_estadual: Number((absErrBolsoM1 / N).toFixed(2)),
        acertos_uf: `${m1CorrectWinner}/${N} (${((m1CorrectWinner / N) * 100).toFixed(1)}%)`
      },
      national_method2_atlas: {
        lula_pct: Number(((sumM2Lula / totM2) * 100).toFixed(2)),
        bolso_pct: Number(((sumM2Bolso / totM2) * 100).toFixed(2)),
        lula_votes: sumM2Lula,
        bolso_votes: sumM2Bolso,
        erro_placar_pp: Number((Math.abs((sumM2Lula / totM2) * 100 - (sumRealLula / totReal) * 100)).toFixed(2)),
        rmse_estadual: Number(Math.sqrt(sqErrBolsoM2 / N).toFixed(2)),
        mae_estadual: Number((absErrBolsoM2 / N).toFixed(2)),
        acertos_uf: `${m2CorrectWinner}/${N} (${((m2CorrectWinner / N) * 100).toFixed(1)}%)`
      },
      abstention_rf_metrics: {
        rmse: Number(Math.sqrt(sqErrAbstRF / N).toFixed(2)),
        mae: Number((absErrAbstRF / N).toFixed(2))
      }
    };

    res.json({
      success: true,
      summary,
      states
    });
  } catch (error) {
    console.error('[API /backtest-2022] Error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * 2026 Projections (Method 1 RF Ballot Boxes & Method 2 Atlas Turnout)
 */
app.get('/api/projections-2026', (req, res) => {
  try {
    const rfPath = path.join(DATA_DIR, 'projecao_rf_votos_2026.csv');
    const atlasPath = path.join(DATA_DIR, 'atlas_com_abstencao_2026.csv');
    const polls2026Path = path.join(DATA_DIR, 'pesquisas_vespera_2026_com_abstencao.csv');
    const polls2026UfPath = path.join(DATA_DIR, 'pesquisas_2026_por_uf.csv');

    const rfStates = parseCSV(rfPath);
    const atlasStates = parseCSV(atlasPath);
    const polls2026 = parseCSV(polls2026Path);
    const polls2026ByUf = parseCSV(polls2026UfPath);

    const atlasMap = {};
    atlasStates.forEach(a => {
      atlasMap[a.uf] = a;
    });

    let totM1Flavio = 0;
    let totM1Lula = 0;
    let totM2Flavio = 0;
    let totM2Lula = 0;

    const combinedStates = rfStates.map(r => {
      const a = atlasMap[r.uf] || {};
      const flavioM1 = Number(r.votos_flavio_2t_rf) || 0;
      const lulaM1 = Number(r.votos_lula_2t_rf) || 0;
      const flavioM2 = Number(a.votos_flavio_proj) || 0;
      const lulaM2 = Number(a.votos_lula_proj) || 0;

      totM1Flavio += flavioM1;
      totM1Lula += lulaM1;
      totM2Flavio += flavioM2;
      totM2Lula += lulaM2;

      const margemM1 = Number(r.pct_flavio_2t_rf) - Number(r.pct_lula_2t_rf);
      const pctFlavioM2 = (flavioM2 + lulaM2 > 0) ? (flavioM2 / (flavioM2 + lulaM2)) * 100 : 0;
      const pctLulaM2 = (flavioM2 + lulaM2 > 0) ? (lulaM2 / (flavioM2 + lulaM2)) * 100 : 0;
      const margemM2 = pctFlavioM2 - pctLulaM2;

      return {
        uf: r.uf,
        estado: r.estado,
        regiao: r.regiao,
        teve_2t_gov: r.teve_2t_gov,
        abst_1t: Number(r.abst_1t),
        abst_2t_rf: Number(r.abst_2t_rf),
        delta_rf: Number(r.delta_rf),
        // Method 1 (RF Urnas)
        votos_flavio_m1: flavioM1,
        votos_lula_m1: lulaM1,
        pct_flavio_m1: Number(r.pct_flavio_2t_rf),
        pct_lula_m1: Number(r.pct_lula_2t_rf),
        margem_m1: Number(margemM1.toFixed(2)),
        // Method 2 (Atlas + Abst)
        votos_flavio_m2: flavioM2,
        votos_lula_m2: lulaM2,
        pct_flavio_m2: Number(pctFlavioM2.toFixed(2)),
        pct_lula_m2: Number(pctLulaM2.toFixed(2)),
        margem_m2: Number(margemM2.toFixed(2)),
        diff_margem: Number((margemM1 - margemM2).toFixed(2))
      };
    });

    const totValidM1 = totM1Flavio + totM1Lula;
    const totValidM2 = totM2Flavio + totM2Lula;

    const summary = {
      method1_rf: {
        flavio_pct: Number(((totM1Flavio / totValidM1) * 100).toFixed(2)),
        lula_pct: Number(((totM1Lula / totValidM1) * 100).toFixed(2)),
        flavio_votes: totM1Flavio,
        lula_votes: totM1Lula,
        vantagem_votos: totM1Flavio - totM1Lula,
        vantagem_pp: Number((((totM1Flavio - totM1Lula) / totValidM1) * 100).toFixed(2))
      },
      method2_atlas: {
        flavio_pct: Number(((totM2Flavio / totValidM2) * 100).toFixed(2)),
        lula_pct: Number(((totM2Lula / totValidM2) * 100).toFixed(2)),
        flavio_votes: totM2Flavio,
        lula_votes: totM2Lula,
        vantagem_votos: totM2Flavio - totM2Lula,
        vantagem_pp: Number((((totM2Flavio - totM2Lula) / totValidM2) * 100).toFixed(2))
      }
    };

    res.json({
      success: true,
      summary,
      states: combinedStates,
      polls2026,
      polls2026ByUf
    });
  } catch (error) {
    console.error('[API /projections-2026] Error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Random Forest Coefficients & Feature Importances
 */
app.get('/api/rf-coefficients', (req, res) => {
  try {
    const csvPath = path.join(DATA_DIR, 'rf_state_coefficients.csv');
    const coefs = parseCSV(csvPath);
    res.json({
      success: true,
      count: coefs.length,
      coefficients: coefs
    });
  } catch (error) {
    console.error('[API /rf-coefficients] Error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Fallback to index.html for client-side routing
app.get('*', (req, res) => {
  res.sendFile(path.join(PUBLIC_DIR, 'index.html'));
});

// Start Server
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`[Liquid Glass App] Running smoothly at http://localhost:${PORT}`);
    console.log(`[Data Source] Serving dynamic datasets from: ${DATA_DIR}`);
  });
}

module.exports = app;
