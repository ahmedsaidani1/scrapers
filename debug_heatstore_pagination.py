"""
Find the correct pagination selector for heat-store.de
"""
import requests
from bs4 import BeautifulSoup

url = "https://www.heat-store.de/heizung/heizkoerper/badheizkoerper//"
response = requests.get(url, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

print("=== SEARCHING FOR PAGINATION ELEMENTS ===\n")

# Look for common pagination patterns
selectors = [
    ('nav.pagination', 'nav with pagination class'),
    ('div.pagination', 'div with pagination class'),
    ('ul.pagination', 'ul with pagination class'),
    ('a[rel="next"]', 'link with rel=next'),
    ('a.page-next', 'link with page-next class'),
    ('a.next', 'link with next class'),
    ('a[aria-label*="next"]', 'link with next in aria-label'),
    ('button[aria-label*="next"]', 'button with next in aria-label'),
]

for selector, description in selectors:
    elements = soup.select(selector)
    print(f"{description} ({selector}): {len(elements)} found")
    if elements:
        for elem in elements[:2]:
            print(f"  {elem}")

# Search for any element with "page" or "pagination" in class
print("\n=== ELEMENTS WITH 'page' OR 'pagination' IN CLASS ===")
all_elements = soup.find_all(class_=lambda x: x and ('page' in str(x).lower() or 'pagination' in str(x).lower()))
print(f"Found {len(all_elements)} elements")
for elem in all_elements[:5]:
    print(f"  {elem.name}.{elem.get('class')}: {elem.get_text(strip=True)[:50]}")

# Look at the bottom of the page for pagination
print("\n=== CHECKING FOOTER AREA ===")
footer_area = soup.find_all('div', class_=lambda x: x and 'footer' in str(x).lower())
print(f"Found {len(footer_area)} footer divs")

# Save HTML to inspect
with open('heatstore_pagination_debug.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("\n✓ Saved HTML to heatstore_pagination_debug.html")

# Search for page numbers (1, 2, 3, etc.)
print("\n=== LOOKING FOR PAGE NUMBER LINKS ===")
all_links = soup.find_all('a', href=True)
page_links = [link for link in all_links if '?p=' in link.get('href', '')]
print(f"Found {len(page_links)} links with ?p= in href")
for link in page_links[:5]:
    print(f"  {link.get_text(strip=True)}: {link.get('href')}")
