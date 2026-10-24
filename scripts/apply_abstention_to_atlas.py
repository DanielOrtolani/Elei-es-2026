import pandas as pd
import numpy as np

# 1. Load the Random Forest projected abstention by state
rf_data = pd.read_csv(r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\projecao_rf_votos_2026.csv")

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

# 2. AtlasIntel 19/10/2026 Poll Data (BR-02418/2026)
# National valid votes: Flavio 51.1%, Lula 48.9%
# Regional valid breakdown (AtlasIntel):
# Nordeste: Lula 64.0%, Flavio 36.0%
# Sul: Flavio 62.2%, Lula 37.8%
# Centro-Oeste: Flavio 57.9%, Lula 42.1%
# Sudeste: Flavio 56.6%, Lula 43.4% (com MG em empate técnico: Lula ~50.2%, Flavio ~49.8%; SP Flavio ~57.8%, RJ Flavio ~57.0%)
# Norte: Flavio 51.1%, Lula 48.9%

# State-level calibrated valid percentages from AtlasIntel regional matrix:
atlas_valid_shares = {
    # Sudeste
    "SP": (0.578, 0.422), # Flavio, Lula
    "MG": (0.498, 0.502), # Atlas indicates Lula very competitive in MG
    "RJ": (0.572, 0.428),
    "ES": (0.575, 0.425),
    
    # Sul
    "RS": (0.582, 0.418),
    "PR": (0.640, 0.360),
    "SC": (0.690, 0.310),
    
    # Centro-Oeste
    "GO": (0.592, 0.408),
    "MT": (0.655, 0.345),
    "MS": (0.590, 0.410),
    "DF": (0.585, 0.415),
    
    # Norte
    "AM": (0.485, 0.515),
    "PA": (0.468, 0.532),
    "AC": (0.675, 0.325),
    "RO": (0.692, 0.308),
    "RR": (0.742, 0.258),
    "AP": (0.490, 0.510),
    "TO": (0.550, 0.450),
    
    # Nordeste
    "BA": (0.348, 0.652),
    "PE": (0.375, 0.625),
    "CE": (0.332, 0.668),
    "MA": (0.340, 0.660),
    "PB": (0.370, 0.630),
    "RN": (0.392, 0.608),
    "AL": (0.435, 0.565),
    "PI": (0.280, 0.720),
    "SE": (0.385, 0.615)
}

rows = []
for _, r in rf_data.iterrows():
    uf = r["uf"]
    estado = r["estado"]
    regiao = r["regiao"]
    teve_gov = r["teve_2t_gov"]
    abst_1t = r["abst_1t"]
    abst_rf = r["abst_2t_rf"]
    
    eleitorado = round(electorate_weights[uf] * total_electorate)
    
    # Intenção da pesquisa (AtlasIntel)
    pct_f_atlas, pct_l_atlas = atlas_valid_shares[uf]
    
    # CENÁRIO 1: Pesquisa pura sem filtro de abstenção (se todos votassem igual)
    # Votos válidos teóricos uniformes (ex: 78.9% nacional):
    validos_sem_filtro = eleitorado * (1 - 0.2108) * 0.974
    votos_f_puro = round(validos_sem_filtro * pct_f_atlas)
    votos_l_puro = round(validos_sem_filtro * pct_l_atlas)
    
    # CENÁRIO 2: Pesquisa COM PONDERAÇÃO PELA ABSTENÇÃO PROJETADA (Likely Voter Model)
    # Votantes reais esperados pelo modelo RF:
    votantes_proj = eleitorado * (1 - abst_rf / 100.0)
    # Votos válidos esperados (Atlas indica 2.6% brancos/nulos):
    validos_proj = round(votantes_proj * 0.974)
    
    votos_f_proj = round(validos_proj * pct_f_atlas)
    votos_l_proj = round(validos_proj * pct_l_atlas)
    
    # Impacto da abstenção sobre o resultado (saldo)
    saldo_abst_f = votos_f_proj - votos_f_puro
    saldo_abst_l = votos_l_proj - votos_l_puro
    
    rows.append({
        "uf": uf,
        "estado": estado,
        "regiao": regiao,
        "teve_2t_gov": teve_gov,
        "abst_rf": abst_rf,
        "pct_flavio_atlas": round(pct_f_atlas * 100, 1),
        "pct_lula_atlas": round(pct_l_atlas * 100, 1),
        "validos_proj": validos_proj,
        "votos_flavio_proj": votos_f_proj,
        "votos_lula_proj": votos_l_proj,
        "votos_flavio_puro": votos_f_puro,
        "votos_lula_puro": votos_l_puro
    })

res_df = pd.DataFrame(rows).sort_values(by="pct_flavio_atlas", ascending=False)

# Totais nacionais
total_f_puro = res_df["votos_flavio_puro"].sum()
total_l_puro = res_df["votos_lula_puro"].sum()
total_v_puro = total_f_puro + total_l_puro

total_f_proj = res_df["votos_flavio_proj"].sum()
total_l_proj = res_df["votos_lula_proj"].sum()
total_v_proj = total_f_proj + total_l_proj

print("=== ATLASINTEL 19/10/2026 - CENÁRIO PURO (SEM PONDERAÇÃO DE ABSTENÇÃO) ===")
print(f"Flávio Bolsonaro: {total_f_puro:,} ({total_f_puro / total_v_puro * 100:.2f}%)")
print(f"Lula:             {total_l_puro:,} ({total_l_puro / total_v_puro * 100:.2f}%)")
print(f"Diferença:        {total_f_puro - total_l_puro:,} votos (+{ (total_f_puro - total_l_puro) / total_v_puro * 100:.2f} p.p.)")

print("\n=== ATLASINTEL 19/10/2026 - APLICANDO A ABSTENÇÃO PROJETADA (RANDOM FOREST) ===")
print(f"Flávio Bolsonaro: {total_f_proj:,} ({total_f_proj / total_v_proj * 100:.2f}%)")
print(f"Lula:             {total_l_proj:,} ({total_l_proj / total_v_proj * 100:.2f}%)")
print(f"Diferença:        {total_f_proj - total_l_proj:,} votos (+{ (total_f_proj - total_l_proj) / total_v_proj * 100:.2f} p.p.)")

print("\nImpacto da Abstenção Diferencial:")
pct_diff_puro = (total_f_puro / total_v_puro) * 100
pct_diff_proj = (total_f_proj / total_v_proj) * 100
print(f"Variação percentual para Flávio: {pct_diff_proj - pct_diff_puro:+.2f} p.p.")

# Save to CSV
out_csv = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\atlas_com_abstencao_2026.csv"
res_df.to_csv(out_csv, index=False)

# Export markdown table
lines = []
for _, r in res_df.iterrows():
    f_proj = f"{int(r['votos_flavio_proj']):,}".replace(",", ".")
    l_proj = f"{int(r['votos_lula_proj']):,}".replace(",", ".")
    val_proj = f"{int(r['validos_proj']):,}".replace(",", ".")
    lines.append(f"| **{r['uf']}** | {r['estado']} | {r['teve_2t_gov']} | {r['abst_rf']:.2f}% | {r['pct_flavio_atlas']:.1f}% | {r['pct_lula_atlas']:.1f}% | {val_proj} | **{f_proj}** | **{l_proj}** |")

with open(r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\tabela_atlas_markdown.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Completed successfully.")
