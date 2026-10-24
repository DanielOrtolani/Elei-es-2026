import json
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import shap

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import statsmodels.formula.api as smf

# 1. Load data
data_path = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\dataset_regressao.csv"
df = pd.read_csv(data_path)

# Verify missing values
print("--- Check Missing Values ---")
print(df.isnull().sum())

# 2. Prepare Features for State-Level Random Forest
# One-hot encode states (27 UFs) without dropping so each state gets its own node in trees
uf_dummies = pd.get_dummies(df["uf"], prefix="UF", dtype=float)
ano_dummies = pd.get_dummies(df["ano"].astype(str), prefix="Ano", drop_first=True, dtype=float)

X_full = pd.concat([
    uf_dummies,
    ano_dummies,
    df[["teve_2t_gov", "abst_1t"]]
], axis=1)

y_full = df["delta_abst"]

# 3. Train/Test Split (75/25 stratified by year)
X_train, X_test, y_train, y_test = train_test_split(
    X_full, y_full, test_size=0.25, random_state=42, stratify=df["ano"]
)

# 4. Fit Random Forest
rf = RandomForestRegressor(
    n_estimators=300,
    max_depth=5,
    min_samples_split=3,
    min_samples_leaf=2,
    random_state=42
)
rf.fit(X_train, y_train)

# Model Evaluation
y_pred_train = rf.predict(X_train)
y_pred_test = rf.predict(X_test)

train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
test_mae = mean_absolute_error(y_test, y_pred_test)
test_r2 = r2_score(y_test, y_pred_test)

cv_scores = cross_val_score(rf, X_train, y_train, cv=5, scoring="neg_mean_squared_error")
cv_rmse = np.sqrt(-cv_scores.mean())

print("\n=== RANDOM FOREST MODEL PERFORMANCE ===")
print(f"Train RMSE: {train_rmse:.4f}")
print(f"Test RMSE:  {test_rmse:.4f}")
print(f"Test MAE:   {test_mae:.4f}")
print(f"Test R2:    {test_r2:.4f}")
print(f"5-Fold CV RMSE: {cv_rmse:.4f}")

# 5. Full Dataset Refit for Complete 27-State Decomposition
rf_full = RandomForestRegressor(
    n_estimators=300,
    max_depth=5,
    min_samples_split=3,
    min_samples_leaf=2,
    random_state=42
)
rf_full.fit(X_full, y_full)

# TreeSHAP Explainer
explainer = shap.TreeExplainer(rf_full)
shap_values = explainer.shap_values(X_full)

# Extract State-Specific SHAP Impact
# For each state, when UF_{state} == 1, what is the mean SHAP contribution to delta_abst?
state_cols = [c for c in X_full.columns if c.startswith("UF_")]
state_coefs = []

for c in state_cols:
    uf_code = c.replace("UF_", "")
    mask = (X_full[c] == 1.0)
    # SHAP value for this feature when the state is active
    col_idx = list(X_full.columns).index(c)
    mean_shap_active = shap_values[mask, col_idx].mean()
    
    # Also extract feature importance (MDI)
    importance_mdi = rf_full.feature_importances_[col_idx]
    
    # Observed historical delta for this state
    mean_obs_delta = df[df["uf"] == uf_code]["delta_abst"].mean()
    
    state_coefs.append({
        "uf": uf_code,
        "rf_shap_coef": round(mean_shap_active, 3),
        "rf_importance_pct": round(importance_mdi * 100, 2),
        "historico_delta_medio": round(mean_obs_delta, 2)
    })

state_df = pd.DataFrame(state_coefs).sort_values(by="rf_shap_coef", ascending=False)

# Compare with OLS State Fixed Effects
m_fe = smf.ols("delta_abst ~ C(uf) + teve_2t_gov + C(ano)", data=df).fit()
fe_coefs = {}
ref_state = "AC"
base_intercept = m_fe.params["Intercept"]
fe_coefs[ref_state] = 0.0 # reference
for uf_code in [c.replace("UF_", "") for c in state_cols]:
    param_name = f"C(uf)[T.{uf_code}]"
    if param_name in m_fe.params:
        fe_coefs[uf_code] = round(m_fe.params[param_name], 3)
    else:
        fe_coefs[uf_code] = 0.0

state_df["ols_fe_coef"] = state_df["uf"].map(fe_coefs)

# Map State Names and Regions
uf_info = {
    "AC": ("Acre", "Norte"), "AL": ("Alagoas", "Nordeste"), "AP": ("Amapá", "Norte"),
    "AM": ("Amazonas", "Norte"), "BA": ("Bahia", "Nordeste"), "CE": ("Ceará", "Nordeste"),
    "DF": ("Distrito Federal", "Centro-Oeste"), "ES": ("Espírito Santo", "Sudeste"),
    "GO": ("Goiás", "Centro-Oeste"), "MA": ("Maranhão", "Nordeste"),
    "MT": ("Mato Grosso", "Centro-Oeste"), "MS": ("Mato Grosso do Sul", "Centro-Oeste"),
    "MG": ("Minas Gerais", "Sudeste"), "PA": ("Pará", "Norte"), "PB": ("Paraíba", "Nordeste"),
    "PR": ("Paraná", "Sul"), "PE": ("Pernambuco", "Nordeste"), "PI": ("Piauí", "Nordeste"),
    "RJ": ("Rio de Janeiro", "Sudeste"), "RN": ("Rio Grande do Norte", "Nordeste"),
    "RS": ("Rio Grande do Sul", "Sul"), "RO": ("Rondônia", "Norte"), "RR": ("Roraima", "Norte"),
    "SC": ("Santa Catarina", "Sul"), "SE": ("Sergipe", "Nordeste"), "SP": ("São Paulo", "Sudeste"),
    "TO": ("Tocantins", "Norte")
}

state_df["estado"] = state_df["uf"].map(lambda u: uf_info[u][0])
state_df["regiao"] = state_df["uf"].map(lambda u: uf_info[u][1])

# Reorder columns
state_df = state_df[["uf", "estado", "regiao", "rf_shap_coef", "rf_importance_pct", "historico_delta_medio", "ols_fe_coef"]]
print("\n=== COEFICIENTES ESTADUAIS DE ABSTENÇÃO (RANDOM FOREST SHAP) ===")
print(state_df.to_string(index=False))

# Save results
out_csv = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\rf_state_coefficients.csv"
state_df.to_csv(out_csv, index=False)

# 6. Visualization
img_dir = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e"
plt.figure(figsize=(10, 8))
colors = ['#E74C3C' if v > 0 else '#2ECC71' for v in state_df["rf_shap_coef"]]
y_pos = np.arange(len(state_df))

plt.barh(y_pos, state_df["rf_shap_coef"], color=colors, edgecolor='black', alpha=0.85)
plt.yticks(y_pos, [f"{r['uf']} - {r['estado']}" for _, r in state_df.iterrows()], fontsize=9)
plt.axvline(0, color='black', linestyle='--', linewidth=1)
plt.xlabel("Coeficiente Marginal Random Forest (SHAP Value em p.p.)", fontsize=11, weight='bold')
plt.title("Ranking Estadual de Impacto Estrutural na Abstenção do 2º Turno (Random Forest)", fontsize=12, weight='bold')
plt.gca().invert_yaxis()
plt.tight_layout()

chart_path = os.path.join(img_dir, "rf_state_abstention_coefficients.png")
plt.savefig(chart_path, dpi=200)
plt.close()

print(f"\nChart saved to {chart_path}")
