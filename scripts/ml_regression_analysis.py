import json
import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.linear_model import Ridge, Lasso, LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# 1. Load data
data_path = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\abstencao_completa.json"
with open(data_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Mapping UFs and Regions
uf_map = {
    "Acre": ("AC", "Norte"),
    "Alagoas": ("AL", "Nordeste"),
    "Amapá": ("AP", "Norte"),
    "Amazonas": ("AM", "Norte"),
    "Bahia": ("BA", "Nordeste"),
    "Ceará": ("CE", "Nordeste"),
    "Distrito Federal": ("DF", "Centro-Oeste"),
    "Espírito Santo": ("ES", "Sudeste"),
    "Goiás": ("GO", "Centro-Oeste"),
    "Maranhão": ("MA", "Nordeste"),
    "Mato Grosso": ("MT", "Centro-Oeste"),
    "Mato Grosso do Sul": ("MS", "Centro-Oeste"),
    "Minas Gerais": ("MG", "Sudeste"),
    "Pará": ("PA", "Norte"),
    "Paraíba": ("PB", "Nordeste"),
    "Paraná": ("PR", "Sul"),
    "Pernambuco": ("PE", "Nordeste"),
    "Piauí": ("PI", "Nordeste"),
    "Rio de Janeiro": ("RJ", "Sudeste"),
    "Rio Grande do Norte": ("RN", "Nordeste"),
    "Rio Grande do Sul": ("RS", "Sul"),
    "Rondônia": ("RO", "Norte"),
    "Roraima": ("RR", "Norte"),
    "Santa Catarina": ("SC", "Sul"),
    "Sergipe": ("SE", "Nordeste"),
    "São Paulo": ("SP", "Sudeste"),
    "Tocantins": ("TO", "Norte")
}

# Second round governor states
# 2022 (12 UFs): AL, AM, BA, ES, MS, PB, PE, RS, RO, SC, SP, SE
gov_2t_2022 = {"AL", "AM", "BA", "ES", "MS", "PB", "PE", "RS", "RO", "SC", "SP", "SE"}

# 2018 (14 UFs): AP, AM, DF, MS, MG, PA, RJ, RN, RS, RO, RR, SC, SP, SE
gov_2t_2018 = {"AP", "AM", "DF", "MS", "MG", "PA", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE"}

# 2014 (14 UFs): AC, AP, AM, CE, DF, GO, MS, PA, PB, RJ, RN, RS, RO, RR
gov_2t_2014 = {"AC", "AP", "AM", "CE", "DF", "GO", "MS", "PA", "PB", "RJ", "RN", "RS", "RO", "RR"}

def parse_pct(s):
    if not s or s == '-': return np.nan
    return float(s.replace('%', '').replace(',', '.').strip())

records = []
for state, d in raw_data.items():
    uf, regiao = uf_map[state]
    
    # 2022
    a1_22 = parse_pct(d.get("2022_t1"))
    a2_22 = parse_pct(d.get("2022_t2"))
    records.append({
        "estado": state, "uf": uf, "regiao": regiao, "ano": 2022,
        "abst_1t": a1_22, "abst_2t": a2_22,
        "delta_abst": a2_22 - a1_22,
        "teve_2t_gov": 1 if uf in gov_2t_2022 else 0
    })
    
    # 2018
    a1_18 = parse_pct(d.get("2018_t1"))
    a2_18 = parse_pct(d.get("2018_t2"))
    records.append({
        "estado": state, "uf": uf, "regiao": regiao, "ano": 2018,
        "abst_1t": a1_18, "abst_2t": a2_18,
        "delta_abst": a2_22 - a1_22 if a2_18 is None else a2_18 - a1_18,
        "teve_2t_gov": 1 if uf in gov_2t_2018 else 0
    })
    
    # 2014
    a1_14 = parse_pct(d.get("2014_t1"))
    a2_14 = parse_pct(d.get("2014_t2"))
    records.append({
        "estado": state, "uf": uf, "regiao": regiao, "ano": 2014,
        "abst_1t": a1_14, "abst_2t": a2_14,
        "delta_abst": a2_14 - a1_14,
        "teve_2t_gov": 1 if uf in gov_2t_2014 else 0
    })

df = pd.DataFrame(records)
csv_out = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\dataset_regressao.csv"
df.to_csv(csv_out, index=False)
print(f"Dataset created with {len(df)} rows. Missing values check:")
print(df.isnull().sum())

# Descriptive stats
print("\n--- Descriptive Statistics: Delta Abstencao (p.p.) by Teve 2T Gov ---")
desc = df.groupby(["teve_2t_gov"])["delta_abst"].agg(["count", "mean", "std", "median", lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)])
desc.columns = ["count", "mean", "std", "median", "q25", "q75"]
print(desc)

print("\n--- Breakdown by Year and Teve 2T Gov ---")
year_desc = df.groupby(["ano", "teve_2t_gov"])["delta_abst"].agg(["count", "mean", "std"]).reset_index()
print(year_desc)

# Statistical test (Welch's t-test and Mann-Whitney U)
group_sim = df[df["teve_2t_gov"] == 1]["delta_abst"]
group_nao = df[df["teve_2t_gov"] == 0]["delta_abst"]
ttest_res = stats.ttest_ind(group_sim, group_nao, equal_var=False)
mw_res = stats.mannwhitneyu(group_sim, group_nao, alternative="two-sided")
print(f"\nWelch's t-test: t = {ttest_res.statistic:.4f}, p = {ttest_res.pvalue:.4f}")
print(f"Mann-Whitney U: U = {mw_res.statistic:.4f}, p = {mw_res.pvalue:.4f}")

# Model 1: Simple Bivariate OLS
m1 = smf.ols("delta_abst ~ teve_2t_gov", data=df).fit()
print("\n=== MODEL 1: Simple OLS ===")
print(m1.summary().tables[1])
print(f"R-squared: {m1.rsquared:.4f}, F p-value: {m1.f_pvalue:.4f}")

# Model 2: Multivariate OLS with Year Fixed Effects and Baseline 1T Abstention
df["ano_str"] = df["ano"].astype(str)
m2 = smf.ols("delta_abst ~ teve_2t_gov + abst_1t + C(ano_str) + C(regiao)", data=df).fit()
print("\n=== MODEL 2: Controlled OLS (with Year and Region Fixed Effects) ===")
print(m2.summary().tables[1])
print(f"R-squared: {m2.rsquared:.4f}, Adj R-squared: {m2.rsquared_adj:.4f}")

# Model 3 & 4: Machine Learning Pipelines (Train/Test Split + Standardization)
X = df[["teve_2t_gov", "abst_1t", "ano_str", "regiao"]]
y = df["delta_abst"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=df["ano_str"])

num_features = ["abst_1t"]
cat_features = ["ano_str", "regiao"]
bin_features = ["teve_2t_gov"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), num_features),
        ("cat", OneHotEncoder(drop="first"), cat_features),
        ("bin", "passthrough", bin_features)
    ]
)

