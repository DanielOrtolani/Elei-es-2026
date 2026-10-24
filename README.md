# 🗳️ Inteligência Eleitoral 2026 & Backtest Oficial 2022 • Apple Liquid Glass Web App

Aplicação web interativa em **Node.js + Express + Vanilla JS + Chart.js** (com estética **Apple Liquid Glass / HIG Light**) e dashboard complementar em **Streamlit**, desenvolvida para modelagem quantitativa de abstenção estadual via **Random Forest** e projeção de votos válidos para o 2º turno presidencial de 2026, acompanhada de validação *Out-of-Time* no 2º turno de 2022.

---

## 🚀 Como Executar

### 1. Web App Apple Liquid Glass (Node.js + Express)
```bash
npm install
npm start
```
Acesse em: **`http://localhost:3000`**

### 2. Dashboard Analítico em Streamlit (Opcional)
```bash
uv run --with streamlit,pandas,plotly streamlit run app_dashboard_eleicoes.py --server.port 8501
```
Acesse em: **`http://localhost:8501`**

### 3. Reexecutar os Scripts de Modelagem e Projeção (Python)
```bash
# Aplicar o filtro de abstenção estadual (Random Forest) a todas as pesquisas de véspera de 2026
uv run --with pandas,numpy python scripts/apply_abstention_all_polls_2026.py

# Executar o backtest Out-of-Time de 2022 das pesquisas de sábado de véspera
uv run --with pandas,numpy,scikit-learn python scripts/backtest_polls_2022.py
```

---

## 📂 Estrutura do Repositório

- `server.js` — Servidor Express e API REST (`/api/projections-2026`, `/api/polls-sabado-2022`, `/api/backtest-2022`, `/api/rf-coefficients`)
- `public/` — Front-end Apple Liquid Glass (`index.html`, `css/liquid-glass.css`, `js/app.js`)
- `data/` — Datasets auditados (27 UFs e pesquisas de véspera de 2022 e 2026):
  - `pesquisas_vespera_2026_com_abstencao.csv` — 8 pesquisas de véspera de 2026 ponderadas pela abstenção RF
  - `pesquisas_2026_por_uf.csv` — Detalhamento nas 27 UFs para cada instituto em 2026
  - `projecao_rf_votos_2026.csv` — Projeção autônoma do Método 1 (Random Forest + Urnas 1ºT) para 2026
  - `atlas_com_abstencao_2026.csv` — Projeção da AtlasIntel com filtro de abstenção RF
  - `backtest_2022_results.csv` — Validação *Out-of-Time* nas 27 UFs na eleição de 2022
  - `pesquisas_sabado_2022_comparativo.csv` — Comparativo das 8 pesquisas de sábado (29/10/2022) frente ao TSE
  - `rf_state_coefficients.csv` — Importância de variáveis e valores SHAP por Unidade da Federação
- `scripts/` — Scripts Python de treinamento do modelo Random Forest, backtest de 2022 e ponderação das pesquisas de 2026
- `app_dashboard_eleicoes.py` — Aplicação complementar em Streamlit
- `painel_eleicoes_apple_ui.html` — Versão *standalone* autocontida em arquivo único HTML
