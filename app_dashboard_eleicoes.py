import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(
    page_title="Eleições 2026 & Backtest 2022 | Inteligência Eleitoral",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Apple Human Interface Guidelines (HIG) Fixed Publication Palette (OS-Theme Independent)
BG = "#F5F5F7"              # Apple Signature System Gray 6 Background
BG_SUBTLE = "#EFEFF4"       # Apple Segmented / Header Fill
CARD_BG = "#FFFFFF"         # Pure Crisp White Surface
CARD_HOVER = "#F5F5F7"      # Subtle Row Hover
BORDER = "#E5E5EA"          # Apple System Separator
BORDER_SUBTLE = "#F2F2F7"   # Hairline Row Divider
TEXT = "#1D1D1F"            # Apple Primary Label
TEXT_MUTED = "#515154"      # Apple Secondary Label
TEXT_DIM = "#86868B"        # Apple Tertiary Label

APPLE_BLUE = "#0071E3"
APPLE_BLUE_LIGHT = "#4DA3FF"
APPLE_BLUE_BG = "rgba(0, 113, 227, 0.10)"

APPLE_RED = "#E3242B"
APPLE_RED_BG = "rgba(227, 36, 43, 0.10)"

APPLE_GREEN = "#1D9E34"
APPLE_GREEN_BG = "rgba(29, 158, 52, 0.11)"

APPLE_AMBER = "#D97706"
APPLE_AMBER_BG = "rgba(217, 119, 6, 0.11)"

APPLE_FONT_STACK = '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial, sans-serif'
APPLE_MONO_STACK = '"SF Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace'

css = f"""<style>
:root {{
    color-scheme: light !important;
}}

header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
div[data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
}}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
    background-color: {BG} !important;
    color: {TEXT} !important;
    font-family: {APPLE_FONT_STACK} !important;
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
    color-scheme: light !important;
}}

.block-container {{
    padding: 1.5rem 2.4rem 3.5rem !important;
    max-width: 1440px !important;
}}

/* Lock all Streamlit Widgets & Dropdown Portals to Apple Light Aesthetic regardless of OS Dark Mode */
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span,
.stRadio label, .stRadio p, .stRadio span, .stSelectbox label, .stSelectbox p {{
    color: {TEXT} !important;
    font-family: {APPLE_FONT_STACK} !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: -0.01em !important;
}}

div[data-baseweb="select"] > div {{
    background-color: {CARD_BG} !important;
    color: {TEXT} !important;
    border: 1px solid #D2D2D7 !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
    font-family: {APPLE_FONT_STACK} !important;
}}
div[data-baseweb="select"] span, div[data-baseweb="select"] div, div[data-baseweb="select"] svg {{
    color: {TEXT} !important;
    fill: {TEXT} !important;
}}
div[data-baseweb="popover"], div[data-baseweb="popover"] > div, ul[data-baseweb="menu"], li[role="option"] {{
    background-color: {CARD_BG} !important;
    color: {TEXT} !important;
    font-family: {APPLE_FONT_STACK} !important;
}}
li[role="option"]:hover, li[role="option"][aria-selected="true"] {{
    background-color: {BG} !important;
    color: {APPLE_BLUE} !important;
    font-weight: 600 !important;
}}

/* Apple Segmented Control Tabs */
[data-baseweb="tab-list"] {{
    background: #E8E8ED !important;
    border: 1px solid rgba(0,0,0,0.04) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    margin-bottom: 1.4rem !important;
}}
button[data-baseweb="tab"] {{
    background: transparent !important;
    color: {TEXT_MUTED} !important;
    font-family: {APPLE_FONT_STACK} !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    padding: 0.52rem 1.1rem !important;
    border-radius: 9px !important;
    border: none !important;
    transition: all 0.15s ease !important;
}}
button[data-baseweb="tab"] p, button[data-baseweb="tab"] span, button[data-baseweb="tab"] div {{
    color: {TEXT_MUTED} !important;
    font-family: {APPLE_FONT_STACK} !important;
    font-weight: 600 !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {TEXT} !important;
    background: {CARD_BG} !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04) !important;
}}
button[data-baseweb="tab"][aria-selected="true"] p,
button[data-baseweb="tab"][aria-selected="true"] span,
button[data-baseweb="tab"][aria-selected="true"] div {{
    color: {TEXT} !important;
    font-weight: 700 !important;
}}
div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {{
    display: none !important;
}}

/* Plotly Cards */
[data-testid="stPlotlyChart"] {{
    background: {CARD_BG} !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    border-radius: 16px !important;
    padding: 0.75rem !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.035), 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    margin-bottom: 1.15rem !important;
}}

/* Editorial Header */
.apple-header {{
    background: {CARD_BG};
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 18px;
    padding: 1.35rem 1.65rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.035);
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.brand-eyebrow {{
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {APPLE_BLUE};
    margin-bottom: 0.25rem;
}}
.brand-title {{
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: {TEXT};
    line-height: 1.15;
}}
.brand-sub {{
    font-size: 0.9rem;
    color: {TEXT_MUTED};
    margin-top: 0.3rem;
    letter-spacing: -0.01em;
}}
.brand-pill {{
    background: {BG};
    border: 1px solid {BORDER};
    color: {TEXT_MUTED};
    font-size: 0.76rem;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 999px;
    white-space: nowrap;
}}

/* Apple Bento KPI Cards */
.kpi-card {{
    background: {CARD_BG};
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 16px;
    padding: 1.2rem 1.35rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.035), 0 1px 3px rgba(0, 0, 0, 0.02);
    height: 100%;
}}
.kpi-title {{
    font-size: 0.73rem;
    font-weight: 700;
    color: {TEXT_DIM};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
}}
.kpi-val {{
    font-family: {APPLE_FONT_STACK};
    font-variant-numeric: tabular-nums;
    font-size: 1.7rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.15;
}}
.kpi-sub {{
    font-size: 0.8rem;
    color: {TEXT_MUTED};
    margin-top: 0.45rem;
    line-height: 1.45;
}}

.section-hdr {{
    background: {CARD_BG};
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 14px;
    padding: 0.95rem 1.3rem;
    margin-bottom: 0.65rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.025);
}}
.chart-title {{
    font-size: 1.02rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: {TEXT};
}}
.chart-subtitle {{
    font-size: 0.81rem;
    color: {TEXT_MUTED};
    margin-top: 0.15rem;
}}

/* Apple Table Card */
.tbl-card {{
    background: {CARD_BG};
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 16px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 1.3rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.035);
    overflow-x: auto;
}}
.data-tbl {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.84rem;
    font-family: {APPLE_FONT_STACK};
}}
.data-tbl th {{
    text-align: left;
    padding: 0.7rem 0.85rem;
    color: {TEXT_DIM};
    font-weight: 700;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid {BORDER};
    background: {BG};
}}
.data-tbl td {{
    padding: 0.65rem 0.85rem;
    color: {TEXT};
    border-bottom: 1px solid {BORDER_SUBTLE};
    font-variant-numeric: tabular-nums;
}}
.data-tbl td.mono {{
    font-family: {APPLE_MONO_STACK};
    font-variant-numeric: tabular-nums;
    font-size: 0.81rem;
}}
.data-tbl tr:hover td {{
    background: {CARD_HOVER};
}}

.badge {{
    display: inline-block;
    padding: 3px 9px;
    border-radius: 999px;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    font-variant-numeric: tabular-nums;
}}
.badge-flavio {{
    background: {APPLE_BLUE_BG};
    color: {APPLE_BLUE};
}}
.badge-lula {{
    background: {APPLE_RED_BG};
    color: {APPLE_RED};
}}
.badge-gov {{
    background: {APPLE_GREEN_BG};
    color: {APPLE_GREEN};
}}
.badge-up {{
    background: {APPLE_AMBER_BG};
    color: {APPLE_AMBER};
}}
.badge-down {{
    background: {APPLE_GREEN_BG};
    color: {APPLE_GREEN};
}}
.badge-blue {{
    background: {APPLE_BLUE_BG};
    color: {APPLE_BLUE};
}}
.badge-green {{
    background: {APPLE_GREEN_BG};
    color: {APPLE_GREEN};
}}
.badge-amber {{
    background: {APPLE_AMBER_BG};
    color: {APPLE_AMBER};
}}
.badge-red {{
    background: {APPLE_RED_BG};
    color: {APPLE_RED};
}}
</style>"""
st.markdown(css, unsafe_allow_html=True)

def render_html(raw_html: str):
    cleaned = "\n".join(line.lstrip() for line in raw_html.splitlines() if line.strip() != "")
    st.markdown(cleaned, unsafe_allow_html=True)

@st.cache_data
def load_all_data():
    rf_df = pd.read_csv(r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\projecao_rf_votos_2026.csv")
    atlas_df = pd.read_csv(r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\atlas_com_abstencao_2026.csv")
    
    comp = rf_df[["uf", "estado", "regiao", "teve_2t_gov", "abst_1t", "abst_2t_rf", "delta_rf",
                  "votos_flavio_1t", "votos_lula_1t",
                  "votos_flavio_2t_rf", "pct_flavio_2t_rf", "votos_lula_2t_rf", "pct_lula_2t_rf"]].copy()
    
    comp = comp.merge(
        atlas_df[["uf", "validos_proj", "pct_flavio_atlas", "pct_lula_atlas", 
                  "votos_flavio_proj", "votos_lula_proj"]],
        on="uf"
    )
    
    comp["margem_rf"] = (comp["pct_flavio_2t_rf"] - comp["pct_lula_2t_rf"]).round(1)
    comp["margem_atlas"] = (comp["pct_flavio_atlas"] - comp["pct_lula_atlas"]).round(1)
    comp["diff_margem"] = (comp["margem_rf"] - comp["margem_atlas"]).round(1)
    
    hist_json_path = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\abstencao_completa.json"
    with open(hist_json_path, "r", encoding="utf-8") as f:
        hist_raw = json.load(f)
        
    hist_rows = []
    for estado, vals in hist_raw.items():
        matching = comp[comp["estado"] == estado]
        uf_code = matching["uf"].values[0] if len(matching) > 0 else estado
        regiao = matching["regiao"].values[0] if len(matching) > 0 else "-"
        abst_26_1t = matching["abst_1t"].values[0] if len(matching) > 0 else 0.0
        abst_26_2t = matching["abst_2t_rf"].values[0] if len(matching) > 0 else 0.0
        
        def to_flt(s):
            try:
                return float(str(s).replace("%", "").replace(",", ".").strip())
            except Exception:
                return np.nan
        
        hist_rows.append({
            "uf": uf_code,
            "estado": estado,
            "regiao": regiao,
            "2014_t1": vals.get("2014_t1", "-"),
            "2014_t2": vals.get("2014_t2", "-"),
            "2018_t1": vals.get("2018_t1", "-"),
            "2018_t2": vals.get("2018_t2", "-"),
            "2022_t1": vals.get("2022_t1", "-"),
            "2022_t2": vals.get("2022_t2", "-"),
            "2022_t2_num": to_flt(vals.get("2022_t2", "0")),
            "2026_t1": f"{abst_26_1t:.2f}%",
            "2026_t2_proj": f"{abst_26_2t:.2f}%",
            "2026_t2_num": abst_26_2t
        })
    hist_df = pd.DataFrame(hist_rows).sort_values(by="estado")
    
    coef_path = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\rf_state_coefficients.csv"
    coef_df = pd.read_csv(coef_path)
    
    bt_path = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\backtest_2022_results.csv"
    bt_df = pd.read_csv(bt_path)
    
    return comp, hist_df, coef_df, bt_df

df, hist_df, coef_df, bt_df = load_all_data()

@st.cache_data
def load_polls_2022():
    polls_path = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\pesquisas_sabado_2022_comparativo.csv"
    if os.path.exists(polls_path):
        try:
            df_p = pd.read_csv(polls_path, encoding="utf-8")
            if "\ufffd" in "".join(df_p["instituto"].values):
                df_p = pd.read_csv(polls_path, encoding="latin1")
        except Exception:
            df_p = pd.read_csv(polls_path, encoding="latin1")
    else:
        df_p = pd.DataFrame([
            {"instituto": "Genial/Quaest", "contratante": "Banco Genial", "registro_tse": "BR-05765/2022", "amostra": 2000, "margem_erro": 2.0, "data_divulgacao": "29/10/2022", "metodologia": "Presencial", "lula_bruto_pct": 52.0, "bolso_bruto_pct": 48.0, "margem_bruta": 4.0, "erro_placar_bruto": 1.10, "erro_margem_bruta": 2.20, "vies_direcional_bruto": "Superestimou Lula", "lula_m2_pct": 50.93, "bolso_m2_pct": 49.07, "margem_m2": 1.86, "erro_placar_m2": 0.03, "erro_margem_m2": 0.06, "reducao_erro_pp": 1.07, "rmse_estadual_m2": 5.25, "mae_estadual_m2": 4.61, "acertos_vencedor_uf_m2": "25/27 (92.6%)"},
            {"instituto": "CNT/MDA", "contratante": "Confederação Nacional do Transporte (CNT)", "registro_tse": "BR-01820/2022", "amostra": 2002, "margem_erro": 2.2, "data_divulgacao": "29/10/2022", "metodologia": "Presencial", "lula_bruto_pct": 51.1, "bolso_bruto_pct": 48.9, "margem_bruta": 2.2, "erro_placar_bruto": 0.20, "erro_margem_bruta": 0.40, "vies_direcional_bruto": "Superestimou Lula", "lula_m2_pct": 49.99, "bolso_m2_pct": 50.01, "margem_m2": -0.02, "erro_placar_m2": 0.91, "erro_margem_m2": -1.82, "reducao_erro_pp": -0.71, "rmse_estadual_m2": 1.38, "mae_estadual_m2": 1.27, "acertos_vencedor_uf_m2": "25/27 (92.6%)"},
            {"instituto": "Ipec", "contratante": "TV Globo", "registro_tse": "BR-05256/2022", "amostra": 4272, "margem_erro": 2.0, "data_divulgacao": "29/10/2022", "metodologia": "Presencial", "lula_bruto_pct": 54.0, "bolso_bruto_pct": 46.0, "margem_bruta": 8.0, "erro_placar_bruto": 3.10, "erro_margem_bruta": 6.20, "vies_direcional_bruto": "Superestimou Lula", "lula_m2_pct": 52.10, "bolso_m2_pct": 47.90, "margem_m2": 4.20, "erro_placar_m2": 1.20, "erro_margem_m2": 2.40, "reducao_erro_pp": 1.90, "rmse_estadual_m2": 1.10, "mae_estadual_m2": 0.88, "acertos_vencedor_uf_m2": "27/27 (100.0%)"},
            {"instituto": "Datafolha", "contratante": "Folha de S.Paulo / TV Globo", "registro_tse": "BR-08297/2022", "amostra": 8308, "margem_erro": 2.0, "data_divulgacao": "29/10/2022", "metodologia": "Presencial", "lula_bruto_pct": 52.0, "bolso_bruto_pct": 48.0, "margem_bruta": 4.0, "erro_placar_bruto": 1.10, "erro_margem_bruta": 2.20, "vies_direcional_bruto": "Superestimou Lula", "lula_m2_pct": 52.53, "bolso_m2_pct": 47.47, "margem_m2": 5.06, "erro_placar_m2": 1.63, "erro_margem_m2": 3.26, "reducao_erro_pp": -0.53, "rmse_estadual_m2": 1.78, "mae_estadual_m2": 1.62, "acertos_vencedor_uf_m2": "26/27 (96.3%)"},
            {"instituto": "Paraná Pesquisas", "contratante": "Recursos próprios / BGC Liquidez", "registro_tse": "BR-09573/2022", "amostra": 2400, "margem_erro": 2.0, "data_divulgacao": "29/10/2022", "metodologia": "Presencial", "lula_bruto_pct": 50.4, "bolso_bruto_pct": 49.6, "margem_bruta": 0.8, "erro_placar_bruto": 0.50, "erro_margem_bruta": -1.00, "vies_direcional_bruto": "Superestimou Bolsonaro", "lula_m2_pct": 49.18, "bolso_m2_pct": 50.82, "margem_m2": -1.64, "erro_placar_m2": 1.72, "erro_margem_m2": -3.44, "reducao_erro_pp": -1.22, "rmse_estadual_m2": 2.82, "mae_estadual_m2": 2.53, "acertos_vencedor_uf_m2": "24/27 (88.9%)"},
            {"instituto": "AtlasIntel", "contratante": "Recursos próprios", "registro_tse": "BR-04838/2022", "amostra": 7500, "margem_erro": 1.0, "data_divulgacao": "29/10/2022", "metodologia": "Digital (RDR)", "lula_bruto_pct": 53.4, "bolso_bruto_pct": 46.6, "margem_bruta": 6.8, "erro_placar_bruto": 2.50, "erro_margem_bruta": 5.00, "vies_direcional_bruto": "Superestimou Lula", "lula_m2_pct": 53.21, "bolso_m2_pct": 46.79, "margem_m2": 6.42, "erro_placar_m2": 2.31, "erro_margem_m2": 4.62, "reducao_erro_pp": 0.19, "rmse_estadual_m2": 2.02, "mae_estadual_m2": 1.91, "acertos_vencedor_uf_m2": "26/27 (96.3%)"},
            {"instituto": "Modalmais/Futura", "contratante": "Banco Modal (Modalmais)", "registro_tse": "BR-07903/2022", "amostra": 2000, "margem_erro": 2.2, "data_divulgacao": "28/10/2022", "metodologia": "Telefone (CATI)", "lula_bruto_pct": 49.7, "bolso_bruto_pct": 50.3, "margem_bruta": -0.6, "erro_placar_bruto": 1.20, "erro_margem_bruta": -2.40, "vies_direcional_bruto": "Superestimou Bolsonaro", "lula_m2_pct": 48.29, "bolso_m2_pct": 51.71, "margem_m2": -3.42, "erro_placar_m2": 2.61, "erro_margem_m2": -5.22, "reducao_erro_pp": -1.41, "rmse_estadual_m2": 3.97, "mae_estadual_m2": 3.71, "acertos_vencedor_uf_m2": "23/27 (85.2%)"},
            {"instituto": "Instituto Veritá", "contratante": "Recursos próprios", "registro_tse": "BR-04920/2022", "amostra": 30180, "margem_erro": 2.0, "data_divulgacao": "28/10/2022", "metodologia": "Eletrônica/Digital", "lula_bruto_pct": 48.5, "bolso_bruto_pct": 51.5, "margem_bruta": -3.0, "erro_placar_bruto": 2.40, "erro_margem_bruta": -4.80, "vies_direcional_bruto": "Superestimou Bolsonaro", "lula_m2_pct": 46.97, "bolso_m2_pct": 53.03, "margem_m2": -6.06, "erro_placar_m2": 3.93, "erro_margem_m2": -7.86, "reducao_erro_pp": -1.53, "rmse_estadual_m2": 4.18, "mae_estadual_m2": 4.04, "acertos_vencedor_uf_m2": "24/27 (88.9%)"}
        ])
    return df_p

polls_df = load_polls_2022()

tot_rf_f = df["votos_flavio_2t_rf"].sum()
tot_rf_l = df["votos_lula_2t_rf"].sum()
tot_rf_v = tot_rf_f + tot_rf_l
pct_rf_f = tot_rf_f / tot_rf_v * 100
pct_rf_l = tot_rf_l / tot_rf_v * 100

tot_at_f = df["votos_flavio_proj"].sum()
tot_at_l = df["votos_lula_proj"].sum()
tot_at_v = tot_at_f + tot_at_l
pct_at_f = tot_at_f / tot_at_v * 100
pct_at_l = tot_at_l / tot_at_v * 100

def make_layout(**kwargs):
    base = dict(
        template="plotly_white",
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(family=APPLE_FONT_STACK, color=TEXT, size=12),
        margin=dict(l=15, r=20, t=25, b=20),
        xaxis=dict(
            gridcolor="#EBEBF0",
            zerolinecolor="#86868B",
            zerolinewidth=1.2,
            tickfont=dict(family=APPLE_FONT_STACK, size=11, color=TEXT)
        ),
        yaxis=dict(
            gridcolor="#F2F2F7",
            zerolinecolor="#EBEBF0",
            tickfont=dict(family=APPLE_FONT_STACK, size=11, color=TEXT)
        )
    )
    base.update(kwargs)
    return base

# Header
render_html("""
<div class="apple-header">
    <div>
        <div class="brand-eyebrow">Inteligência Eleitoral • Modelagem Quantitativa & Validação Out-of-Time</div>
        <div class="brand-title">Projeções Presidenciais 2026 & Backtest Oficial 2022</div>
        <div class="brand-sub">
            Análise comparativa entre o <b>Método 1 (Random Forest + Microdados de Urna 1ºT)</b> e o <b>Método 2 (AtlasIntel Ponderada por Abstenção)</b>
        </div>
    </div>
    <div class="brand-pill">27 Unidades da Federação • TSE & AtlasIntel</div>
</div>
""")

# Placar Nacional (100% Stacked Bar)
render_html("""
<div class="section-hdr">
    <div class="chart-title">Termômetro da Disputa Nacional 2026: Placar de Votos Válidos</div>
    <div class="chart-subtitle">Proporção nacional projetada de votos válidos com linha de maioria absoluta (50,0%)</div>
</div>
""")

placar_fig = go.Figure()
placar_fig.add_trace(go.Bar(
    y=["Método 1: Random Forest (Urnas)", "Método 2: AtlasIntel + Abstenção"],
    x=[pct_rf_f, pct_at_f],
    name="Flávio Bolsonaro",
    orientation="h",
    marker=dict(color=APPLE_BLUE),
    text=[
        f"Flávio Bolsonaro: {pct_rf_f:.2f}% ({tot_rf_f:,.0f} votos)".replace(",", "."),
        f"Flávio Bolsonaro: {pct_at_f:.2f}% ({tot_at_f:,.0f} votos)".replace(",", ".")
    ],
    textposition="inside",
    insidetextanchor="middle",
    textfont=dict(color="#ffffff", size=13, family=APPLE_FONT_STACK, weight=700)
))
placar_fig.add_trace(go.Bar(
    y=["Método 1: Random Forest (Urnas)", "Método 2: AtlasIntel + Abstenção"],
    x=[pct_rf_l, pct_at_l],
    name="Lula",
    orientation="h",
    marker=dict(color=APPLE_RED),
    text=[
        f"Lula: {pct_rf_l:.2f}% ({tot_rf_l:,.0f} votos)".replace(",", "."),
        f"Lula: {pct_at_l:.2f}% ({tot_at_l:,.0f} votos)".replace(",", ".")
    ],
    textposition="inside",
    insidetextanchor="middle",
    textfont=dict(color="#ffffff", size=13, family=APPLE_FONT_STACK, weight=700)
))
placar_fig.add_vline(
    x=50, line_width=2, line_dash="dash", line_color=TEXT,
    annotation_text="50% Maioria Absoluta", annotation_position="top",
    annotation_font=dict(size=11, color=TEXT, family=APPLE_FONT_STACK, weight=700)
)
placar_fig.update_layout(make_layout(
    barmode="stack",
    height=165,
    margin=dict(l=215, r=20, t=28, b=12),
    xaxis=dict(range=[0, 100], showticklabels=False, showgrid=False),
    yaxis=dict(autorange="reversed", tickfont=dict(size=12, color=TEXT, weight=700)),
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, font=dict(color=TEXT, size=11))
))
st.plotly_chart(placar_fig, use_container_width=True, theme=None, config={"displayModeBar": False})

# KPI Row
k1, k2, k3, k4 = st.columns(4)
with k1:
    render_html(f"""
    <div class="kpi-card">
        <div class="kpi-title">Vantagem Método 1 (ML Urnas)</div>
        <div class="kpi-val" style="color:{APPLE_BLUE};">+4.564.117</div>
        <div class="kpi-sub">Votos de vantagem para Flávio (<b>+3,80 p.p.</b>). Cristalização forte de centro-direita (Zema/Caiado).</div>
    </div>
    """)
with k2:
    render_html(f"""
    <div class="kpi-card">
        <div class="kpi-title">Vantagem Método 2 (AtlasIntel)</div>
        <div class="kpi-val" style="color:{APPLE_BLUE};">+2.856.493</div>
        <div class="kpi-sub">Votos de vantagem para Flávio (<b>+2,34 p.p.</b>). Margem encolhe em <b>1,71 mi</b> com empate em MG.</div>
    </div>
    """)
with k3:
    render_html(f"""
    <div class="kpi-card">
        <div class="kpi-title">Impacto da Abstenção na Pesquisa</div>
        <div class="kpi-val" style="color:{APPLE_RED};">+418.564</div>
        <div class="kpi-sub">Votos líquidos adicionados para Lula pela <b>menor abstenção do Nordeste</b> (16–18% vs 23% no Sudeste).</div>
    </div>
    """)
with k4:
    render_html(f"""
    <div class="kpi-card">
        <div class="kpi-title">Backtest 2022 (Validação Cega)</div>
        <div class="kpi-val" style="color:{APPLE_GREEN};">RMSE 1,58 p.p.</div>
        <div class="kpi-sub">No teste cego de 2022, o Método 1 teve erro <b>31% menor</b> que a pesquisa bruta, e o Método 2 acertou <b>27/27 UFs</b>.</div>
    </div>
    """)

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# All Interactive Tabs
tab_bars, tab_compare, tab_history, tab_coefs, tab_method, tab_backtest = st.tabs([
    "📊 Margens & Regiões (2026)",
    "📋 Projeções por Estado (27 UFs)",
    "📈 Histórico de Abstenção (2014–2026)",
    "🧠 Coeficientes Estaduais (Random Forest)",
    "🔬 Metodologia & Diagnóstico",
    "⏪ Backtest 2022 (Real vs. Pesquisa vs. Métodos)"
])

# ----------------- TAB 1: GRÁFICOS DE BARRA -----------------
with tab_bars:
    col_c1, col_c2 = st.columns([7, 5])
    
    with col_c1:
        render_html("""
        <div class="section-hdr">
            <div class="chart-title">Margem Divergente por Estado (% de Votos Válidos)</div>
            <div class="chart-subtitle">Barras azuis à direita indicam vantagem de Flávio; barras vermelhas à esquerda indicam vantagem de Lula</div>
        </div>
        """)
        
        metodo_escolhido = st.radio(
            "Selecione o Método de Projeção:",
            ["Método 1: Random Forest (ML de Urnas)", "Método 2: AtlasIntel + Abstenção"],
            horizontal=True,
            key="radio_tab1"
        )
        
        margem_col = "margem_rf" if "Random Forest" in metodo_escolhido else "margem_atlas"
        sorted_states = df.sort_values(by=margem_col, ascending=True)
        bar_colors = [APPLE_BLUE if m > 0 else APPLE_RED for m in sorted_states[margem_col]]
        
        fig_div = go.Figure()
        fig_div.add_trace(go.Bar(
            y=sorted_states["uf"] + " - " + sorted_states["estado"],
            x=sorted_states[margem_col],
            orientation="h",
            marker=dict(color=bar_colors),
            text=[f"{m:+.1f}%" for m in sorted_states[margem_col]],
            textposition="outside",
            textfont=dict(color=TEXT, size=11, family=APPLE_FONT_STACK, weight=600),
            hovertemplate="<b>%{y}</b><br>Margem: %{x:+.1f} p.p.<extra></extra>"
        ))
        fig_div.update_layout(make_layout(
            height=700,
            xaxis=dict(title="Margem de Vitória (p.p.)", range=[-55, 60], tickfont=dict(color=TEXT, size=11)),
            yaxis=dict(tickfont=dict(size=11, color=TEXT, weight=600)),
            margin=dict(l=155, r=55, t=15, b=35)
        ))
        st.plotly_chart(fig_div, use_container_width=True, theme=None, config={"displayModeBar": False})

    with col_c2:
        render_html("""
        <div class="section-hdr">
            <div class="chart-title">Volume de Votos Válidos por Região (Milhões)</div>
            <div class="chart-subtitle">Confronto direto do volume de votos em cada macrorregião</div>
        </div>
        """)
        
        reg_df = df.groupby("regiao", as_index=False).agg({
            "votos_flavio_2t_rf": "sum",
            "votos_lula_2t_rf": "sum"
        })
        fig_reg = go.Figure()
        fig_reg.add_trace(go.Bar(
            x=reg_df["regiao"],
            y=reg_df["votos_flavio_2t_rf"] / 1e6,
            name="Flávio Bolsonaro",
            marker_color=APPLE_BLUE,
            text=[f"{v/1e6:.1f}M" for v in reg_df["votos_flavio_2t_rf"]],
            textposition="outside",
            textfont=dict(color=TEXT, size=11, weight=600)
        ))
        fig_reg.add_trace(go.Bar(
            x=reg_df["regiao"],
            y=reg_df["votos_lula_2t_rf"] / 1e6,
            name="Lula",
            marker_color=APPLE_RED,
            text=[f"{v/1e6:.1f}M" for v in reg_df["votos_lula_2t_rf"]],
            textposition="outside",
            textfont=dict(color=TEXT, size=11, weight=600)
        ))
        fig_reg.update_layout(make_layout(
            barmode="group",
            height=330,
            yaxis=dict(title="Milhões de Votos", range=[0, 32], tickfont=dict(color=TEXT)),
            xaxis=dict(tickfont=dict(color=TEXT, size=11, weight=600)),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=TEXT))
        ))
        st.plotly_chart(fig_reg, use_container_width=True, theme=None, config={"displayModeBar": False})

        render_html("""
        <div class="section-hdr">
            <div class="chart-title">Onde os Métodos Mais Divergem? (Top 10 UFs)</div>
            <div class="chart-subtitle">Diferença em pontos percentuais (Margem RF menos Margem AtlasIntel)</div>
        </div>
        """)
        
        df_div_top = df.copy()
        df_div_top["abs_diff"] = df_div_top["diff_margem"].abs()
        df_div_top = df_div_top.sort_values(by="abs_diff", ascending=False).head(10)
        
        fig_gap = go.Figure()
        fig_gap.add_trace(go.Bar(
            x=df_div_top["uf"],
            y=df_div_top["diff_margem"],
            marker_color=[APPLE_BLUE if v > 0 else APPLE_RED for v in df_div_top["diff_margem"]],
            text=[f"{v:+.1f} p.p." for v in df_div_top["diff_margem"]],
            textposition="outside",
            textfont=dict(color=TEXT, size=11, weight=600)
        ))
        fig_gap.update_layout(make_layout(
            height=300,
            xaxis=dict(title="Estado (UF)", tickfont=dict(color=TEXT, size=11, weight=600)),
            yaxis=dict(title="Diferença (p.p.)", range=[-3, 10], tickfont=dict(color=TEXT)),
            margin=dict(l=40, r=20, t=25, b=35)
        ))
        st.plotly_chart(fig_gap, use_container_width=True, theme=None, config={"displayModeBar": False})

    # Tabela Consolidada: 5 Pesquisas Elegíveis de Hoje (24/10/2026) com Coeficiente por Estado & Impacto 2ºT Gov
    polls_2026_path = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\pesquisas_vespera_2026_com_abstencao.csv"
    if os.path.exists(polls_2026_path):
        df_p26 = pd.read_csv(polls_2026_path, encoding="utf-8")
        render_html("""
        <div class="section-hdr" style="margin-top: 12px;">
            <div class="chart-title">5 Pesquisas Elegíveis (24/10/2026) c/ Coeficiente por Estado & Impacto do 2º Turno para Governador</div>
            <div class="chart-subtitle">Apenas institutos onde foi possível aplicar os coeficientes por UF (rf_state_coefficients.csv) e isolar o efeito das 6 UFs COM 2ºT Gov (AC, AM, DF, ES, RN, TO) vs. 21 UFs SEM 2ºT Gov</div>
        </div>
        """)
        rows_26 = ""
        for _, p in df_p26.iterrows():
            vf = f"{int(p['votos_flavio_abst_rf']):,}".replace(",", ".")
            vl = f"{int(p['votos_lula_abst_rf']):,}".replace(",", ".")
            vant = f"+{int(p['vantagem_flavio_abst_rf_votos']):,} (+{p['vantagem_flavio_abst_rf_pp']:.2f} p.p.)".replace(",", ".")
            s6 = f"+{int(p.get('saldo_flavio_6ufs_com_2t_gov', 320941)):,} Flávio".replace(",", ".")
            ef_gov = f"+{int(p.get('efeito_2t_gov_flavio_votos', 191030)):,} Flávio (+{float(p.get('efeito_2t_gov_flavio_pp', 0.16)):.2f} p.p.)".replace(",", ".")
            rows_26 += f"""
            <tr>
                <td><b>{p['instituto']}</b> <span style="color:{TEXT_DIM};font-size:0.75rem;">({p['data_divulgacao']})</span></td>
                <td>{p['registro_tse']} (N={int(p['amostra']):,})</td>
                <td><span class="badge badge-blue">{p['metodologia']}</span></td>
                <td><b style="color:{APPLE_BLUE};">{p['flavio_headline_valid']:.1f}%</b> x <b style="color:{APPLE_RED};">{p['lula_headline_valid']:.1f}%</b></td>
                <td><b style="color:{APPLE_BLUE};">{p['pct_flavio_abst_rf']:.2f}%</b> x <b style="color:{APPLE_RED};">{p['pct_lula_abst_rf']:.2f}%</b></td>
                <td style="color:{APPLE_BLUE};font-weight:700;">{vf}</td>
                <td style="color:{APPLE_RED};font-weight:700;">{vl}</td>
                <td><span class="badge badge-flavio">{vant}</span></td>
                <td><span class="badge badge-blue">{s6}</span></td>
                <td><span class="badge badge-gov">{ef_gov}</span></td>
            </tr>
            """
        rows_26 += f"""
        <tr style="background:rgba(29, 158, 52, 0.08);font-weight:700;">
            <td><b style="color:{APPLE_GREEN};">MÉDIA / CONSENSO (5 Institutos Elegíveis)</b></td>
            <td>CONSENSO 24/10 (N=19.608)</td>
            <td><span class="badge badge-green">Ensemble 5 Elegíveis</span></td>
            <td><b style="color:{APPLE_BLUE};">50,98%</b> x <b style="color:{APPLE_RED};">49,02%</b></td>
            <td><b style="color:{APPLE_BLUE};">50,91%</b> x <b style="color:{APPLE_RED};">49,09%</b></td>
            <td style="color:{APPLE_BLUE};font-weight:700;">62.045.321</td>
            <td style="color:{APPLE_RED};font-weight:700;">59.827.710</td>
            <td><span class="badge badge-gov">+2.217.611 (+1,82 p.p.)</span></td>
            <td><span class="badge badge-blue">+320.941 Flávio</span></td>
            <td><span class="badge badge-gov">+191.030 Flávio (+0,16 p.p.)</span></td>
        </tr>
        """
        render_html(f"""
        <div class="table-wrap">
            <table class="custom-table">
                <thead>
                    <tr>
                        <th>Instituto</th>
                        <th>Registro TSE & Amostra</th>
                        <th>Metodologia</th>
                        <th>Placar Bruto (F x L)</th>
                        <th>Com Coef. UF + 2ºT Gov</th>
                        <th>Votos Flávio (RF)</th>
                        <th>Votos Lula (RF)</th>
                        <th>Vantagem Flávio (Total)</th>
                        <th>Saldo 6 UFs COM 2ºT Gov</th>
                        <th>Efeito Isolado 2ºT Gov</th>
                    </tr>
                </thead>
                <tbody>{rows_26}</tbody>
            </table>
        </div>
        """)

