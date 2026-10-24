import urllib.request
import urllib.parse
import json

q = '"56104503" OR "56 104 503" OR "302.807"'
url = f"https://pt.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&format=json"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
for item in data.get('query', {}).get('search', []):
    print(item.get('title'))
    snippet = item.get('snippet', '')
    print('  Snippet:', snippet[:150])
