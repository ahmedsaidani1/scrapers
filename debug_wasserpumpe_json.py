"""
Debug JSON-LD extraction for wasserpumpe
"""
import json
from bs4 import BeautifulSoup

with open("wasserpumpe_debug_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
scripts = soup.find_all("script", {"type": "application/ld+json"})

for i, script in enumerate(scripts, 1):
    raw = script.string or script.get_text(strip=True)
    if not raw:
        continue
    
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and data.get("@type") == "Product":
            print(f"Product JSON-LD #{i}:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("\n" + "="*60 + "\n")
    except Exception as e:
        print(f"Failed to parse JSON-LD #{i}: {e}")
