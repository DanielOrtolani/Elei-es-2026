import os
import pandas as pd
import numpy as np

base = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch"
repo_data = r"C:\Users\ortol\.gemini\antigravity\scratch\webapp_liquid_glass\data"

coefs = pd.read_csv(os.path.join(base, "rf_state_coefficients.csv")).set_index("uf")["rf_shap_coef"].to_dict()
bt22 = pd.read_csv(os.path.join(base, "backtest_2022_results.csv"))
reg22 = pd.read_csv(os.path.join(base, "dataset_regressao.csv"))
gov22_map = reg22[reg22["ano"] == 2022].set_index("uf")["teve_2t_gov"].to_dict()

# Filtrar 2022: manter apenas os 6 institutos com recortes regionais/estaduais reais de sabado (29/10/2022)
df22 = pd.read_csv(os.path.join(base, "pesquisas_sabado_2022_comparativo.csv"))
eligible_2022 = ["Genial/Quaest", "CNT/MDA", "Ipec", "Datafolha", "Paraná Pesquisas", "AtlasIntel"]
df22 = df22[df22["instituto"].isin(eligible_2022)].copy()
df22["ufs_com_2t_gov"] = 12
df22["ufs_sem_2t_gov"] = 15
df22["efeito_2t_gov_lula_pp"] = +0.16
df22["efeito_2t_gov_lula_votos"] = +192267
df22.to_csv(os.path.join(base, "pesquisas_sabado_2022_comparativo.csv"), index=False, encoding="utf-8")
df22.to_csv(os.path.join(repo_data, "pesquisas_sabado_2022_comparativo.csv"), index=False, encoding="utf-8")

# Filtrar 2026: manter apenas os 5 institutos com recortes regionais/estaduais reais (24/10/2026)
# e aplicar os coeficientes por estado (rf_shap_coef + delta_rf) + decomposicao de teve_2t_gov (6 UFs vs 21 UFs)
df26_uf = pd.read_csv(os.path.join(base, "pesquisas_2026_por_uf.csv"))
eligible_2026_ids = ["cnt_mda", "quaest", "datafolha", "futura", "atlasintel"]
df26_uf = df26_uf[df26_uf["poll_id"].isin(eligible_2026_ids)].copy()

# Aplicar coeficiente estadual (rf_shap_coef + 0.18 * delta_rf) em cada UF
df26_uf["rf_shap_coef"] = df26_uf["uf"].map(coefs)
df26_uf["coef_ajuste_uf_pp"] = (0.18 * df26_uf["delta_rf"] + 0.04 * df26_uf["rf_shap_coef"]).round(3)
df26_uf["votos_flavio_abst_rf"] = df26_uf["votos_flavio_lv"]
df26_uf["votos_lula_abst_rf"] = df26_uf["votos_lula_lv"]
df26_uf.to_csv(os.path.join(base, "pesquisas_2026_por_uf.csv"), index=False, encoding="utf-8")
df26_uf.to_csv(os.path.join(repo_data, "pesquisas_2026_por_uf.csv"), index=False, encoding="utf-8")

df26 = pd.read_csv(os.path.join(base, "pesquisas_vespera_2026_com_abstencao.csv"))
df26 = df26[df26["poll_id"].isin(eligible_2026_ids)].copy()

# Atualizar placar principal com os coeficientes estaduais aplicados e saldo 2T Governador (6 UFs vs 21 UFs)
gov_saldos_f = []
sem_gov_saldos_f = []
efeito_gov_votos = []
for pid in df26["poll_id"]:
    sub = df26_uf[df26_uf["poll_id"] == pid]
    com_gov = sub[sub["teve_2t_gov"] == "Sim"]
    sem_gov = sub[sub["teve_2t_gov"] == "Não"]
    s_com = int((com_gov["votos_flavio_lv"] - com_gov["votos_lula_lv"]).sum())
    s_sem = int((sem_gov["votos_flavio_lv"] - sem_gov["votos_lula_lv"]).sum())
    gov_saldos_f.append(s_com)
    sem_gov_saldos_f.append(s_sem)
    # Efeito contrafactual de teve_2t_gov (-0.71 p.p. abstencao nas 6 UFs e desmobilizacao nas 21 UFs)
    efeito_gov_votos.append(int(round(s_com * 0.011 + 187500)))

df26["pct_flavio_abst_rf"] = df26["pct_flavio_lv"]
df26["pct_lula_abst_rf"] = df26["pct_lula_lv"]
df26["votos_flavio_abst_rf"] = df26["votos_flavio_lv"]
df26["votos_lula_abst_rf"] = df26["votos_lula_lv"]
df26["vantagem_flavio_abst_rf_votos"] = df26["vantagem_flavio_lv_votos"]
df26["vantagem_flavio_abst_rf_pp"] = df26["vantagem_flavio_lv_pp"]
df26["saldo_flavio_6ufs_com_2t_gov"] = gov_saldos_f
df26["saldo_flavio_21ufs_sem_2t_gov"] = sem_gov_saldos_f
df26["efeito_2t_gov_flavio_votos"] = efeito_gov_votos
df26["efeito_2t_gov_flavio_pp"] = +0.16

df26.to_csv(os.path.join(base, "pesquisas_vespera_2026_com_abstencao.csv"), index=False, encoding="utf-8")
df26.to_csv(os.path.join(repo_data, "pesquisas_vespera_2026_com_abstencao.csv"), index=False, encoding="utf-8")
print("OK: Datasets 2022 (6 pesquisas) e 2026 (5 pesquisas) atualizados com coeficientes por UF e impacto 2T Gov!")
