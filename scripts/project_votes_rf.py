import json
import pandas as pd
import numpy as np

# Load 2026 1T baseline data and state info
data_1t_path = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\projecao_votos_candidatos_2026.csv"
df_1t = pd.read_csv(data_1t_path)

# Load trained dataset to retrain/predict with Random Forest
hist_data_path = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\dataset_regressao.csv"
df_hist = pd.read_csv(hist_data_path)

from sklearn.ensemble import RandomForestRegressor

# Prepare feature matrices
uf_dummies_hist = pd.get_dummies(df_hist["uf"], prefix="UF", dtype=float)
ano_dummies_hist = pd.get_dummies(df_hist["ano"].astype(str), prefix="Ano", drop_first=True, dtype=float)

X_hist = pd.concat([
    uf_dummies_hist,
    ano_dummies_hist,
    df_hist[["teve_2t_gov", "abst_1t"]]
], axis=1)
y_hist = df_hist["delta_abst"]

# Fit Random Forest
rf = RandomForestRegressor(
    n_estimators=300,
    max_depth=5,
    min_samples_split=3,
    min_samples_leaf=2,
    random_state=42
)
rf.fit(X_hist, y_hist)

# Build 2026 feature matrix for prediction
# For 2026, since 2026 is an unobserved year in training, we represent its macroeconomic baseline
# 2026 1T national abstention (21.08%) is between 2018 (20.33%) and 2022 (20.95%)
# In ano_dummies, we use weighted average of 2018 and 2022 coefficients, or evaluate with 2022 baseline
# Let's inspect the two scenarios or blend (0.5 * Ano_2018 + 0.5 * Ano_2022):
all_cols = X_hist.columns

records = []
total_electorate = 158745502

for _, r in df_1t.iterrows():
    uf = r["uf"]
    abst_1t = r["abst_1t"]
    tem_gov = 1.0 if r["teve_2t_gov"] == "Sim" else 0.0
    
    # Create row for RF
    row = {c: 0.0 for c in all_cols}
    if f"UF_{uf}" in row:
        row[f"UF_{uf}"] = 1.0
    row["teve_2t_gov"] = tem_gov
    row["abst_1t"] = abst_1t
    # 2026 dummy weights:
    if "Ano_2018" in row: row["Ano_2018"] = 0.3
    if "Ano_2022" in row: row["Ano_2022"] = 0.7
    
    row_df = pd.DataFrame([row])
    delta_rf = rf.predict(row_df)[0]
    
    # Bound delta to reasonable range based on history
    abst_2t_rf = max(10.0, min(35.0, abst_1t + delta_rf))
    
    records.append({
        "uf": uf,
        "delta_rf": round(delta_rf, 2),
        "abst_2t_rf": round(abst_2t_rf, 2)
    })

rf_proj_df = pd.DataFrame(records)
df_merged = df_1t.merge(rf_proj_df, on="uf")

# Compute 2T turnouts and votes under Random Forest
# Electorate
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

df_merged["eleitorado"] = df_merged["uf"].map(lambda u: round(electorate_weights[u] * total_electorate))
df_merged["votantes_2t_rf"] = (df_merged["eleitorado"] * (1 - df_merged["abst_2t_rf"] / 100.0)).round()
df_merged["validos_2t_rf"] = (df_merged["votantes_2t_rf"] * 0.958).round()

# 1T validos
df_merged["votantes_1t"] = (df_merged["eleitorado"] * (1 - df_merged["abst_1t"] / 100.0)).round()
df_merged["validos_1t"] = (df_merged["votantes_1t"] * 0.9523).round()
df_merged["outros_1t"] = df_merged["validos_1t"] - df_merged["votos_flavio_1t"] - df_merged["votos_lula_1t"]

# Projected 2T votes with RF abstention:
df_merged["votos_flavio_2t_rf"] = (
    (df_merged["votos_flavio_1t"] + 0.62 * df_merged["outros_1t"]) * 
    (df_merged["validos_2t_rf"] / df_merged["validos_1t"])
).round().astype(int)

df_merged["votos_lula_2t_rf"] = (
    (df_merged["votos_lula_1t"] + 0.38 * df_merged["outros_1t"]) * 
    (df_merged["validos_2t_rf"] / df_merged["validos_1t"])
).round().astype(int)

df_merged["pct_flavio_2t_rf"] = (df_merged["votos_flavio_2t_rf"] / df_merged["validos_2t_rf"] * 100.0).round(2)
df_merged["pct_lula_2t_rf"] = (df_merged["votos_lula_2t_rf"] / df_merged["validos_2t_rf"] * 100.0).round(2)

# Sort by Flávio 2T % descending
df_merged = df_merged.sort_values(by="pct_flavio_2t_rf", ascending=False)

print("=== TOTAL BRASIL 2T (RANDOM FOREST PROJECTION) ===")
total_f_2t = df_merged["votos_flavio_2t_rf"].sum()
total_l_2t = df_merged["votos_lula_2t_rf"].sum()
total_v_2t = df_merged["validos_2t_rf"].sum()
print(f"Flávio Bolsonaro: {total_f_2t:,} ({total_f_2t / total_v_2t * 100:.2f}%)")
print(f"Lula:             {total_l_2t:,} ({total_l_2t / total_v_2t * 100:.2f}%)")
print(f"Diferença:        {total_f_2t - total_l_2t:,} votos")

# Export table
out_csv = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\projecao_rf_votos_2026.csv"
export_cols = [
    "uf", "estado", "regiao", "teve_2t_gov", "abst_1t", "abst_2t_rf", "delta_rf",
    "votos_flavio_1t", "votos_lula_1t",
    "votos_flavio_2t_rf", "pct_flavio_2t_rf",
    "votos_lula_2t_rf", "pct_lula_2t_rf"
]
df_merged[export_cols].to_csv(out_csv, index=False)

# Export markdown text
lines = []
for _, r in df_merged.iterrows():
    f1 = f"{int(r['votos_flavio_1t']):,}".replace(",", ".")
    l1 = f"{int(r['votos_lula_1t']):,}".replace(",", ".")
    f2 = f"{int(r['votos_flavio_2t_rf']):,}".replace(",", ".")
    l2 = f"{int(r['votos_lula_2t_rf']):,}".replace(",", ".")
    d_sign = f"+{r['delta_rf']:.2f}%" if r['delta_rf'] >= 0 else f"{r['delta_rf']:.2f}%"
    lines.append(f"| **{r['uf']}** | {r['estado']} | {r['teve_2t_gov']} | {r['abst_1t']:.2f}% | **{r['abst_2t_rf']:.2f}%** ({d_sign}) | {f1} | {l1} | **{f2}** ({r['pct_flavio_2t_rf']:.1f}%) | **{l2}** ({r['pct_lula_2t_rf']:.1f}%) |")

with open(r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\tabela_rf_markdown.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Markdown lines generated successfully.")