models = {
    "LinearRegression": Pipeline([("prep", preprocessor), ("reg", LinearRegression())]),
    "Ridge (alpha=1.0)": Pipeline([("prep", preprocessor), ("reg", Ridge(alpha=1.0))]),
    "Lasso (alpha=0.1)": Pipeline([("prep", preprocessor), ("reg", Lasso(alpha=0.1))]),
    "RandomForest": Pipeline([("prep", preprocessor), ("reg", RandomForestRegressor(n_estimators=100, random_state=42, max_depth=3))])
}

results = []
for name, pipe in models.items():
    pipe.fit(X_train, y_train)
    y_pred_train = pipe.predict(X_train)
    y_pred_test = pipe.predict(X_test)
    
    rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
    rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
    mae_test = mean_absolute_error(y_test, y_pred_test)
    r2_test = r2_score(y_test, y_pred_test)
    
    cv_scores = cross_val_score(pipe, X_train, y_train, cv=5, scoring="neg_mean_squared_error")
    rmse_cv = np.sqrt(-cv_scores.mean())
    
    results.append({
        "Model": name,
        "Train RMSE": rmse_train,
        "Test RMSE": rmse_test,
        "Test MAE": mae_test,
        "Test R2": r2_test,
        "CV RMSE (5-fold)": rmse_cv
    })

res_df = pd.DataFrame(results)
print("\n=== MACHINE LEARNING MODEL EVALUATION ===")
print(res_df.to_string(index=False))

# Feature coefficients from Ridge
ridge_pipe = models["Ridge (alpha=1.0)"]
feature_names = (
    num_features +
    list(ridge_pipe.named_steps["prep"].named_transformers_["cat"].get_feature_names_out(cat_features)) +
    bin_features
)
ridge_coefs = ridge_pipe.named_steps["reg"].coef_
coef_df = pd.DataFrame({"Feature": feature_names, "Coefficient": ridge_coefs}).sort_values(by="Coefficient", ascending=False)
print("\n=== RIDGE REGRESSION COEFFICIENTS ===")
print(coef_df.to_string(index=False))

# Visualizations
img_dir = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e"
os.makedirs(img_dir, exist_ok=True)

# Plot 1: Boxplot comparison
plt.figure(figsize=(10, 6))
sns.set_theme(style="whitegrid")
palette = {0: "#4A90E2", 1: "#E74C3C"}
ax = sns.boxplot(x="ano", y="delta_abst", hue="teve_2t_gov", data=df, palette=palette, showmeans=True,
                 meanprops={"marker":"o", "markerfacecolor":"white", "markeredgecolor":"black"})
plt.title("Variação da Abstenção no 2º Turno (Δ p.p.) por Presença de Eleição para Governador", fontsize=13, weight="bold")
plt.xlabel("Ano da Eleição", fontsize=11)
plt.ylabel("Δ Abstenção (2ºT - 1ºT em p.p.)", fontsize=11)
plt.axhline(0, color="gray", linestyle="--", alpha=0.7)
handles, _ = ax.get_legend_handles_labels()
plt.legend(handles, ["Sem 2ºT Gov (Apenas Presidente)", "Com 2ºT Gov (Presid. + Gov.)"], title="Segundo Turno Estadual")
plt.tight_layout()
p1_path = os.path.join(img_dir, "boxplot_delta_abstencao.png")
plt.savefig(p1_path, dpi=200)
plt.close()

# Plot 2: Scatter / Regression actual vs predicted
best_model = models["Ridge (alpha=1.0)"]
y_pred_all = best_model.predict(X)
plt.figure(figsize=(8, 6))
plt.scatter(y, y_pred_all, c=df["teve_2t_gov"], cmap="coolwarm", edgecolors="black", s=60, alpha=0.8)
plt.plot([y.min(), y.max()], [y.min(), y.max()], "r--", lw=2, label="Linha de Identidade 1:1")
plt.xlabel("Δ Abstenção Real (p.p.)", fontsize=11)
plt.ylabel("Δ Abstenção Previsto (p.p.)", fontsize=11)
plt.title("Valores Reais vs. Previstos (Modelo Ridge Regularizado)", fontsize=13, weight="bold")
plt.colorbar(label="Teve 2º Turno Gov (0=Não, 1=Sim)")
plt.legend()
plt.tight_layout()
p2_path = os.path.join(img_dir, "actual_vs_predicted.png")
plt.savefig(p2_path, dpi=200)
plt.close()

print(f"\nPlots saved to {p1_path} and {p2_path}")