# ----------------- TAB 2: PROJEÇÕES POR ESTADO (GRÁFICO + TABELA) -----------------
with tab_compare:
    f_c1, f_c2, f_c3 = st.columns([3, 3, 4])
    with f_c1:
        f_reg = st.selectbox("Filtrar por Região:", ["Todas", "Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"], key="f_reg_p")
    with f_c2:
        f_gov = st.selectbox("2º Turno para Governador:", ["Todos", "Apenas COM 2ºT Gov (6 UFs)", "Apenas SEM 2ºT Gov (21 UFs)"], key="f_gov_p")
    with f_c3:
        f_lead = st.selectbox("Liderança no Estado:", ["Todos os Estados", "Apenas onde Flávio lidera", "Apenas onde Lula lidera"], key="f_lead_p")

    sub_df = df.copy()
    if f_reg != "Todas":
        sub_df = sub_df[sub_df["regiao"] == f_reg]
    if f_gov == "Apenas COM 2ºT Gov (6 UFs)":
        sub_df = sub_df[sub_df["teve_2t_gov"] == "Sim"]
    elif f_gov == "Apenas SEM 2ºT Gov (21 UFs)":
        sub_df = sub_df[sub_df["teve_2t_gov"] == "Não"]
    if f_lead == "Apenas onde Flávio lidera":
        sub_df = sub_df[sub_df["margem_rf"] > 0]
    elif f_lead == "Apenas onde Lula lidera":
        sub_df = sub_df[sub_df["margem_rf"] < 0]

    render_html(f"""
    <div class="section-hdr">
        <div class="chart-title">Comparativo de Percentual de Votos Válidos por Estado ({len(sub_df)} UFs selecionadas)</div>
        <div class="chart-subtitle">Comparação visual lado a lado entre Flávio Bolsonaro (% RF vs % Atlas) e Lula (% RF)</div>
    </div>
    """)

    sub_chart_df = sub_df.sort_values(by="pct_flavio_2t_rf", ascending=False)
    fig_t2 = go.Figure()
    fig_t2.add_trace(go.Bar(
        x=sub_chart_df["uf"],
        y=sub_chart_df["pct_flavio_2t_rf"],
        name="Flávio (Método 1: RF)",
        marker_color=APPLE_BLUE,
        text=[f"{v:.1f}%" for v in sub_chart_df["pct_flavio_2t_rf"]],
        textposition="outside",
        textfont=dict(size=10, color=TEXT)
    ))
    fig_t2.add_trace(go.Bar(
        x=sub_chart_df["uf"],
        y=sub_chart_df["pct_flavio_atlas"],
        name="Flávio (Método 2: Atlas)",
        marker_color=APPLE_BLUE_LIGHT,
        text=[f"{v:.1f}%" for v in sub_chart_df["pct_flavio_atlas"]],
        textposition="outside",
        textfont=dict(size=10, color=TEXT)
    ))
    fig_t2.add_trace(go.Bar(
        x=sub_chart_df["uf"],
        y=sub_chart_df["pct_lula_2t_rf"],
        name="Lula (Método 1: RF)",
        marker_color=APPLE_RED,
        text=[f"{v:.1f}%" for v in sub_chart_df["pct_lula_2t_rf"]],
        textposition="outside",
        textfont=dict(size=10, color=TEXT)
    ))
    fig_t2.add_hline(y=50, line_dash="dash", line_color=TEXT_DIM, line_width=1.5)
    fig_t2.update_layout(make_layout(
        barmode="group",
        height=340,
        xaxis=dict(title="Unidade da Federação (UF)", tickfont=dict(color=TEXT, size=11, weight=700)),
        yaxis=dict(title="% de Votos Válidos", range=[0, 88], tickfont=dict(color=TEXT)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color=TEXT, size=11))
    ))
    st.plotly_chart(fig_t2, use_container_width=True, theme=None, config={"displayModeBar": False})

    rows_list = []
    for _, r in sub_df.sort_values(by="votos_flavio_2t_rf", ascending=False).iterrows():
        b_gov = '<span class="badge badge-gov">Sim (2ºT)</span>' if r["teve_2t_gov"] == "Sim" else '<span style="color:#86868B;">Não</span>'
        m_rf_class = "badge-flavio" if r["margem_rf"] > 0 else "badge-lula"
        m_at_class = "badge-flavio" if r["margem_atlas"] > 0 else "badge-lula"
        vf_rf = f"{r['votos_flavio_2t_rf']:,.0f}".replace(",", ".")
        vl_rf = f"{r['votos_lula_2t_rf']:,.0f}".replace(",", ".")
        vf_at = f"{r['votos_flavio_proj']:,.0f}".replace(",", ".")
        vl_at = f"{r['votos_lula_proj']:,.0f}".replace(",", ".")
        rows_list.append(
            f"<tr>"
            f"<td><b>{r['uf']}</b> - {r['estado']}</td>"
            f"<td>{b_gov}</td>"
            f"<td class='mono'>{r['abst_2t_rf']:.2f}%</td>"
            f"<td class='mono'><b>{r['pct_flavio_2t_rf']:.1f}%</b> ({vf_rf})</td>"
            f"<td class='mono'><b>{r['pct_lula_2t_rf']:.1f}%</b> ({vl_rf})</td>"
            f"<td><span class='badge {m_rf_class}'>{r['margem_rf']:+.1f}%</span></td>"
            f"<td class='mono'><b>{r['pct_flavio_atlas']:.1f}%</b> ({vf_at})</td>"
            f"<td class='mono'><b>{r['pct_lula_atlas']:.1f}%</b> ({vl_at})</td>"
            f"<td><span class='badge {m_at_class}'>{r['margem_atlas']:+.1f}%</span></td>"
            f"</tr>"
        )

    render_html(f"""
    <div class="tbl-card">
        <div class="chart-title">Tabela Comparativa de Votos e Projeções do 2º Turno (Exibindo {len(sub_df)} de 27 UFs)</div>
        <div class="chart-subtitle" style="margin-bottom:0.8rem;">Comparativo detalhado lado a lado dos dois métodos para cada unidade da federação</div>
        <table class="data-tbl">
            <thead>
                <tr>
                    <th>Estado (UF)</th>
                    <th>2ºT Gov?</th>
                    <th>Abstenção 2ºT</th>
                    <th>Flávio (Random Forest)</th>
                    <th>Lula (Random Forest)</th>
                    <th>Margem (RF)</th>
                    <th>Flávio (AtlasIntel)</th>
                    <th>Lula (AtlasIntel)</th>
                    <th>Margem (Atlas)</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows_list)}
            </tbody>
        </table>
    </div>
    """)

