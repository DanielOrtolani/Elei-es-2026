import pandas as pd

df = pd.read_csv(r"C:\Users\ortol\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\projecao_votos_candidatos_2026.csv") if False else pd.read_csv(r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\projecao_votos_candidatos_2026.csv")

lines = []
for _, r in df.iterrows():
    f1 = f"{int(r['votos_flavio_1t']):,}".replace(",", ".")
    l1 = f"{int(r['votos_lula_1t']):,}".replace(",", ".")
    f2 = f"{int(r['votos_flavio_2t']):,}".replace(",", ".")
    l2 = f"{int(r['votos_lula_2t']):,}".replace(",", ".")
    lines.append(f"| **{r['uf']}** | {r['estado']} | {r['teve_2t_gov']} | {r['abst_1t']:.2f}% | {r['abst_2t_projetada']:.2f}% | {f1} | {l1} | **{f2}** ({r['pct_flavio_2t']:.1f}%) | **{l2}** ({r['pct_lula_2t']:.1f}%) |")

out_txt = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\tabela_markdown.txt"
with open(out_txt, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Exported {len(lines)} lines to {out_txt}")
