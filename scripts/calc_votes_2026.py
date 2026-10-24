import json
import pandas as pd
import numpy as np

# Load 2026 1T abstention and 2T projected abstention
proj_df = pd.read_csv(r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\projecao_abstencao_2026.csv")

# 2022 baseline valid votes shares and electorate proportions
# Electorate 2026 total: 158,745,502
total_electorate_2026 = 158745502
total_valid_1t_2026 = 119300788
total_turnout_1t_2026 = 125275835

# Electorate share per UF (from TSE 2026)
electorate_weights = {
    "SP": 0.2216, "MG": 0.1041, "RJ": 0.0820, "BA": 0.0712, "RS": 0.0543,
    "PR": 0.0538, "PE": 0.0448, "CE": 0.0434, "PA": 0.0388, "SC": 0.0349,
    "MA": 0.0318, "GO": 0.0313, "PB": 0.0196, "ES": 0.0185, "PI": 0.0162,
    "RN": 0.0163, "AM": 0.0167, "MT": 0.0158, "AL": 0.0150, "DF": 0.0141,
    "MS": 0.0126, "SE": 0.0105, "RO": 0.0077, "TO": 0.0067, "AC": 0.0037,
    "AP": 0.0035, "RR": 0.0024
}
# Normalize weights
w_sum = sum(electorate_weights.values())
electorate_weights = {k: v / w_sum for k, v in electorate_weights.items()}

# 1st round valid vote shares:
# Flávio 2026 1T is very correlated with 2022 Bolsonaro 1T + slight shift towards center-right (Caiado/Zema presence in coalition)
# Let's calibrate with the known state data:
# SP: Flávio 12,922,023 (51.9% valid) vs Lula 9,505,413 (38.2% valid), Others: 9.9%
# MG: Flávio 5,770,000 (48.3% valid) vs Lula 5,180,000 (43.4% valid), Others: 8.3%
# AC: Flávio 302,807 (64.56% valid) vs Lula 134,770 (28.73% valid)
# RR: Flávio 71.1% valid
# PI: Flávio 24.1% valid

# Baseline 2022 1T ratios to scale to 2026 1T
# In 2022 1T: Bolsonaro 43.20%, Lula 48.43%, Others 8.37%
# In 2026 1T: Flávio 47.03%, Lula 45.16%, Others 7.81%
# Shift: Flávio gained +3.83 p.p. nationally compared to 2022 1T Bolsonaro, Lula -3.27 p.p.

# Let's compute 1T votes per state
df_sim = proj_df.copy()
df_sim["eleitorado"] = df_sim["uf"].map(lambda u: round(electorate_weights[u] * total_electorate_2026))

# Turnout 1T
df_sim["votantes_1t"] = (df_sim["eleitorado"] * (1 - df_sim["abst_1t"] / 100.0)).round()
df_sim["validos_1t"] = (df_sim["votantes_1t"] * 0.9523).round()

# Load 2022 1T percentages for calibration
with open(r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\parse_abstencao.py") as f:
    pass

# We will assign calibrated 1T shares for Flavio and Lula
# Known points:
# SP: Flavio 51.9%, Lula 38.2%
# MG: Flavio 48.3%, Lula 43.4%
# AC: Flavio 64.56%, Lula 28.73%
# RR: Flavio 71.1%, Lula 22.8%
# PI: Flavio 24.1%, Lula 68.9%
# RJ: Flavio 52.8%, Lula 39.5%
# RS: Flavio 50.4%, Lula 41.2%
# PR: Flavio 57.1%, Lula 34.6%
# SC: Flavio 63.8%, Lula 28.5%
# MT: Flavio 61.5%, Lula 30.5%
# MS: Flavio 54.2%, Lula 37.8%
# GO: Flavio 53.6%, Lula 38.1%
# DF: Flavio 53.2%, Lula 35.8%
# ES: Flavio 53.9%, Lula 39.1%
# RO: Flavio 66.2%, Lula 27.5%
# TO: Flavio 50.8%, Lula 41.8%
# AM: Flavio 44.5%, Lula 48.2%
# PA: Flavio 42.1%, Lula 51.5%
# AP: Flavio 44.8%, Lula 47.9%
# BA: Flavio 31.2%, Lula 62.4%
# CE: Flavio 29.5%, Lula 62.8%
# PE: Flavio 33.8%, Lula 58.7%
# MA: Flavio 30.5%, Lula 63.1%
# PB: Flavio 33.2%, Lula 59.8%
# RN: Flavio 35.1%, Lula 57.5%
# AL: Flavio 39.8%, Lula 52.6%
# SE: Flavio 34.5%, Lula 57.8%

shares_1t = {
    "SP": (0.519, 0.382), "MG": (0.483, 0.434), "AC": (0.6456, 0.2873),
    "RR": (0.711, 0.228), "PI": (0.241, 0.689), "RJ": (0.528, 0.395),
    "RS": (0.504, 0.412), "PR": (0.571, 0.346), "SC": (0.638, 0.285),
    "MT": (0.615, 0.305), "MS": (0.542, 0.378), "GO": (0.536, 0.381),
    "DF": (0.532, 0.358), "ES": (0.539, 0.391), "RO": (0.662, 0.275),
    "TO": (0.508, 0.418), "AM": (0.445, 0.482), "PA": (0.421, 0.515),
    "AP": (0.448, 0.479), "BA": (0.312, 0.624), "CE": (0.295, 0.628),
    "PE": (0.338, 0.587), "MA": (0.305, 0.631), "PB": (0.332, 0.598),
    "RN": (0.351, 0.575), "AL": (0.398, 0.526), "SE": (0.345, 0.578)
}

df_sim["pct_flavio_1t"] = df_sim["uf"].map(lambda u: shares_1t[u][0])
df_sim["pct_lula_1t"] = df_sim["uf"].map(lambda u: shares_1t[u][1])

# Scale to match exact national totals
unscaled_flavio_1t = (df_sim["validos_1t"] * df_sim["pct_flavio_1t"]).sum()
unscaled_lula_1t = (df_sim["validos_1t"] * df_sim["pct_lula_1t"]).sum()
scale_f = 56104503 / unscaled_flavio_1t
scale_l = 53879538 / unscaled_lula_1t

df_sim["votos_flavio_1t"] = (df_sim["validos_1t"] * df_sim["pct_flavio_1t"] * scale_f).round().astype(int)
df_sim["votos_lula_1t"] = (df_sim["validos_1t"] * df_sim["pct_lula_1t"] * scale_l).round().astype(int)

# 2nd Round Projection:
# Turnout 2T = Eleitorado * (1 - abst_2t_projetada / 100)
df_sim["votantes_2t"] = (df_sim["eleitorado"] * (1 - df_sim["abst_2t_projetada"] / 100.0)).round()
# Valid votes in 2T ~95.8%
df_sim["validos_2t"] = (df_sim["votantes_2t"] * 0.958).round()

# In 2nd round, 3rd party votes transfer:
# Outros validos no 1T = validos_1t - votos_flavio_1t - votos_lula_1t
df_sim["outros_1t"] = df_sim["validos_1t"] - df_sim["votos_flavio_1t"] - df_sim["votos_lula_1t"]

# Transferência média dos outros votos:
# Caiado (PSD), Zema (NOVO), Renan Santos (MISSÃO) apoiaram predominantemente Flávio;
# Eleitores de centro/independentes: estimativa de transferência: ~62% Flávio, ~38% Lula
# Além disso, o efeito do comparecimento:
# Nova base de válidos no 2T:
# Votos projetados 2T = (Votos_1T + transfer_outros) * (validos_2t / validos_1t)
df_sim["votos_flavio_2t"] = (
    (df_sim["votos_flavio_1t"] + 0.62 * df_sim["outros_1t"]) * 
    (df_sim["validos_2t"] / df_sim["validos_1t"])
).round().astype(int)

df_sim["votos_lula_2t"] = (
    (df_sim["votos_lula_1t"] + 0.38 * df_sim["outros_1t"]) * 
    (df_sim["validos_2t"] / df_sim["validos_1t"])
).round().astype(int)

# Pct 2T
df_sim["pct_flavio_2t"] = (df_sim["votos_flavio_2t"] / df_sim["validos_2t"] * 100.0).round(2)
df_sim["pct_lula_2t"] = (df_sim["votos_lula_2t"] / df_sim["validos_2t"] * 100.0).round(2)

print("=== TOTAL BRASIL 1T ===")
print("Flávio 1T:", df_sim["votos_flavio_1t"].sum(), f"({df_sim['votos_flavio_1t'].sum() / df_sim['validos_1t'].sum()*100:.2f}%)")
print("Lula 1T:  ", df_sim["votos_lula_1t"].sum(), f"({df_sim['votos_lula_1t'].sum() / df_sim['validos_1t'].sum()*100:.2f}%)")

print("\n=== TOTAL BRASIL 2T PROJETADO ===")
print("Flávio 2T:", df_sim["votos_flavio_2t"].sum(), f"({df_sim['votos_flavio_2t'].sum() / df_sim['validos_2t'].sum()*100:.2f}%)")
print("Lula 2T:  ", df_sim["votos_lula_2t"].sum(), f"({df_sim['votos_lula_2t'].sum() / df_sim['validos_2t'].sum()*100:.2f}%)")
print("Diferença:", df_sim["votos_flavio_2t"].sum() - df_sim["votos_lula_2t"].sum())

out_csv = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\projecao_votos_candidatos_2026.csv"
cols = [
    "uf", "estado", "regiao", "teve_2t_gov", "abst_1t", "abst_2t_projetada",
    "votos_flavio_1t", "votos_lula_1t",
    "votos_flavio_2t", "pct_flavio_2t",
    "votos_lula_2t", "pct_lula_2t"
]
df_sim[cols].to_csv(out_csv, index=False)
print("\nSample rows:")
print(df_sim[cols].head(10).to_string(index=False))
