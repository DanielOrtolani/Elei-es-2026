import urllib.request
import urllib.parse
import json
import re
import os
import time
from html.parser import HTMLParser

CACHE_DIR = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\cache"
os.makedirs(CACHE_DIR, exist_ok=True)

class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.current_table = []
        self.current_row = []
        self.current_cell = []
        self.in_table = False
        self.in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
            self.current_table = []
        elif self.in_table and tag in ('tr',):
            self.current_row = []
        elif self.in_table and tag in ('td', 'th'):
            self.in_cell = True
            self.current_cell = []

    def handle_endtag(self, tag):
        if tag == 'table' and self.in_table:
            self.in_table = False
            self.tables.append(self.current_table)
        elif self.in_table and tag in ('tr',):
            if self.current_row:
                self.current_table.append(self.current_row)
        elif self.in_table and tag in ('td', 'th'):
            self.in_cell = False
            cell_text = "".join(self.current_cell).strip()
            cell_text = re.sub(r'\s+', ' ', cell_text.replace('\xa0', ' '))
            self.current_row.append(cell_text)

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell.append(data)

def get_section_html(title, section_index):
    cache_file = os.path.join(CACHE_DIR, f"{title}_{section_index}.html")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()

    time.sleep(1)
    url = f"https://pt.wikipedia.org/w/api.php?action=parse&page={urllib.parse.quote(title)}&section={section_index}&prop=text&format=json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AntigravityResearch/1.0'
    }
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                html = data.get('parse', {}).get('text', {}).get('*', '')
                with open(cache_file, "w", encoding="utf-8") as f:
                    f.write(html)
                return html
        except Exception as e:
            print(f"Retry {attempt+1} for {title} s={section_index} due to {e}")
            time.sleep(3 * (attempt + 1))
    return ""

def parse_section(title, section_index):
    html = get_section_html(title, section_index)
    parser = TableParser()
    parser.feed(html)
    return parser.tables

def clean_state_name(name):
    # remove footnotes like [1], [nota 1], etc.
    name = re.sub(r'\[.*?\]', '', name).strip()
    return name

def main():
    print("Collecting 2022...")
    t22_1 = parse_section('Resultados_da_eleição_presidencial_no_Brasil_em_2022', 6)[0]
    t22_2 = parse_section('Resultados_da_eleição_presidencial_no_Brasil_em_2022', 7)[0]

    print("Collecting 2018...")
    t18_1 = parse_section('Resultados_da_eleição_presidencial_no_Brasil_em_2018', 9)[1]
    t18_2 = parse_section('Resultados_da_eleição_presidencial_no_Brasil_em_2018', 10)[1]

    print("Collecting 2014...")
    t14_1 = parse_section('Resultados_da_eleição_presidencial_no_Brasil_em_2014', 3)[1]
    t14_2 = parse_section('Resultados_da_eleição_presidencial_no_Brasil_em_2014', 4)[1]

    def extract_dict(table):
        d = {}
        for row in table[1:]:
            if not row or len(row) < 4: continue
            raw_name = clean_state_name(row[0])
            if any(k in raw_name for k in ['Total', 'Exterior', 'Total geral']):
                continue
            abs_val = row[2].replace(' ', '').strip()
            pct_val = row[3].strip()
            d[raw_name] = {'abs': abs_val, 'pct': pct_val}
        return d

    d22_1 = extract_dict(t22_1)
    d22_2 = extract_dict(t22_2)
    d18_1 = extract_dict(t18_1)
    d18_2 = extract_dict(t18_2)
    d14_1 = extract_dict(t14_1)
    d14_2 = extract_dict(t14_2)

    # Let's see all unique state names
    all_states = sorted(list(set(list(d22_1.keys()) + list(d18_1.keys()) + list(d14_1.keys()))))
    
    result = {}
    for st in all_states:
        result[st] = {
            '2022_t1': d22_1.get(st, {}).get('pct', '-'),
            '2022_t2': d22_2.get(st, {}).get('pct', '-'),
            '2018_t1': d18_1.get(st, {}).get('pct', '-'),
            '2018_t2': d18_2.get(st, {}).get('pct', '-'),
            '2014_t1': d14_1.get(st, {}).get('pct', '-'),
            '2014_t2': d14_2.get(st, {}).get('pct', '-'),
        }

    out_file = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\abstencao_completa.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Successfully processed {len(result)} states. Saved to {out_file}.")
    for st, v in sorted(result.items()):
        print(f"{st:25} | 2022: {v['2022_t1']:>6} / {v['2022_t2']:>6} | 2018: {v['2018_t1']:>6} / {v['2018_t2']:>6} | 2014: {v['2014_t1']:>6} / {v['2014_t2']:>6}")

if __name__ == "__main__":
    main()
