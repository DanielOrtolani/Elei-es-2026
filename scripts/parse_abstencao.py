import urllib.request
import urllib.parse
import json
import re
from html.parser import HTMLParser

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
            # clean whitespace and non-breaking spaces
            cell_text = re.sub(r'\s+', ' ', cell_text.replace('\xa0', ' '))
            self.current_row.append(cell_text)

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell.append(data)

def get_section_html(title, section_index):
    url = f"https://pt.wikipedia.org/w/api.php?action=parse&page={urllib.parse.quote(title)}&section={section_index}&prop=text&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'AntigravityDataBot/1.0'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    return data.get('parse', {}).get('text', {}).get('*', '')

def parse_section(title, section_index):
    html = get_section_html(title, section_index)
    parser = TableParser()
    parser.feed(html)
    return parser.tables

print("Parsing 2022...")
tables_2022_t1 = parse_section('Resultados_da_eleição_presidencial_no_Brasil_em_2022', 6)
tables_2022_t2 = parse_section('Resultados_da_eleição_presidencial_no_Brasil_em_2022', 7)

print("Parsing 2018...")
tables_2018_t1 = parse_section('Resultados_da_eleição_presidencial_no_Brasil_em_2018', 9)
tables_2018_t2 = parse_section('Resultados_da_eleição_presidencial_no_Brasil_em_2018', 10)

print("Parsing 2014...")
tables_2014_t1 = parse_section('Resultados_da_eleição_presidencial_no_Brasil_em_2014', 3)
tables_2014_t2 = parse_section('Resultados_da_eleição_presidencial_no_Brasil_em_2014', 4)

def dump_headers_and_first_row(name, tables):
    print(f"=== {name} ===")
    for idx, t in enumerate(tables):
        print(f"Table {idx} ({len(t)} rows):")
        for r in t[:3]:
            print("  ", r)

dump_headers_and_first_row("2022 T1", tables_2022_t1)
dump_headers_and_first_row("2022 T2", tables_2022_t2)
dump_headers_and_first_row("2018 T1", tables_2018_t1)
dump_headers_and_first_row("2018 T2", tables_2018_t2)
dump_headers_and_first_row("2014 T1", tables_2014_t1)
dump_headers_and_first_row("2014 T2", tables_2014_t2)