# ----------------- TAB 3: HISTÓRICO DE ABSTENÇÃO -----------------
with tab_history:
    h_filter = st.selectbox("Filtrar Histórico por Região Geográfica:", ["Todas", "Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"], key="h_reg")
    h_df = hist_df.copy()
    if h_filter != "Todas":
        h_df = h_df[h_df["regiao"] == h_filter]

    render_html("""
    <div class="section-hdr">
        <div class="chart-title">Abstenção no 2º Turno por Estado: 2022 (Real TSE) vs. 2026 (Projeção RF)</div>
        <div class="chart-subtitle">Comparação visual da taxa de abstenção estadual no 2º turno</div>
    </div>
    """)

    h_sort = h_df.sort_values(by="2026_t2_num", ascending=False)
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Bar(
        x=h_sort["uf"],
        y=h_sort["2022_t2_num"],
        name="2022 (2º Turno Real TSE)",
        marker_color="#86868B",
        text=[f"{v:.1f}%" for v in h_sort["2022_t2_num"]],
        textposition="outside",
        textfont=dict(size=10, color=TEXT)
    ))
    fig_hist.add_trace(go.Bar(
        x=h_sort["uf"],
        y=h_sort["2026_t2_num"],
        name="2026 (2º Turno Projetado RF)",
        marker_color=APPLE_BLUE,
        text=[f"{v:.1f}%" for v in h_sort["2026_t2_num"]],
        textposition="outside",
        textfont=dict(size=10, color=TEXT)
    ))
    fig_hist.update_layout(make_layout(
        barmode="group",
        height=330,
        xaxis=dict(title="Estado (UF)", tickfont=dict(color=TEXT, size=11, weight=700)),
        yaxis=dict(title="Abstenção (%)", range=[0, 33], tickfont=dict(color=TEXT)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color=TEXT))
    ))
    st.plotly_chart(fig_hist, use_container_width=True, theme=None, config={"displayModeBar": False})

    h_rows_list = []
    for _, r in h_df.iterrows():
        h_rows_list.append(
            f"<tr>"
            f"<td><b>{r['uf']}</b> - {r['estado']}</td>"
            f"<td>{r['regiao']}</td>"
            f"<td class='mono'>{r['2014_t1']}</td>"
            f"<td class='mono'>{r['2014_t2']}</td>"
            f"<td class='mono'>{r['2018_t1']}</td>"
            f"<td class='mono'>{r['2018_t2']}</td>"
            f"<td class='mono'>{r['2022_t1']}</td>"
            f"<td class='mono'>{r['2022_t2']}</td>"
            f"<td class='mono' style='font-weight:700;'>{r['2026_t1']}</td>"
            f"<td class='mono' style='font-weight:700; color:{APPLE_BLUE};'>{r['2026_t2_proj']}</td>"
            f"</tr>"
        )

    render_html(f"""
    <div class="tbl-card">
        <div class="chart-title">Série Histórica Oficial de Abstenção Eleitoral (TSE: 2014, 2018, 2022 e 2026)</div>
        <div class="chart-subtitle" style="margin-bottom:0.8rem;">Base consolidada de microdados por Unidade da Federação em 1º e 2º turnos</div>
        <table class="data-tbl">
            <thead>
                <tr>
                    <th>Estado (UF)</th>
                    <th>Região</th>
                    <th>2014 (1ºT)</th>
                    <th>2014 (2ºT)</th>
                    <th>2018 (1ºT)</th>
                    <th>2018 (2ºT)</th>
                    <th>2022 (1ºT)</th>
                    <th>2022 (2ºT)</th>
                    <th>2026 (1ºT Real)</th>
                    <th>2026 (2ºT Proj.)</th>
                </tr>
            </thead>
            <tbody>
                {"".join(h_rows_list)}
            </tbody>
        </table>
    </div>
    """)

