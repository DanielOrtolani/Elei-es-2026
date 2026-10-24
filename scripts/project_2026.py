import json
import pandas as pd
import numpy as np

# 1. 2026 1st round abstention data by UF
abst_2026_1t = {
    "MS": 23.87,
    "RJ": 23.32,
    "MG": 22.79,
    "SP": 22.54,
    "MT": 22.20,
    "GO": 21.83,
    "RO": 21.71,
    "ES": 21.37,
    "RS": 21.35,
    "AL": 20.61,
    "PR": 20.57,
    "AC": 20.43,
    "AM": 20.16,
    "BA": 19.97,
    "MA": 19.74,
    "PA": 19.11,
    "SC": 18.95,
    "DF": 18.90,
    "RN": 18.38,
    "TO": 18.34,
    "PE": 18.16,
    "AP": 17.41,
    "PB": 17.38,
    "SE": 17.30,
    "PI": 17.16,
    "RR": 17.12,
    "CE": 15.52
}

uf_info = {
    "AC": ("Acre", "Norte"),
    "AL": ("Alagoas", "Nordeste"),
    "AP": ("Amapá", "Norte"),
    "AM": ("Amazonas", "Norte"),
    "BA": ("Bahia", "Nordeste"),
    "CE": ("Ceará", "Nordeste"),
    "DF": ("Distrito Federal", "Centro-Oeste"),
    "ES": ("Espírito Santo", "Sudeste"),
    "GO": ("Goiás", "Centro-Oeste"),
    "MA": ("Maranhão", "Nordeste"),
    "MT": ("Mato Grosso", "Centro-Oeste"),
    "MS": ("Mato Grosso do Sul", "Centro-Oeste"),
    "MG": ("Minas Gerais", "Sudeste"),
    "PA": ("Pará", "Norte"),
    "PB": ("Paraíba", "Nordeste"),
    "PR": ("Paraná", "Sul"),
    "PE": ("Pernambuco", "Nordeste"),
    "PI": ("Piauí", "Nordeste"),
    "RJ": ("Rio de Janeiro", "Sudeste"),
    "RN": ("Rio Grande do Norte", "Nordeste"),
    "RS": ("Rio Grande do Sul", "Sul"),
    "RO": ("Rondônia", "Norte"),
    "RR": ("Roraima", "Norte"),
    "SC": ("Santa Catarina", "Sul"),
    "SE": ("Sergipe", "Nordeste"),
    "SP": ("São Paulo", "Sudeste"),
    "TO": ("Tocantins", "Norte")
}

# 2026 Gubernatorial 2nd round: AC, AM, DF, ES, RN, TO
gov_2t_2026 = {"AC", "AM", "DF", "ES", "RN", "TO"}

# Load dataset and refit the best model
data_path = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\dataset_regressao.csv"
df = pd.read_csv(data_path)

import statsmodels.formula.api as smf
# We fit model with year as category and region as category
# For 2026, since 2026 national 1T abstention is 21.08% (very close to 2022's 20.95% and 2018's 20.33%),
# let's look at the parameters:
m_ols = smf.ols("delta_abst ~ teve_2t_gov + abst_1t + C(regiao)", data=df).fit()
print("Model fit without year dummy (for cross-year generalization):")
print(m_ols.summary().tables[1])

# Also let's fit the full model with year dummies and evaluate scenario:
# 2026 national climate: high polarization, transportation, national 1T abstention 21.08%
# Baseline OLS with Region + Gov Effect:
# Delta = Intercept + beta_gov * teve_2t + beta_abst * abst_1t + beta_regiao
# Let's compute projections for each state!

records = []
for uf, abst_1t in sorted(abst_2026_1t.items()):
    state_name, regiao = uf_info[uf]
    tem_gov = 1 if uf in gov_2t_2026 else 0
    
    # Predict using OLS
    row_actual = pd.DataFrame([{
        "teve_2t_gov": tem_gov,
        "abst_1t": abst_1t,
        "regiao": regiao
    }])
    delta_pred = m_ols.predict(row_actual)[0]
    abst_2t_pred = abst_1t + delta_pred
    
    # Counterfactual (se NÃO tivesse / se TIVESSE)
    row_counter = pd.DataFrame([{
        "teve_2t_gov": 1 - tem_gov,
        "abst_1t": abst_1t,
        "regiao": regiao
    }])
    delta_counter = m_ols.predict(row_counter)[0]
    abst_2t_counter = abst_1t + delta_counter
    
    impacto_gov = delta_pred - delta_counter # negative when gov presence reduces abstention
    
    records.append({
        "uf": uf,
        "estado": state_name,
        "regiao": regiao,
        "teve_2t_gov": "Sim" if tem_gov == 1 else "Não",
        "abst_1t": abst_1t,
        "delta_projetado": round(delta_pred, 2),
        "abst_2t_projetada": round(abst_2t_pred, 2),
        "abst_2t_cenario_oposto": round(abst_2t_counter, 2),
        "impacto_governador": round(impacto_gov, 2)
    })

res_df = pd.DataFrame(records).sort_values(by="abst_2t_projetada", ascending=False)
print("\n=== PROJEÇÃO DE ABSTENÇÃO DO 2º TURNO DE 2026 ===")
print(res_df.to_string(index=False))

res_df.to_csv(r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\projecao_abstencao_2026.csv", index=False)
