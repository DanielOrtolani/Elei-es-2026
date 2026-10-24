import os
import re
from html.parser import HTMLParser

CACHE_DIR = r"C:\Users\ortol\.gemini\antigravity\brain\217781a3-1ac8-4982-a57b-100af633710e\scratch\cache"

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

def parse_file(fname):
    with open(os.path.join(CACHE_DIR, fname), "r", encoding="utf-8") as f:
        html = f.read()
    p = TableParser()
    p.feed(html)
    return p.tables

t1 = parse_file("Resultados_da_eleição_presidencial_no_Brasil_em_2022_6.html")[0]
t2 = parse_file("Resultados_da_eleição_presidencial_no_Brasil_em_2022_7.html")[0]

print("=== 2022 1T HEADERS & FIRST 3 ROWS ===")
for r in t1[:5]:
    print(r)

print("\n=== 2022 2T HEADERS & FIRST 3 ROWS ===")
for r in t2[:5]:
    print(r)
