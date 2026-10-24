import urllib.request
import json

polls_res = json.loads(urllib.request.urlopen("http://localhost:3000/api/polls-sabado-2022").read().decode("utf-8"))
bt_res = json.loads(urllib.request.urlopen("http://localhost:3000/api/backtest-2022").read().decode("utf-8"))
proj_res = json.loads(urllib.request.urlopen("http://localhost:3000/api/projections-2026").read().decode("utf-8"))
rf_res = json.loads(urllib.request.urlopen("http://localhost:3000/api/rf-coefficients").read().decode("utf-8"))

with open(r"C:\Users\ortol\.gemini\antigravity\scratch\webapp_liquid_glass\public\css\liquid-glass.css", encoding="utf-8") as f:
    css = f.read()
with open(r"C:\Users\ortol\.gemini\antigravity\scratch\webapp_liquid_glass\public\index.html", encoding="utf-8") as f:
    html = f.read()
with open(r"C:\Users\ortol\.gemini\antigravity\scratch\webapp_liquid_glass\public\js\app.js", encoding="utf-8") as f:
    js = f.read()

target_fetch = """    // Fetch all endpoints in parallel
    const [pollsRes, backtestRes, projRes, rfRes] = await Promise.all([
      fetch('/api/polls-sabado-2022').then(r => r.json()),
      fetch('/api/backtest-2022').then(r => r.json()),
      fetch('/api/projections-2026').then(r => r.json()),
      fetch('/api/rf-coefficients').then(r => r.json())
    ]);"""

inline_fetch = f"""    const pollsRes = {json.dumps(polls_res, ensure_ascii=False)};
    const backtestRes = {json.dumps(bt_res, ensure_ascii=False)};
    const projRes = {json.dumps(proj_res, ensure_ascii=False)};
    const rfRes = {json.dumps(rf_res, ensure_ascii=False)};"""

js_inline = js.replace(target_fetch, inline_fetch)

out = html.replace(
    '<link rel="stylesheet" href="/css/liquid-glass.css" />',
    f'<style>\n{css}\n</style>'
).replace(
    '<script src="/js/app.js"></script>',
    f'<script>\n{js_inline}\n</script>'
)

out_path = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\painel_eleicoes_apple_ui.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(out)

print(f"Updated painel_eleicoes_apple_ui.html successfully ({len(out)} bytes)")
