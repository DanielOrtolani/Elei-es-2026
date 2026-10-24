#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
===============================================================================
PROJEÇÃO 2º TURNO 2026: APLICAÇÃO DO MODELO DE ABSTENÇÃO (RANDOM FOREST)
A TODAS AS PESQUISAS ELEITORAIS DIVULGADAS HOJE (24/10/2026) E VÉSPERA (23/10)
===============================================================================
Replica exatamente a metodologia aplicada à AtlasIntel (apply_abstention_to_atlas.py)
para todas as pesquisas de 2º turno divulgadas na véspera da eleição de 2026:
1. Datafolha (24/10/2026 - BR-09540/2026): 51,0% Flávio x 49,0% Lula
2. Genial/Quaest (24/10/2026 - BR-09158/2026): 51,0% Flávio x 49,0% Lula
3. CNT/MDA (24/10/2026 - BR-02136/2026): 50,7% Flávio x 49,3% Lula
4. Palver (24/10/2026 - BR-08814/2026): 50,5% Flávio x 49,5% Lula
5. Futura/Apex (24/10/2026 - BR-07412/2026): 51,1% Flávio x 48,9% Lula
6. Gerp (24/10/2026 - BR-09327/2026): 52,0% Flávio x 48,0% Lula
7. RealTime Big Data (23/10/2026 - BR-06190/2026): 52,0% Flávio x 48,0% Lula
8. AtlasIntel (Referência - BR-02418/2026): 51,1% Flávio x 48,9% Lula (51,34% puro / 51,17% c/ abstenção)
===============================================================================
"""

import os
import sys
import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch"
RF_VOTOS_PATH = os.path.join(BASE_DIR, "projecao_rf_votos_2026.csv")
ATLAS_PATH = os.path.join(BASE_DIR, "atlas_com_abstencao_2026.csv")
OUT_SUMMARY_CSV = os.path.join(BASE_DIR, "pesquisas_vespera_2026_com_abstencao.csv")
OUT_UF_CSV = os.path.join(BASE_DIR, "pesquisas_2026_por_uf.csv")

# 1. Load RF 2026 state projections and AtlasIntel baseline
rf_data = pd.read_csv(RF_VOTOS_PATH)
atlas_df = pd.read_csv(ATLAS_PATH)

total_electorate = 158745502
electorate_weights = {
    "SP": 0.2216, "MG": 0.1041, "RJ": 0.0820, "BA": 0.0712, "RS": 0.0543,
    "PR": 0.0538, "PE": 0.0448, "CE": 0.0434, "PA": 0.0388, "SC": 0.0349,
    "MA": 0.0318, "GO": 0.0313, "PB": 0.0196, "ES": 0.0185, "PI": 0.0162,
    "RN": 0.0163, "AM": 0.0167, "MT": 0.0158, "AL": 0.0150, "DF": 0.0141,
    "MS": 0.0126, "SE": 0.0105, "RO": 0.0077, "TO": 0.0067, "AC": 0.0037,
    "AP": 0.0035, "RR": 0.0024
}
w_sum = sum(electorate_weights.values())
electorate_weights = {k: v / w_sum for k, v in electorate_weights.items()}

# Base AtlasIntel state valid shares (Flavio, Lula)
atlas_valid_shares = {
    "SP": (0.578, 0.422), "MG": (0.498, 0.502), "RJ": (0.572, 0.428), "ES": (0.575, 0.425),
    "RS": (0.582, 0.418), "PR": (0.640, 0.360), "SC": (0.690, 0.310),
    "GO": (0.592, 0.408), "MT": (0.655, 0.345), "MS": (0.590, 0.410), "DF": (0.585, 0.415),
    "AM": (0.485, 0.515), "PA": (0.468, 0.532), "AC": (0.675, 0.325), "RO": (0.692, 0.308),
    "RR": (0.742, 0.258), "AP": (0.490, 0.510), "TO": (0.550, 0.450),
    "BA": (0.348, 0.652), "PE": (0.375, 0.625), "CE": (0.332, 0.668), "MA": (0.340, 0.660),
    "PB": (0.370, 0.630), "RN": (0.392, 0.608), "AL": (0.435, 0.565), "PI": (0.280, 0.720),
    "SE": (0.385, 0.615)
}

# Precompute uniform valid votes and RF abstention-adjusted valid votes per state directly from atlas_df & rf_data
atlas_lookup = atlas_df.set_index("uf").to_dict(orient="index")
state_meta = {}
for _, r in rf_data.iterrows():
    uf = r["uf"]
    arow = atlas_lookup[uf]
    validos_sem_filtro = float(arow["votos_flavio_puro"] + arow["votos_lula_puro"])
    validos_proj = int(arow["validos_proj"])
    state_meta[uf] = {
        "uf": uf,
        "estado": r["estado"],
        "regiao": r["regiao"],
        "teve_2t_gov": r["teve_2t_gov"],
        "abst_1t": float(r["abst_1t"]),
        "abst_rf": float(r["abst_2t_rf"]),
        "delta_rf": float(r["delta_rf"]),
        "validos_sem_filtro": validos_sem_filtro,
        "validos_proj": validos_proj,
        "atlas_f": atlas_valid_shares[uf][0]
    }

# Regional baseline of Flavio in AtlasIntel (under uniform turnout)
reg_atlas_f = {}
for reg in ["Sudeste", "Nordeste", "Sul", "Norte", "Centro-Oeste"]:
    ufs_reg = [u for u, m in state_meta.items() if m["regiao"] == reg]
    num = sum(state_meta[u]["validos_sem_filtro"] * state_meta[u]["atlas_f"] for u in ufs_reg)
    den = sum(state_meta[u]["validos_sem_filtro"] for u in ufs_reg)
    reg_atlas_f[reg] = num / den

# Catalog of 2026 2nd Round Polls released today (24/10/2026) and yesterday (23/10/2026)
polls_2026 = [
    {
        "id": "datafolha",
        "instituto": "Datafolha",
        "contratante": "Folha de S.Paulo / TV Globo",
        "registro_tse": "BR-09540/2026",
        "data_divulgacao": "24/10/2026",
        "amostra": 5106,
        "margem_erro": 2.0,
        "metodologia": "Presencial",
        "flavio_total_pct": 48.0,
        "lula_total_pct": 47.0,
        "bn_ind_pct": 5.0,
        "flavio_headline_valid": 51.00,
        "lula_headline_valid": 49.00,
        # Regional shifts relative to baseline (Nordeste slightly stronger for Lula in Datafolha, Sul/CO strong for Flavio)
        "reg_tilts_flavio": {"Sudeste": -0.003, "Nordeste": -0.008, "Sul": +0.004, "Norte": -0.002, "Centro-Oeste": +0.005},
        "use_exact_atlas": False
    },
    {
        "id": "quaest",
        "instituto": "Genial/Quaest",
        "contratante": "Banco Genial",
        "registro_tse": "BR-09158/2026",
        "data_divulgacao": "24/10/2026",
        "amostra": 3000,
        "margem_erro": 2.0,
        "metodologia": "Presencial",
        "flavio_total_pct": 48.0,
        "lula_total_pct": 46.0,
        "bn_ind_pct": 6.0,
        "flavio_headline_valid": 51.00,
        "lula_headline_valid": 49.00,
        "reg_tilts_flavio": {"Sudeste": -0.001, "Nordeste": -0.011, "Sul": +0.008, "Norte": -0.003, "Centro-Oeste": +0.003},
        "use_exact_atlas": False
    },
    {
        "id": "cnt_mda",
        "instituto": "CNT/MDA",
        "contratante": "CNT",
        "registro_tse": "BR-02136/2026",
        "data_divulgacao": "24/10/2026",
        "amostra": 2002,
        "margem_erro": 2.2,
        "metodologia": "Presencial",
        "flavio_total_pct": 46.3,
        "lula_total_pct": 45.0,
        "bn_ind_pct": 8.7,
        "flavio_headline_valid": 50.70,
        "lula_headline_valid": 49.30,
        "reg_tilts_flavio": {"Sudeste": -0.006, "Nordeste": -0.009, "Sul": -0.002, "Norte": -0.005, "Centro-Oeste": -0.003},
        "use_exact_atlas": False
    },
    {
        "id": "palver",
        "instituto": "Palver",
        "contratante": "Palver / Recursos próprios",
        "registro_tse": "BR-08814/2026",
        "data_divulgacao": "24/10/2026",
        "amostra": 2500,
        "margem_erro": 2.0,
        "metodologia": "Digital / Painel",
        "flavio_total_pct": 47.5,
        "lula_total_pct": 46.5,
        "bn_ind_pct": 6.0,
        "flavio_headline_valid": 50.50,
        "lula_headline_valid": 49.50,
        "reg_tilts_flavio": {"Sudeste": -0.009, "Nordeste": -0.008, "Sul": -0.005, "Norte": -0.007, "Centro-Oeste": -0.006},
        "use_exact_atlas": False
    },
    {
        "id": "futura",
        "instituto": "Futura/Apex",
        "contratante": "Apex Partners",
        "registro_tse": "BR-07412/2026",
        "data_divulgacao": "24/10/2026",
        "amostra": 2000,
        "margem_erro": 2.2,
        "metodologia": "CATI (Telefone)",
        "flavio_total_pct": 48.9,
        "lula_total_pct": 46.8,
        "bn_ind_pct": 4.3,
        "flavio_headline_valid": 51.10,
        "lula_headline_valid": 48.90,
        "reg_tilts_flavio": {"Sudeste": +0.001, "Nordeste": -0.005, "Sul": +0.003, "Norte": +0.001, "Centro-Oeste": +0.002},
        "use_exact_atlas": False
    },
    {
        "id": "gerp",
        "instituto": "Gerp",
        "contratante": "Gerp / Recursos próprios",
        "registro_tse": "BR-09327/2026",
        "data_divulgacao": "24/10/2026",
        "amostra": 2000,
        "margem_erro": 2.0,
        "metodologia": "Presencial",
        "flavio_total_pct": 49.0,
        "lula_total_pct": 46.0,
        "bn_ind_pct": 5.0,
        "flavio_headline_valid": 52.00,
        "lula_headline_valid": 48.00,
        "reg_tilts_flavio": {"Sudeste": +0.009, "Nordeste": +0.005, "Sul": +0.007, "Norte": +0.006, "Centro-Oeste": +0.008},
        "use_exact_atlas": False
    },
    {
        "id": "realtime",
        "instituto": "RealTime Big Data",
        "contratante": "Record TV / Recursos próprios",
        "registro_tse": "BR-06190/2026",
        "data_divulgacao": "23/10/2026",
        "amostra": 2500,
        "margem_erro": 2.0,
        "metodologia": "CATI / Mista",
        "flavio_total_pct": 49.0,
        "lula_total_pct": 45.0,
        "bn_ind_pct": 6.0,
        "flavio_headline_valid": 52.00,
        "lula_headline_valid": 48.00,
        "reg_tilts_flavio": {"Sudeste": +0.010, "Nordeste": +0.003, "Sul": +0.008, "Norte": +0.007, "Centro-Oeste": +0.009},
        "use_exact_atlas": False
    },
    {
        "id": "atlasintel",
        "instituto": "AtlasIntel (Ref.)",
        "contratante": "AtlasIntel / Recursos próprios",
        "registro_tse": "BR-02418/2026",
        "data_divulgacao": "24/10/2026",
        "amostra": 7500,
        "margem_erro": 1.0,
        "metodologia": "Digital (RDR)",
        "flavio_total_pct": 49.8,
        "lula_total_pct": 47.6,
        "bn_ind_pct": 2.6,
        "flavio_headline_valid": 51.10,
        "lula_headline_valid": 48.90,
        "reg_tilts_flavio": {"Sudeste": 0.0, "Nordeste": 0.0, "Sul": 0.0, "Norte": 0.0, "Centro-Oeste": 0.0},
        "use_exact_atlas": True
    }
]

summary_rows = []
uf_rows = []

for p in polls_2026:
    # Step 1: Compute calibrated state shares (pct_f_uf, pct_l_uf)
    uf_shares = {}
    if p["use_exact_atlas"]:
        for uf in state_meta:
            uf_shares[uf] = atlas_valid_shares[uf][0]
    else:
        # Apply regional tilts first
        raw_uf_f = {}
        for uf, meta in state_meta.items():
            reg = meta["regiao"]
            raw_uf_f[uf] = meta["atlas_f"] + p["reg_tilts_flavio"][reg]
        # Calibrate additive offset so that uniform-turnout national average equals exact headline valid %
        cur_nat_f = sum(state_meta[u]["validos_sem_filtro"] * raw_uf_f[u] for u in state_meta) / sum(
            state_meta[u]["validos_sem_filtro"] for u in state_meta
        )
        target_nat_f = p["flavio_headline_valid"] / 100.0
        offset = target_nat_f - cur_nat_f
        for uf in state_meta:
            uf_shares[uf] = round(min(0.85, max(0.15, raw_uf_f[uf] + offset)), 4)

    # Step 2: Calculate Cenario 1 (Puro / Uniform Abstention) & Cenario 2 (RF Abstention Filter) & Cenario 2B (RF + Likely Voter)
    tot_f_puro = 0
    tot_l_puro = 0
    tot_f_proj = 0
    tot_l_proj = 0
    tot_f_lv = 0
    tot_l_lv = 0

    for _, r in rf_data.iterrows():
        uf = r["uf"]
        meta = state_meta[uf]
        pct_f = uf_shares[uf]
        pct_l = 1.0 - pct_f

        # Cenario 1: Puro (Sem filtro de abstencao estadual)
        vf_puro = round(meta["validos_sem_filtro"] * pct_f)
        vl_puro = round(meta["validos_sem_filtro"] * pct_l)

        # Cenario 2: Com Filtro de Abstencao Estadual RF (replicacao exata de apply_abstention_to_atlas.py)
        validos_proj = meta["validos_proj"]
        vf_proj = round(validos_proj * pct_f)
        vl_proj = validos_proj - vf_proj if not p["use_exact_atlas"] else round(validos_proj * pct_l)

        # Cenario 2B: Com Filtro de Abstencao Estadual RF + Ajuste Marginal Likely Voter (0.18 * delta_rf)
        lv_shift = 0.0018 * meta["delta_rf"]
        pct_f_lv = min(0.90, max(0.10, pct_f + lv_shift))
        vf_lv = round(validos_proj * pct_f_lv)
        vl_lv = validos_proj - vf_lv

        tot_f_puro += vf_puro
        tot_l_puro += vl_puro
        tot_f_proj += vf_proj
        tot_l_proj += vl_proj
        tot_f_lv += vf_lv
        tot_l_lv += vl_lv

        uf_rows.append({
            "poll_id": p["id"],
            "instituto": p["instituto"],
            "uf": uf,
            "estado": meta["estado"],
            "regiao": meta["regiao"],
            "teve_2t_gov": meta["teve_2t_gov"],
            "abst_1t": meta["abst_1t"],
            "abst_rf": meta["abst_rf"],
            "delta_rf": meta["delta_rf"],
            "pct_flavio_poll": round(pct_f * 100.0, 2),
            "pct_lula_poll": round(pct_l * 100.0, 2),
            "validos_proj": validos_proj,
            "votos_flavio_puro": vf_puro,
            "votos_lula_puro": vl_puro,
            "votos_flavio_proj": vf_proj,
            "votos_lula_proj": vl_proj,
            "saldo_abst_flavio": vf_proj - vf_puro,
            "saldo_abst_lula": vl_proj - vl_puro,
            "votos_flavio_lv": vf_lv,
            "votos_lula_lv": vl_lv
        })

    tot_v_puro = tot_f_puro + tot_l_puro
    tot_v_proj = tot_f_proj + tot_l_proj
    tot_v_lv = tot_f_lv + tot_l_lv

    pct_f_puro_calc = round(tot_f_puro / tot_v_puro * 100.0, 2)
    pct_l_puro_calc = round(tot_l_puro / tot_v_puro * 100.0, 2)

    pct_f_proj_calc = round(tot_f_proj / tot_v_proj * 100.0, 2)
    pct_l_proj_calc = round(tot_l_proj / tot_v_proj * 100.0, 2)

    pct_f_lv_calc = round(tot_f_lv / tot_v_lv * 100.0, 2)
    pct_l_lv_calc = round(tot_l_lv / tot_v_lv * 100.0, 2)

    diff_votos_puro = tot_f_puro - tot_l_puro
    diff_votos_proj = tot_f_proj - tot_l_proj
    diff_votos_lv = tot_f_lv - tot_l_lv

    impacto_margem_votos = diff_votos_proj - diff_votos_puro
    impacto_flavio_pp = round(pct_f_proj_calc - pct_f_puro_calc, 2)

    # Check regional totals under RF abstention
    uf_sub = [r for r in uf_rows if r["poll_id"] == p["id"]]
    reg_pcts = {}
    for reg in ["Sudeste", "Nordeste", "Sul", "Norte", "Centro-Oeste"]:
        r_f = sum(x["votos_flavio_proj"] for x in uf_sub if x["regiao"] == reg)
        r_v = sum(x["validos_proj"] for x in uf_sub if x["regiao"] == reg)
        reg_pcts[reg] = round(r_f / r_v * 100.0, 1)

    summary_rows.append({
        "poll_id": p["id"],
        "instituto": p["instituto"],
        "contratante": p["contratante"],
        "registro_tse": p["registro_tse"],
        "data_divulgacao": p["data_divulgacao"],
        "amostra": p["amostra"],
        "margem_erro": p["margem_erro"],
        "metodologia": p["metodologia"],
        "flavio_total_pct": p["flavio_total_pct"],
        "lula_total_pct": p["lula_total_pct"],
        "bn_ind_pct": p["bn_ind_pct"],
        "flavio_headline_valid": p["flavio_headline_valid"],
        "lula_headline_valid": p["lula_headline_valid"],
        "pct_flavio_puro": pct_f_puro_calc,
        "pct_lula_puro": pct_l_puro_calc,
        "votos_flavio_puro": tot_f_puro,
        "votos_lula_puro": tot_l_puro,
        "vantagem_flavio_puro_votos": diff_votos_puro,
        "vantagem_flavio_puro_pp": round(pct_f_puro_calc - pct_l_puro_calc, 2),
        "pct_flavio_abst_rf": pct_f_proj_calc,
        "pct_lula_abst_rf": pct_l_proj_calc,
        "votos_flavio_abst_rf": tot_f_proj,
        "votos_lula_abst_rf": tot_l_proj,
        "vantagem_flavio_abst_rf_votos": diff_votos_proj,
        "vantagem_flavio_abst_rf_pp": round(pct_f_proj_calc - pct_l_proj_calc, 2),
        "impacto_abst_flavio_pp": impacto_flavio_pp,
        "impacto_abst_margem_votos": impacto_margem_votos,
        "pct_flavio_lv": pct_f_lv_calc,
        "pct_lula_lv": pct_l_lv_calc,
        "votos_flavio_lv": tot_f_lv,
        "votos_lula_lv": tot_l_lv,
        "vantagem_flavio_lv_votos": diff_votos_lv,
        "vantagem_flavio_lv_pp": round(pct_f_lv_calc - pct_l_lv_calc, 2),
        "flavio_sudeste_pct": reg_pcts["Sudeste"],
        "flavio_nordeste_pct": reg_pcts["Nordeste"],
        "flavio_sul_pct": reg_pcts["Sul"],
        "flavio_norte_pct": reg_pcts["Norte"],
        "flavio_co_pct": reg_pcts["Centro-Oeste"]
    })

df_sum = pd.DataFrame(summary_rows)
df_uf = pd.DataFrame(uf_rows)

df_sum.to_csv(OUT_SUMMARY_CSV, index=False, encoding="utf-8")
df_uf.to_csv(OUT_UF_CSV, index=False, encoding="utf-8")

print("=" * 125)
print("  ANÁLISE 2º TURNO 2026: PESQUISAS DE HOJE (24/10/2026) PONDERADAS PELA ABSTENÇÃO ESTADUAL (RANDOM FOREST)  ")
print("=" * 125)
header = (
    f"{'Instituto':18} | {'Reg. TSE':13} | {'Bruto (F x L)':15} | "
    f"{'C/ Abst RF (F x L)':18} | {'Votos Flávio (RF)':17} | {'Votos Lula (RF)':15} | "
    f"{'Vantagem Flávio (RF)':22} | {'Efeito Abst. (Margem)':21}"
)
print(header)
print("-" * 125)
for _, r in df_sum.iterrows():
    bruto_str = f"{r['flavio_headline_valid']:.1f}% x {r['lula_headline_valid']:.1f}%"
    rf_str = f"{r['pct_flavio_abst_rf']:.2f}% x {r['pct_lula_abst_rf']:.2f}%"
    vf_str = f"{int(r['votos_flavio_abst_rf']):,}".replace(",", ".")
    vl_str = f"{int(r['votos_lula_abst_rf']):,}".replace(",", ".")
    vant_str = f"+{int(r['vantagem_flavio_abst_rf_votos']):,} (+{r['vantagem_flavio_abst_rf_pp']:.2f}pp)".replace(",", ".")
    imp_str = f"{int(r['impacto_abst_margem_votos']):+,} ({r['impacto_abst_flavio_pp']:+.2f}pp F)".replace(",", ".")
    print(f"{r['instituto']:18} | {r['registro_tse']:13} | {bruto_str:15} | {rf_str:18} | {vf_str:17} | {vl_str:15} | {vant_str:22} | {imp_str:21}")

print("-" * 125)
# Media das pesquisas de hoje
mean_f_bruto = df_sum["flavio_headline_valid"].mean()
mean_l_bruto = df_sum["lula_headline_valid"].mean()
mean_f_rf = df_sum["pct_flavio_abst_rf"].mean()
mean_l_rf = df_sum["pct_lula_abst_rf"].mean()
mean_vf_rf = int(df_sum["votos_flavio_abst_rf"].mean())
mean_vl_rf = int(df_sum["votos_lula_abst_rf"].mean())
mean_vant_rf = mean_vf_rf - mean_vl_rf
print(
    f"{'MÉDIA 8 INSTITUTOS':18} | {'CONSENSO 24/10':13} | "
    f"{mean_f_bruto:.2f}% x {mean_l_bruto:.2f}% | "
    f"{mean_f_rf:.2f}% x {mean_l_rf:.2f}%  | "
    f"{mean_vf_rf:,}".replace(",", ".") + f"      | "
    f"{mean_vl_rf:,}".replace(",", ".") + f"    | "
    f"+{mean_vant_rf:,} (+{mean_f_rf - mean_l_rf:.2f}pp)".replace(",", ".") + " | "
    f"{int(df_sum['impacto_abst_margem_votos'].mean()):+,} votos".replace(",", ".")
)
print("=" * 125)
