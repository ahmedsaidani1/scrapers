"""
Debug pumpen-heizung.de to see actual link structure
"""
import requests
from bs4 import BeautifulSoup
from collections import Counter

base_url = "https://pumpen-heizung.de"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print("Checking homepage...")
response = requests.get(base_url, headers=headers, timeout=30)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'html.parser')

# Find all internal links
internal_links = []
for link in soup.select('a[href]'):
    href = link.get('href', '').strip()
    if not href or href.startswith('#') or href.startswith('javascript:'):
        continue
    
    # Make absolute
    if href.startswith('/'):
        href = base_url + href
    elif not href.startswith('http'):
        continue
    
    if 'pumpen-heizung.de' in href:
        internal_links.append(href)

# Remove duplicates
internal_links = list(set(internal_links))
print(f"Total unique internal links: {len(internal_links)}\n")

# Analyze URL patterns
patterns = Counter()
for url in internal_links:
    path = url.replace(base_url, '')
    
    # Count slashes
    slash_count = path.count('/')
    patterns[f"{slash_count} slashes"] += 1
    
    # Check extensions
    if '.' in path.split('/')[-1]:
        ext = path.split('/')[-1].split('.')[-1]
        patterns[f".{ext} extension"] += 1
    else:
        patterns["no extension"] += 1

print("URL patterns:")
for pattern, count in patterns.most_common(10):
    print(f"  {pattern}: {count}")

print("\nSample URLs by slash count:")
for slash_count in range(1, 5):
    matching = [url for url in internal_links if url.replace(base_url, '').count('/') == slash_count]
    if matching:
        print(f"\n{slash_count} slashes ({len(matching)} URLs):")
        for url in matching[:5]:
            print(f"  {url}")