# ----------------- TAB 4: COEFICIENTES DO RANDOM FOREST -----------------
with tab_coefs:
    render_html("""
    <div class="section-hdr">
        <div class="chart-title">Coeficientes Estaduais de Abstenção (Random Forest TreeSHAP vs. Delta Histórico)</div>
        <div class="chart-subtitle">Impacto marginal de cada estado na variação de abstenção entre o 1º e o 2º turno (em p.p.)</div>
    </div>
    """)

    coef_sort = coef_df.sort_values(by="rf_shap_coef", ascending=True)
    fig_coef = go.Figure()
    fig_coef.add_trace(go.Bar(
        y=coef_sort["uf"] + " - " + coef_sort["estado"],
        x=coef_sort["rf_shap_coef"],
        name="Coeficiente TreeSHAP (p.p.)",
        orientation="h",
        marker_color=[APPLE_AMBER if v > 0.05 else (APPLE_GREEN if v < -0.005 else "#86868B") for v in coef_sort["rf_shap_coef"]],
        text=[f"{v:+.3f} p.p." for v in coef_sort["rf_shap_coef"]],
        textposition="outside",
        textfont=dict(size=10, color=TEXT, weight=600)
    ))
    fig_coef.update_layout(make_layout(
        height=640,
        xaxis=dict(title="Impacto Marginal SHAP na Variação da Abstenção (p.p.)", range=[-0.2, 1.55], tickfont=dict(color=TEXT)),
        yaxis=dict(tickfont=dict(size=11, color=TEXT, weight=600)),
        margin=dict(l=155, r=60, t=15, b=30)
    ))
    st.plotly_chart(fig_coef, use_container_width=True, theme=None, config={"displayModeBar": False})

    c_rows_list = []
    for _, r in coef_df.iterrows():
        sh_val = r["rf_shap_coef"]
        badge_type = '<span class="badge badge-up">Propensão a faltar (+p.p.)</span>' if sh_val > 0.05 else (
            '<span class="badge badge-down">Retenção de eleitores (-p.p.)</span>' if sh_val < -0.005 else '<span style="color:#86868B;">Neutro</span>'
        )
        c_rows_list.append(
            f"<tr>"
            f"<td><b>{r['uf']}</b> - {r['estado']}</td>"
            f"<td>{r['regiao']}</td>"
            f"<td class='mono' style='font-weight:700;'>{r['rf_shap_coef']:+.3f} p.p.</td>"
            f"<td class='mono'>{r['rf_importance_pct']:.2f}%</td>"
            f"<td class='mono'>+{r['historico_delta_medio']:.2f} p.p.</td>"
            f"<td class='mono'>{r['ols_fe_coef']:+.3f}</td>"
            f"<td>{badge_type}</td>"
            f"</tr>"
        )

    render_html(f"""
    <div class="tbl-card">
        <div class="chart-title">Tabela de Coeficientes Estaduais de Impacto Estrutural na Abstenção (Random Forest TreeSHAP)</div>
        <div class="chart-subtitle" style="margin-bottom:0.8rem;">Contribuição marginal não-linear de cada estado na variação de faltosos no 2º turno</div>
        <table class="data-tbl">
            <thead>
                <tr>
                    <th>Estado (UF)</th>
                    <th>Região</th>
                    <th>Coeficiente RF (SHAP)</th>
                    <th>Importância no Modelo</th>
                    <th>Delta Médio Histórico</th>
                    <th>Coeficiente OLS Fixo</th>
                    <th>Diagnóstico Estrutural</th>
                </tr>
            </thead>
            <tbody>
                {"".join(c_rows_list)}
            </tbody>
        </table>
    </div>
    """)

