"""
Analyze the saved pumpenheizung HTML to understand structure
"""
from bs4 import BeautifulSoup

with open('pumpenheizung_page_test.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=== PRODUCT CONTAINERS ===")
# Look for common product container patterns
selectors = [
    'div[class*="product"]',
    'article[class*="product"]',
    'div[class*="item"]',
    'li[class*="product"]',
    'div[data-product]',
]

for selector in selectors:
    elements = soup.select(selector)
    if elements:
        print(f"\n{selector}: {len(elements)} found")
        if elements:
            first = elements[0]
            print(f"  Classes: {first.get('class', [])}")
            # Check for product links
            links = first.select('a[href]')
            if links:
                print(f"  Links in first: {len(links)}")
                print(f"  First link: {links[0].get('href', 'N/A')}")

print("\n\n=== PAGINATION ===")
# Look for pagination
pag_selectors = [
    '.pagination',
    '.pager',
    'nav.pagination',
    'ul.pagination',
    'div[class*="pag"]',
    'nav[role="navigation"]',
]

for selector in pag_selectors:
    elements = soup.select(selector)
    if elements:
        print(f"\n{selector}: {len(elements)} found")
        for elem in elements[:1]:
            links = elem.select('a[href]')
            print(f"  Links: {len(links)}")
            if links:
                print(f"  Sample hrefs:")
                for link in links[:5]:
                    text = link.get_text(strip=True)
                    href = link.get('href', 'N/A')
                    print(f"    '{text}': {href}")

print("\n\n=== ALL LINKS ANALYSIS ===")
all_links = soup.select('a[href]')
print(f"Total links: {len(all_links)}")

# Categorize by href pattern
internal_links = []
for link in all_links:
    href = link.get('href', '')
    if 'pumpen-heizung.de' in href or href.startswith('/'):
        internal_links.append(href)

print(f"Internal links: {len(internal_links)}")

# Count by slash depth
from collections import Counter
slash_counts = Counter()
for href in internal_links:
    if href.startswith('http'):
        path = href.split('pumpen-heizung.de')[-1]
    else:
        path = href
    slash_counts[path.count('/')] += 1

print("\nLinks by slash count:")
for count, num in sorted(slash_counts.items()):
    print(f"  {count} slashes: {num} links")
