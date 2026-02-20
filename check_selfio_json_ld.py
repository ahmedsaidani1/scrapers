"""Check JSON-LD structure in selfio page"""
import json
from bs4 import BeautifulSoup

with open('selfio_debug_page.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script', {'type': 'application/ld+json'})

print(f"Found {len(scripts)} JSON-LD scripts\n")

for i, script in enumerate(scripts, 1):
    print(f"{'='*60}")
    print(f"Script {i}")
    print(f"{'='*60}")
    
    if not script.string:
        print("Empty script")
        continue
    
    try:
        data = json.loads(script.string)
        print(json.dumps(data, indent=2)[:1000])
        print("\n...")
    except Exception as e:
        print(f"Error parsing: {e}")
        print(script.string[:500])