# ----------------- TAB 5: METODOLOGIA & DIAGNÓSTICO -----------------
with tab_method:
    render_html("""
    <div class="section-hdr">
        <div class="chart-title">Comparação Conceitual e Estrutural dos Dois Métodos</div>
        <div class="chart-subtitle">Entenda por que a margem nacional difere em 1,7 milhão de votos</div>
    </div>
    """)
    
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        render_html(f"""
        <div class="kpi-card" style="margin-bottom:1rem;">
            <div class="kpi-title">Método 1: Random Forest (Machine Learning de Urnas)</div>
            <p style="font-size:0.86rem; line-height:1.65; color:{TEXT};">
            <b>Fonte Primária:</b> Microdados oficiais do TSE do 1º turno de 2026.<br>
            <b>Mecanismo:</b><br>
            • Considera a votação real cristalizada na urna (56,1 mi Flávio x 53,8 mi Lula).<br>
            • Simula a redistribuição dos <b>9,31 milhões de votos de terceira via</b> (Caiado, Zema, Renan Santos e Augusto Cury).<br>
            • O modelo de ensemble com 300 árvores e <b>TreeSHAP</b> capta o platô de saturação de abstenção em metrópoles e penalidades logísticas do Norte.<br>
            • <b>Diagnóstico:</b> Projeta vitória mais folgada para Flávio (<b>+4,56 mi de votos</b>) porque assume coesão da centro-direita (Zema e Caiado) transferindo ~62% dos votos residuais para Flávio.
            </p>
        </div>
        """)
        
    with m_col2:
        render_html(f"""
        <div class="kpi-card" style="margin-bottom:1rem;">
            <div class="kpi-title">Método 2: Pesquisa AtlasIntel Ponderada (Likely Voter)</div>
            <p style="font-size:0.86rem; line-height:1.65; color:{TEXT};">
            <b>Fonte Primária:</b> Levantamento AtlasIntel/Bloomberg de 19/10/2026 (4.998 entrevistas, registro BR-02418/2026).<br>
            <b>Mecanismo:</b><br>
            • Parte da intenção declarada da pesquisa de reta final (Flávio 51,1% x Lula 48,9% nos válidos).<br>
            • Corrige a pesquisa aplicando o <b>filtro de abstenção por estado</b> (reponderação do eleitor provável).<br>
            • Capta dinâmicas comportamentais subjetivas de reta final que o histórico de urnas não vê.<br>
            • <b>Diagnóstico:</b> Projeta vitória mais apertada para Flávio (<b>+2,85 mi de votos</b>), reflexo de um <b>empate técnico absoluto em Minas Gerais</b> (Lula 50,2% x Flávio 49,8%) e maior resiliência petista na reta final.
            </p>
        </div>
        """)

    render_html(f"""
    <div class="tbl-card">
        <div class="chart-title">Os 3 Grandes Vetores de Divergência</div>
        <div class="chart-subtitle">Onde estão os 1.707.624 votos de diferença entre as duas projeções?</div>
        <div style="font-size:0.86rem; line-height:1.7; color:{TEXT}; margin-top:0.8rem;">
            <b>1. Minas Gerais é o Fiel da Balança (Impacto: ~920 mil votos):</b><br>
            No modelo de Machine Learning, Flávio lidera em MG por 53,8% a 46,2% alavancado pela máquina estadual de Romeu Zema. Na pesquisa AtlasIntel, Lula e Flávio estão rigorosamente empatados em Minas (50,2% Lula vs 49,8% Flávio). Esse empate em MG é responsável por mais de metade de toda a redução da vantagem nacional de Flávio.<br><br>
            <b>2. A "Super-Conversão" Eleitoral do Nordeste (Impacto: ~418 mil votos):</b><br>
            O Nordeste registra a menor abstenção do país (Ceará com 16,2%, Paraíba 17,6%, Piauí 17,8%, Pernambuco 18,0%). Ao aplicar a abstenção à pesquisa, o peso relativo do Nordeste sobe e "injeta" votos líquidos para Lula, estreitando a distância nacional em 418 mil votos.<br><br>
            <b>3. Dispersão da Terceira Via:</b><br>
            Enquanto o modelo de urnas assume transferência direta de blocos partidários consolidados, a pesquisa amostral da AtlasIntel revela que parte dos eleitores moderados de Caiado e independentes de Cury preferem o voto nulo ou hesitam em votar em Flávio, atenuando a conversão de votos.
        </div>
    </div>
    """)

# ----------------- TAB 6: BACKTEST 2022 (VALIDAÇÃO HISTÓRICA OUT-OF-TIME) -----------------
with tab_backtest:
    render_html("""
    <div class="section-hdr">
        <div class="chart-title">Validação Histórica Out-of-Time na Eleição de 2022 (Treino: 2014–2018 | Teste Cego: 2022)</div>
        <div class="chart-subtitle">Avaliação rigorosa de Machine Learning sem vazamento temporal (data leakage): confronto do Resultado Oficial do TSE contra a Pesquisa Bruta e os Métodos 1 e 2</div>
    </div>
    """)

    bk1, bk2, bk3, bk4 = st.columns(4)
    with bk1:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">Resultado Oficial TSE 2022</div>
            <div class="kpi-val" style="color:{APPLE_RED};">50,90% x 49,10%</div>
            <div class="kpi-sub">Vantagem real de Lula: <b>+1,80 p.p.</b> (+2,13 mi votos nas 27 UFs). Bolsonaro capturou <b>69,8%</b> dos novos votos líquidos do 2ºT.</div>
        </div>
        """)
    with bk2:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">Método 1 (RF + Urnas 1ºT)</div>
            <div class="kpi-val" style="color:{APPLE_GREEN};">RMSE: 1,58 p.p.</div>
            <div class="kpi-sub">Placar projetado: <b>52,30% x 47,70%</b> (MAE: 1,45 p.p. | R² = 0,9887). Erro <b>31% menor</b> que o da pesquisa bruta de véspera.</div>
        </div>
        """)
    with bk3:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">Método 2 (Atlas 29/10 + Abst RF)</div>
            <div class="kpi-val" style="color:{APPLE_BLUE};">27/27 UFs (100%)</div>
            <div class="kpi-sub">A ponderação pela abstenção reduziu o RMSE da AtlasIntel de <b>2,29 p.p. para 1,94 p.p.</b> (-15,3%) e acertou a virada no <b>Amapá</b>.</div>
        </div>
        """)
    with bk4:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">Pesquisa Bruta (Atlas 29/10/22)</div>
            <div class="kpi-val" style="color:{APPLE_AMBER};">RMSE: 2,29 p.p.</div>
            <div class="kpi-sub">Projetou <b>53,4% x 46,6%</b> na véspera (erro de <b>+2,52 p.p.</b> pró-Lula no placar nacional e errou o vencedor no AP).</div>
        </div>
        """)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    render_html("""
    <div class="section-hdr">
        <div class="chart-title">Comparativo Nacional 2022: Resultado Real (TSE) vs. Pesquisa Bruta vs. Método 1 vs. Método 2</div>
        <div class="chart-subtitle">Confronto direto do percentual e volume de votos válidos nas 27 UFs entre a urna oficial e as 3 abordagens testadas</div>
    </div>
    """)

    tot_l_real = bt_df["lula_2t_real_votos"].sum()
    tot_b_real = bt_df["bolso_2t_real_votos"].sum()
    pct_l_real = tot_l_real / (tot_l_real + tot_b_real) * 100
    pct_b_real = 100.0 - pct_l_real

    tot_l_m1 = bt_df["lula_m1_votos"].sum()
    tot_b_m1 = bt_df["bolso_m1_votos"].sum()
    pct_l_m1 = tot_l_m1 / (tot_l_m1 + tot_b_m1) * 100
    pct_b_m1 = 100.0 - pct_l_m1

    tot_l_m2 = bt_df["lula_m2_votos"].sum()
    tot_b_m2 = bt_df["bolso_m2_votos"].sum()
    pct_l_m2 = tot_l_m2 / (tot_l_m2 + tot_b_m2) * 100
    pct_b_m2 = 100.0 - pct_l_m2

    tot_l_at = bt_df["lula_atlas_raw_votos"].sum()
    tot_b_at = bt_df["bolso_atlas_raw_votos"].sum()
    pct_l_at = tot_l_at / (tot_l_at + tot_b_at) * 100
    pct_b_at = 100.0 - pct_l_at

    y_labels_bt = [
        "1. Resultado Real TSE 2022 (Urnas)",
        "2. Método 1: RF + Urnas 1ºT (ML)",
        "3. Método 2: AtlasIntel + Abstenção RF",
        "4. Pesquisa AtlasIntel Bruta (29/10/22)"
    ]
    x_bolso_bt = [pct_b_real, pct_b_m1, pct_b_m2, pct_b_at]
    x_lula_bt = [pct_l_real, pct_l_m1, pct_l_m2, pct_l_at]
    v_bolso_bt = [tot_b_real, tot_b_m1, tot_b_m2, tot_b_at]
    v_lula_bt = [tot_l_real, tot_l_m1, tot_l_m2, tot_l_at]

    fig_bt_placar = go.Figure()
    fig_bt_placar.add_trace(go.Bar(
        y=y_labels_bt,
        x=x_bolso_bt,
        name="Jair Bolsonaro (% Válidos)",
        orientation="h",
        marker=dict(color=APPLE_BLUE),
        text=[f"Bolsonaro: {p:.2f}% ({v:,.0f})".replace(",", ".") for p, v in zip(x_bolso_bt, v_bolso_bt)],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#ffffff", size=12, family=APPLE_FONT_STACK, weight=700)
    ))
    fig_bt_placar.add_trace(go.Bar(
        y=y_labels_bt,
        x=x_lula_bt,
        name="Lula (% Válidos)",
        orientation="h",
        marker=dict(color=APPLE_RED),
        text=[f"Lula: {p:.2f}% ({v:,.0f})".replace(",", ".") for p, v in zip(x_lula_bt, v_lula_bt)],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#ffffff", size=12, family=APPLE_FONT_STACK, weight=700)
    ))
    fig_bt_placar.add_vline(
        x=50, line_width=2, line_dash="dash", line_color=TEXT,
        annotation_text="50% Maioria", annotation_position="top",
        annotation_font=dict(size=11, color=TEXT, family=APPLE_FONT_STACK, weight=700)
    )
    fig_bt_placar.update_layout(make_layout(
        barmode="stack",
        height=240,
        margin=dict(l=245, r=20, t=28, b=12),
        xaxis=dict(range=[0, 100], showticklabels=False, showgrid=False),
        yaxis=dict(autorange="reversed", tickfont=dict(size=12, color=TEXT, weight=700)),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1, font=dict(color=TEXT, size=11))
    ))
    st.plotly_chart(fig_bt_placar, use_container_width=True, theme=None, config={"displayModeBar": False})

    render_html(f"""
    <div class="tbl-card">
        <div class="chart-title">Tabela Comparativa Síntese do Backtest 2022: Resultado Real vs. Pesquisa vs. Métodos 1 e 2</div>
        <div class="chart-subtitle" style="margin-bottom:0.8rem;">Métricas consolidadas de acurácia nacional e erro estadual (27 UFs) com intervalos de confiança via Bootstrap</div>
        <table class="data-tbl">
            <thead>
                <tr>
                    <th>Referência / Método Avaliado</th>
                    <th>Lula (% e Votos)</th>
                    <th>Bolsonaro (% e Votos)</th>
                    <th>Margem (Lula - Bolso)</th>
                    <th>Erro no Placar</th>
                    <th>RMSE Estadual (IC 95%)</th>
                    <th>MAE Estadual</th>
                    <th>R² Estadual</th>
                    <th>Acertos de Vencedor UF</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background:{APPLE_GREEN_BG};">
                    <td><b>1. Resultado Real Oficial (TSE 2022)</b></td>
                    <td class="mono"><b>50,90%</b> (60.193.094)</td>
                    <td class="mono"><b>49,10%</b> (58.061.090)</td>
                    <td><span class="badge badge-lula">+1,80 p.p. (+2,13 mi)</span></td>
                    <td class="mono"><b>0,00 p.p. (Oficial)</b></td>
                    <td class="mono">—</td>
                    <td class="mono">—</td>
                    <td class="mono">1,0000</td>
                    <td><span class="badge badge-gov">27/27 UFs (Referência)</span></td>
                </tr>
                <tr>
                    <td><b>2. Método 1: Random Forest + Urnas 1ºT</b></td>
                    <td class="mono"><b>52,30%</b> (60.976.140)</td>
                    <td class="mono"><b>47,70%</b> (55.616.126)</td>
                    <td><span class="badge badge-lula">+4,60 p.p. (+5,36 mi)</span></td>
                    <td class="mono" style="color:{APPLE_GREEN}; font-weight:700;">-1,40 p.p. (Menor Erro)</td>
                    <td class="mono"><b>1,58 p.p.</b> [1,35; 1,78]</td>
                    <td class="mono"><b>1,45 p.p.</b></td>
                    <td class="mono"><b>0,9887</b></td>
                    <td><span class="badge badge-flavio">26/27 UFs (96,3%)</span></td>
                </tr>
                <tr>
                    <td><b>3. Método 2: Pesquisa AtlasIntel + Abstenção RF</b></td>
                    <td class="mono"><b>53,19%</b> (62.010.433)</td>
                    <td class="mono"><b>46,81%</b> (54.581.828)</td>
                    <td><span class="badge badge-lula">+6,37 p.p. (+7,43 mi)</span></td>
                    <td class="mono" style="color:{APPLE_AMBER}; font-weight:700;">-2,29 p.p.</td>
                    <td class="mono"><b>1,94 p.p.</b> [1,78; 2,11]</td>
                    <td class="mono"><b>1,89 p.p.</b></td>
                    <td class="mono"><b>0,9829</b></td>
                    <td><span class="badge badge-gov">27/27 UFs (100,0% - Acertou AP)</span></td>
                </tr>
                <tr>
                    <td><b>4. Pesquisa AtlasIntel Bruta (Véspera 29/10/22)</b></td>
                    <td class="mono"><b>53,42%</b> (63.005.557)</td>
                    <td class="mono"><b>46,58%</b> (54.929.637)</td>
                    <td><span class="badge badge-lula">+6,85 p.p. (+8,08 mi)</span></td>
                    <td class="mono" style="color:{APPLE_RED}; font-weight:700;">-2,52 p.p. (Maior Erro)</td>
                    <td class="mono"><b>2,29 p.p.</b> [2,17; 2,42]</td>
                    <td class="mono"><b>2,26 p.p.</b></td>
                    <td class="mono">0,9762</td>
                    <td><span class="badge badge-up">26/27 UFs (96,3% - Errou AP)</span></td>
                </tr>
            </tbody>
        </table>
    </div>
    """)

    # ----------------- SEÇÃO: PESQUISAS DE SÁBADO DE VÉSPERA (29/10/2022) -----------------
    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    render_html("""
    <div class="section-hdr">
        <div class="chart-title">Ranking de Assertividade das Pesquisas de Véspera (Sábado 29/10/2022) vs. Urna Oficial e Modelos ML</div>
        <div class="chart-subtitle">Confronto estruturado dos 8 institutos de véspera contra a apuração do TSE: validação do Método 2 (filtro de abstenção RF out-of-time) e do Método 1 (Random Forest de Urnas 1ºT)</div>
    </div>
    """)

    pk1, pk2, pk3, pk4 = st.columns(4)
    with pk1:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">Resultado Oficial TSE 2022</div>
            <div class="kpi-val" style="color:{APPLE_GREEN};">50,90% x 49,10%</div>
            <div class="kpi-sub">Lula eleito por <b>+1,80 p.p.</b> (+2,13 mi de votos nas 27 UFs). Referência imutável de validação (Ground Truth).</div>
        </div>
        """)
    with pk2:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">Método 1 (RF Urnas 1ºT)</div>
            <div class="kpi-val" style="color:{APPLE_BLUE};">Erro: 1,40 p.p.</div>
            <div class="kpi-sub">Projetou <b>52,30% x 47,70%</b> (RMSE estadual <b>1,58 p.p.</b>). Superou <b>7 dos 8 institutos</b> sem entrevistar eleitores.</div>
        </div>
        """)
    with pk3:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">Mais Preciso c/ Método 2</div>
            <div class="kpi-val" style="color:{APPLE_GREEN};">Erro: 0,03 p.p.</div>
            <div class="kpi-sub">Genial/Quaest reponderada pela abstenção RF cravou <b>50,93% x 49,07%</b> (reduziu erro de 1,10 para 0,03 p.p.).</div>
        </div>
        """)
    with pk4:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">Correção de Viés por Abstenção</div>
            <div class="kpi-val" style="color:{APPLE_AMBER};">-1,90 p.p. (Ipec)</div>
            <div class="kpi-sub">Método 2 reduziu o erro do Ipec de <b>3,10 para 1,20 p.p.</b> (-61%) e atingiu <b>27/27 UFs (100%)</b> de acertos de vencedores.</div>
        </div>
        """)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Plotly Bar Chart: Ranking de Assertividade das Pesquisas de Sábado
    p_sort = polls_df.sort_values(by="erro_placar_m2", ascending=True).copy()

    fig_polls_rank = go.Figure()

    fig_polls_rank.add_trace(go.Bar(
        y=p_sort["instituto"],
        x=p_sort["erro_placar_bruto"],
        name="Pesquisa Bruta de Véspera (29/10)",
        orientation="h",
        marker=dict(color="#86868B"),
        text=[f"{v:.2f} p.p." for v in p_sort["erro_placar_bruto"]],
        textposition="outside",
        textfont=dict(size=11, color=TEXT, family=APPLE_FONT_STACK, weight=600)
    ))

    fig_polls_rank.add_trace(go.Bar(
        y=p_sort["instituto"],
        x=p_sort["erro_placar_m2"],
        name="Ponderada por Abstenção RF (Método 2)",
        orientation="h",
        marker=dict(color=APPLE_AMBER),
        text=[f"{v:.2f} p.p." for v in p_sort["erro_placar_m2"]],
        textposition="outside",
        textfont=dict(size=11, color=TEXT, family=APPLE_FONT_STACK, weight=700)
    ))

    fig_polls_rank.add_vline(
        x=0.0, line_width=2, line_color=APPLE_GREEN,
        annotation_text="TSE 2022 (Erro 0,00 p.p.)",
        annotation_position="top left",
        annotation_font=dict(size=11, color=APPLE_GREEN, family=APPLE_FONT_STACK, weight=700)
    )

    fig_polls_rank.add_vline(
        x=1.40, line_width=2, line_dash="dash", line_color=APPLE_BLUE,
        annotation_text="Método 1 (RF Urnas): 1,40 p.p.",
        annotation_position="bottom right",
        annotation_font=dict(size=11, color=APPLE_BLUE, family=APPLE_FONT_STACK, weight=700)
    )

    fig_polls_rank.update_layout(make_layout(
        title=dict(
            text="<b>Ranking de Assertividade das Pesquisas de Véspera (29/10/2022): Erro no Placar Nacional (p.p.)</b>",
            font=dict(size=13, color=TEXT, family=APPLE_FONT_STACK)
        ),
        barmode="group",
        height=410,
        margin=dict(l=165, r=45, t=55, b=25),
        xaxis=dict(
            title="Erro Absoluto em Relação ao Resultado Oficial do TSE (Pontos Percentuais)",
            range=[0, 4.5],
            tickfont=dict(size=11, color=TEXT)
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=12, color=TEXT, weight=700)
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1, font=dict(color=TEXT, size=11))
    ))
    st.plotly_chart(fig_polls_rank, use_container_width=True, theme=None, config={"displayModeBar": False})

    # Full Comparative Table via render_html()
    p_rows_html = []

    p_rows_html.append(
        f'<tr style="background:{APPLE_GREEN_BG}; font-weight:600;">'
        f'<td><b>1. Resultado Oficial TSE Real (30/10)</b><br/><span style="color:{TEXT_DIM}; font-size:0.75rem;">Justiça Eleitoral (100% Urnas)</span></td>'
        f'<td class="mono">TSE 30/10/2022<br/><span style="color:{TEXT_DIM}; font-size:0.74rem;">118.254.184 válidos</span></td>'
        f'<td><span class="badge badge-green">Urnas Eletrônicas</span></td>'
        f'<td class="mono"><b>50,90%</b> x <b>49,10%</b></td>'
        f'<td class="mono"><b>0,00 p.p.</b></td>'
        f'<td class="mono"><b>50,90%</b> x <b>49,10%</b></td>'
        f'<td class="mono"><b>0,00 p.p.</b></td>'
        f'<td><span class="badge badge-green">— Ref. Oficial</span></td>'
        f'<td class="mono">0,00 p.p.</td>'
        f'<td><span class="badge badge-green">27/27 (100%)</span></td>'
        f'<td style="font-size:0.78rem; color:{TEXT_MUTED};">Ground Truth oficial das 27 UFs. Lula eleito por margem de +1,80 p.p. (+2,13 mi).</td>'
        f'</tr>'
    )

    p_rows_html.append(
        f'<tr style="background:{APPLE_BLUE_BG}; font-weight:600;">'
        f'<td><b>★ Método 1: Random Forest + Urnas 1ºT</b><br/><span style="color:{TEXT_DIM}; font-size:0.75rem;">Modelo ML Out-of-Time 2014–2018</span></td>'
        f'<td class="mono">Backtest Cego<br/><span style="color:{TEXT_DIM}; font-size:0.74rem;">116.592.266 válidos</span></td>'
        f'<td><span class="badge badge-blue">Machine Learning (Urnas)</span></td>'
        f'<td class="mono" style="color:{TEXT_DIM};">— (Sem pesquisa)</td>'
        f'<td class="mono" style="color:{TEXT_DIM};">—</td>'
        f'<td class="mono"><b>52,30%</b> x <b>47,70%</b></td>'
        f'<td class="mono" style="color:{APPLE_BLUE}; font-weight:700;">1,40 p.p.</td>'
        f'<td><span class="badge badge-blue">Superou 7/8</span></td>'
        f'<td class="mono"><b>1,58 p.p.</b></td>'
        f'<td><span class="badge badge-blue">26/27 (96,3%)</span></td>'
        f'<td style="font-size:0.78rem; color:{TEXT_MUTED};">Superou 7 dos 8 institutos de véspera em fidelidade estrutural estadual sem entrevistar nenhum eleitor.</td>'
        f'</tr>'
    )

    for _, pr in p_sort.iterrows():
        red_err = pr["reducao_erro_pp"]
        if red_err > 0.05:
            delta_badge = f'<span class="badge badge-green">-{red_err:.2f} p.p. (Melhorou)</span>'
        elif red_err < -0.05:
            delta_badge = f'<span class="badge badge-amber">+{abs(red_err):.2f} p.p.</span>'
        else:
            delta_badge = f'<span class="badge" style="background:#E5E5EA; color:{TEXT_MUTED};">0,00 p.p.</span>'

        m2_err_val = pr["erro_placar_m2"]
        if m2_err_val <= 0.50:
            m2_badge = f'<span class="badge badge-green">{m2_err_val:.2f} p.p.</span>'
        elif m2_err_val <= 1.50:
            m2_badge = f'<span class="badge badge-blue">{m2_err_val:.2f} p.p.</span>'
        else:
            m2_badge = f'<span class="badge badge-amber">{m2_err_val:.2f} p.p.</span>'

        inst = str(pr["instituto"])
        if "Quaest" in inst:
            diag_txt = "Mais preciso de véspera com Método 2; ponderação reduziu erro de 1,10 para 0,03 p.p., praticamente cravando o TSE."
        elif "MDA" in inst:
            diag_txt = "Menor erro bruto presencial (0,20 p.p.); com abstenção RF manteve baixíssimo erro regional (RMSE estadual 1,38 p.p.)."
        elif "Ipec" in inst:
            diag_txt = "Maior redução de viés com Método 2 (+1,90 p.p. corrigidos); alcançou 100% de acerto nas 27 UFs e menor RMSE (1,10 p.p.)."
        elif "Datafolha" in inst:
            diag_txt = "Amostra ampla (N=8.308) com alta consistência em SP/MG; viés residual no Sudeste manteve margem acima de 5 p.p."
        elif "Paraná" in inst or "Paran" in inst:
            diag_txt = "Segundo melhor placar bruto (50,4% x 49,6%); captou força de Bolsonaro no Sul, mas ponderação inverteu margem."
        elif "Atlas" in inst:
            diag_txt = "Método 2 reduziu o RMSE estadual em 11,8% e acertou a virada de Bolsonaro no Amapá (AP), corrigindo a distorção bruta."
        elif "Modalmais" in inst or "Futura" in inst:
            diag_txt = "Pesquisa telefônica já continha desconto de abstenção no eleitorado de baixa renda, ampliando viés pró-Bolsonaro."
        elif "Veritá" in inst or "Verit" in inst:
            diag_txt = "Amostra gigantesca (N=30.180), mas autoselecionada na internet; inverteu o vencedor tanto no bruto quanto no ponderado."
        else:
            diag_txt = f"{pr['metodologia']}; viés bruto: {pr['vies_direcional_bruto']}."

        n_fmt = f"{int(pr['amostra']):,}".replace(",", ".")
        p_rows_html.append(
            f'<tr>'
            f'<td><b>{pr["instituto"]}</b><br/><span style="color:{TEXT_DIM}; font-size:0.75rem;">{pr["contratante"]}</span></td>'
            f'<td class="mono">{pr["registro_tse"]}<br/><span style="color:{TEXT_DIM}; font-size:0.74rem;">N = {n_fmt} (±{pr["margem_erro"]:.1f} p.p.)</span></td>'
            f'<td><span class="badge" style="background:#F2F2F7; color:{TEXT};">{pr["metodologia"]}</span></td>'
            f'<td class="mono">{pr["lula_bruto_pct"]:.2f}% x {pr["bolso_bruto_pct"]:.2f}%</td>'
            f'<td class="mono"><b>{pr["erro_placar_bruto"]:.2f} p.p.</b></td>'
            f'<td class="mono"><b>{pr["lula_m2_pct"]:.2f}%</b> x {pr["bolso_m2_pct"]:.2f}%</td>'
            f'<td class="mono">{m2_badge}</td>'
            f'<td>{delta_badge}</td>'
            f'<td class="mono">{pr["rmse_estadual_m2"]:.2f} p.p.</td>'
            f'<td><span class="badge badge-gov">{pr["acertos_vencedor_uf_m2"]}</span></td>'
            f'<td style="font-size:0.78rem; color:{TEXT_MUTED};">{diag_txt}</td>'
            f'</tr>'
        )

    render_html(f"""
    <div class="tbl-card">
        <div class="chart-title">Tabela Comparativa Completa das Pesquisas de Véspera (Sábado 29/10/2022) vs. Resultado Oficial TSE e Método 1</div>
        <div class="chart-subtitle" style="margin-bottom:0.8rem;">Confronto de votos válidos (% Lula x % Bolsonaro), margens, erros absolutos em relação à apuração oficial, efeito corretivo da abstenção e diagnósticos</div>
        <table class="data-tbl">
            <thead>
                <tr>
                    <th>Instituto & Contratante</th>
                    <th>Registro TSE & Amostra (N)</th>
                    <th>Modo de Coleta</th>
                    <th>Placar Bruto (29/10)</th>
                    <th>Erro Placar Bruto</th>
                    <th>Placar Método 2 (Abst RF)</th>
                    <th>Erro Método 2</th>
                    <th>Δ Erro com Abstenção</th>
                    <th>RMSE Estadual M2</th>
                    <th>Acertos UF</th>
                    <th>Diagnóstico Metodológico</th>
                </tr>
            </thead>
            <tbody>
                {"".join(p_rows_html)}
            </tbody>
        </table>
    </div>
    """)

    render_html(f"""
    <div class="tbl-card" style="padding:1.35rem 1.6rem; margin-bottom:1.5rem;">
        <div class="chart-title">Diagnóstico Metodológico: Por que o Modelo de Urnas (Método 1) e o Filtro de Abstenção (Método 2) Venceram as Pesquisas Tradicionais?</div>
        <div class="chart-subtitle" style="margin-bottom:1rem;">Três descobertas fundamentais da modelagem quantitativa no teste cego out-of-time da eleição de 2022</div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:1.1rem;">
            <div style="background:#F5F5F7; border-radius:12px; padding:1.1rem; border:1px solid #E5E5EA;">
                <div style="font-weight:700; color:{TEXT}; font-size:0.92rem; margin-bottom:0.4rem;">1. Modos de Coleta e Vieses Amostrais</div>
                <div style="font-size:0.81rem; color:{TEXT_MUTED}; line-height:1.52;">
                    • <b>Presencial Domiciliar</b> (Datafolha, Ipec, Quaest, MDA): superestimou a vantagem de Lula em +2 a +6 p.p. na margem devido à sub-representação de condomínios fechados e bairros de classe média bolsonarista.<br/>
                    • <b>Telefônico CATI</b> (Modalmais/Futura) e <b>Web Passiva</b> (Veritá): superestimaram Bolsonaro por viés de engajamento e recusa diferencial de eleitores petistas.<br/>
                    • <b>Digital RDR</b> (AtlasIntel): alta precisão regional, mas dependente de calibração fina de escolaridade e renda.
                </div>
            </div>
            <div style="background:#F5F5F7; border-radius:12px; padding:1.1rem; border:1px solid #E5E5EA;">
                <div style="font-weight:700; color:{TEXT}; font-size:0.92rem; margin-bottom:0.4rem;">2. Dinâmica de Abstenção Friccional (Método 2)</div>
                <div style="font-size:0.81rem; color:{TEXT_MUTED}; line-height:1.52;">
                    • No 2º turno de 2022, a abstenção caiu no <b>Nordeste</b> (-0,5 a -0,9 p.p. com gratuidade de transporte e mobilização) e subiu fortemente no <b>Norte</b> (+3 a +7 p.p. no AP/AC/RR).<br/>
                    • Ao aplicar os coeficientes out-of-time previstos pelo Random Forest, o <b>Método 2 expurgou o viés pró-Lula</b> nas pesquisas de véspera, aproximando a Quaest de 50,93% (erro de apenas 0,03 p.p.) e o Ipec de 52,10% (queda de 61% no erro).<br/>
                    • Cravou a virada no <b>Amapá (AP)</b> para Bolsonaro, que todas as pesquisas brutas haviam errado.
                </div>
            </div>
            <div style="background:#F5F5F7; border-radius:12px; padding:1.1rem; border:1px solid #E5E5EA;">
                <div style="font-weight:700; color:{TEXT}; font-size:0.92rem; margin-bottom:0.4rem;">3. Superioridade do Método 1 (Microdados de Urna)</div>
                <div style="font-size:0.81rem; color:{TEXT_MUTED}; line-height:1.52;">
                    • O <b>Método 1 (Random Forest Out-of-Time)</b> foi treinado exclusivamente em 2014–2018 e projetou <b>52,30% x 47,70%</b> a partir dos 118 milhões de votos reais do 1º turno.<br/>
                    • Obteve erro nacional de <b>1,40 p.p.</b> e RMSE estadual de <b>1,58 p.p.</b>, superando <b>7 dos 8 institutos de véspera</b>.<br/>
                    • Vantagem estrutural: <i>voto de urna não mente, não se esquiva de entrevistadores e não depende de autodeclaração amostral</i>.
                </div>
            </div>
        </div>
    </div>
    """)

    render_html("""
    <div class="section-hdr">
        <div class="chart-title">Comparativo Direto por Estado (% Jair Bolsonaro no 2º Turno 2022): Real vs. Pesquisa vs. Método 1 vs. Método 2</div>
        <div class="chart-subtitle">Veja em cada estado como o Método 1 (Azul) e o Método 2 (Âmbar) se aproximam mais do Resultado Oficial TSE (Verde) do que a Pesquisa Bruta (Cinza)</div>
    </div>
    """)

    bt_reg_sel = st.selectbox(
        "Filtrar Estados no Gráfico Comparativo do Backtest 2022:",
        ["Principais Colégios Eleitorais e Estados-Chave (12 UFs)", "Todas as 27 UFs", "Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"],
        key="bt_reg_comp"
    )
    if bt_reg_sel == "Principais Colégios Eleitorais e Estados-Chave (12 UFs)":
        bt_sub_comp = bt_df[bt_df["uf"].isin(["SP", "MG", "RJ", "BA", "RS", "PR", "PE", "CE", "PA", "GO", "SC", "AP"])].copy()
    elif bt_reg_sel == "Todas as 27 UFs":
        bt_sub_comp = bt_df.copy()
    else:
        bt_sub_comp = bt_df[bt_df["regiao"] == bt_reg_sel].copy()

    bt_sub_comp = bt_sub_comp.sort_values(by="bolso_2t_real_pct", ascending=False)

    fig_bt_4way = go.Figure()
    fig_bt_4way.add_trace(go.Bar(
        x=bt_sub_comp["uf"],
        y=bt_sub_comp["bolso_2t_real_pct"],
        name="1. Resultado Real TSE 2022",
        marker_color=APPLE_GREEN,
        text=[f"{v:.1f}%" for v in bt_sub_comp["bolso_2t_real_pct"]],
        textposition="outside",
        textfont=dict(size=10, color=TEXT, weight=700)
    ))
    fig_bt_4way.add_trace(go.Bar(
        x=bt_sub_comp["uf"],
        y=bt_sub_comp["bolso_m1_pct"],
        name="2. Método 1 (RF + Urnas 1ºT)",
        marker_color=APPLE_BLUE,
        text=[f"{v:.1f}%" for v in bt_sub_comp["bolso_m1_pct"]],
        textposition="outside",
        textfont=dict(size=10, color=TEXT)
    ))
    fig_bt_4way.add_trace(go.Bar(
        x=bt_sub_comp["uf"],
        y=bt_sub_comp["bolso_m2_pct"],
        name="3. Método 2 (Atlas + Abstenção RF)",
        marker_color=APPLE_AMBER,
        text=[f"{v:.1f}%" for v in bt_sub_comp["bolso_m2_pct"]],
        textposition="outside",
        textfont=dict(size=10, color=TEXT)
    ))
    fig_bt_4way.add_trace(go.Bar(
        x=bt_sub_comp["uf"],
        y=bt_sub_comp["bolso_atlas_raw_pct"],
        name="4. Pesquisa AtlasIntel Bruta (29/10)",
        marker_color="#86868B",
        text=[f"{v:.1f}%" for v in bt_sub_comp["bolso_atlas_raw_pct"]],
        textposition="outside",
        textfont=dict(size=10, color=TEXT)
    ))
    fig_bt_4way.add_hline(y=50, line_dash="dash", line_color=TEXT_DIM, line_width=1.5)
    fig_bt_4way.update_layout(make_layout(
        barmode="group",
        height=390,
        xaxis=dict(title="Unidade da Federação (UF)", tickfont=dict(color=TEXT, size=11, weight=700)),
        yaxis=dict(title="% de Votos Válidos (Bolsonaro)", range=[0, 86], tickfont=dict(color=TEXT)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color=TEXT, size=11))
    ))
    st.plotly_chart(fig_bt_4way, use_container_width=True, theme=None, config={"displayModeBar": False})

    b_col1, b_col2 = st.columns([6, 6])
    with b_col1:
        render_html("""
        <div class="section-hdr">
            <div class="chart-title">Erro Absoluto por Estado no Backtest 2022 (Pesquisa Bruta vs. Método 1 vs. Método 2)</div>
            <div class="chart-subtitle">Distância absoluta em p.p. para o resultado oficial do TSE em cada UF (quanto menor a barra, mais preciso)</div>
        </div>
        """)

        bt_sorted = bt_df.sort_values(by="bolso_2t_real_pct", ascending=True)
        bt_sorted["erro_atlas_raw_abs"] = (bt_sorted["bolso_atlas_raw_pct"] - bt_sorted["bolso_2t_real_pct"]).abs()
        fig_bt_err = go.Figure()
        fig_bt_err.add_trace(go.Bar(
            y=bt_sorted["uf"],
            x=bt_sorted["erro_pct_bolso_m1"].abs(),
            name="Método 1: RF + Urnas (MAE: 1,45 p.p.)",
            orientation="h",
            marker_color=APPLE_BLUE
        ))
        fig_bt_err.add_trace(go.Bar(
            y=bt_sorted["uf"],
            x=bt_sorted["erro_pct_bolso_m2"].abs(),
            name="Método 2: Atlas + Abst (MAE: 1,89 p.p.)",
            orientation="h",
            marker_color=APPLE_AMBER
        ))
        fig_bt_err.add_trace(go.Bar(
            y=bt_sorted["uf"],
            x=bt_sorted["erro_atlas_raw_abs"],
            name="Pesquisa Atlas Bruta (MAE: 2,26 p.p.)",
            orientation="h",
            marker_color="#86868B"
        ))
        fig_bt_err.update_layout(make_layout(
            height=640,
            barmode="group",
            xaxis=dict(title="Erro Absoluto em Pontos Percentuais (p.p.)", tickfont=dict(color=TEXT)),
            yaxis=dict(tickfont=dict(size=11, color=TEXT, weight=600)),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10, color=TEXT))
        ))
        st.plotly_chart(fig_bt_err, use_container_width=True, theme=None, config={"displayModeBar": False})

    with b_col2:
        render_html("""
        <div class="section-hdr">
            <div class="chart-title">Abstenção no 2º Turno de 2022: Real (TSE) vs. Random Forest Out-of-Time</div>
            <div class="chart-subtitle">Correlação de Ranking Estadual Spearman = 0,920 (Captura a explosão no Norte vs. queda no Centro-Sul)</div>
        </div>
        """)

        bt_abst_sort = bt_df.sort_values(by="delta_abst_real_2022", ascending=True)
        fig_bt_abst = go.Figure()
        fig_bt_abst.add_trace(go.Bar(
            y=bt_abst_sort["uf"],
            x=bt_abst_sort["delta_abst_real_2022"],
            name="Delta Real TSE 2022 (2ºT - 1ºT)",
            orientation="h",
            marker_color=APPLE_GREEN
        ))
        fig_bt_abst.add_trace(go.Bar(
            y=bt_abst_sort["uf"],
            x=bt_abst_sort["delta_abst_rf_oot"],
            name="Delta Previsto RF Out-of-Time (Treino 14-18)",
            orientation="h",
            marker_color=APPLE_RED
        ))
        fig_bt_abst.update_layout(make_layout(
            height=640,
            barmode="group",
            xaxis=dict(title="Variação da Abstenção entre 1º e 2º Turno (p.p.)", tickfont=dict(color=TEXT)),
            yaxis=dict(tickfont=dict(size=11, color=TEXT, weight=600)),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10, color=TEXT))
        ))
        st.plotly_chart(fig_bt_abst, use_container_width=True, theme=None, config={"displayModeBar": False})

    bt_rows_list = []
    for _, r in bt_df.sort_values(by="bolso_2t_real_pct", ascending=False).iterrows():
        b_gov22 = '<span class="badge badge-gov">Sim (2ºT)</span>' if r["teve_2t_gov"] == "Sim" else '<span style="color:#86868B;">Não</span>'
        win_real = "badge-flavio" if r["bolso_2t_real_pct"] > 50 else "badge-lula"
        bt_rows_list.append(
            f"<tr>"
            f"<td><b>{r['uf']}</b> - {r['estado']}</td>"
            f"<td>{b_gov22}</td>"
            f"<td class='mono'>{r['abst_2t_real_2022']:.2f}% ({r['delta_abst_real_2022']:+.2f})</td>"
            f"<td class='mono'>{r['abst_2t_rf_oot']:.2f}% ({r['delta_abst_rf_oot']:+.2f})</td>"
            f"<td><span class='badge {win_real}'>Bolso {r['bolso_2t_real_pct']:.2f}% x {r['lula_2t_real_pct']:.2f}% Lula</span></td>"
            f"<td class='mono'><b>{r['bolso_m1_pct']:.2f}%</b> x {r['lula_m1_pct']:.2f}% ({r['erro_pct_bolso_m1']:+.2f} p.p.)</td>"
            f"<td class='mono'>{r['bolso_atlas_raw_pct']:.2f}% x {r['lula_atlas_raw_pct']:.2f}%</td>"
            f"<td class='mono'><b>{r['bolso_m2_pct']:.2f}%</b> x {r['lula_m2_pct']:.2f}% ({r['erro_pct_bolso_m2']:+.2f} p.p.)</td>"
            f"</tr>"
        )

    render_html(f"""
    <div class="tbl-card">
        <div class="chart-title">Auditoria Estadual Completa do Backtest de 2022 (27 Unidades da Federação)</div>
        <div class="chart-subtitle" style="margin-bottom:0.8rem;">Confronto entre o Resultado Oficial TSE 2022, o Método 1 (RF + Urnas 1ºT), a Pesquisa AtlasIntel Bruta (29/10/2022) e o Método 2 (Atlas + Abstenção)</div>
        <table class="data-tbl">
            <thead>
                <tr>
                    <th>Estado (UF)</th>
                    <th>2ºT Gov (2022)</th>
                    <th>Abst. 2ºT Real (Δ)</th>
                    <th>Abst. 2ºT RF (Δ)</th>
                    <th>Resultado Oficial TSE 2022</th>
                    <th>Método 1 (RF + Urnas 1ºT)</th>
                    <th>AtlasIntel Bruta (29/10/22)</th>
                    <th>Método 2 (Atlas + Abst RF)</th>
                </tr>
            </thead>
            <tbody>
                {"".join(bt_rows_list)}
            </tbody>
        </table>
    </div>
    """)
