"""
Debug wolfonlineshop - explore category structure deeply
"""
import requests
from bs4 import BeautifulSoup
import time

base_url = "https://www.heat-store.de"

def get_subcategories(url):
    """Get subcategories from a category page"""
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for category links
        cat_links = soup.select('a.category-link, a[href*="/heizung/"]')
        
        subcats = set()
        for link in cat_links:
            href = link.get('href', '')
            if href and '/heizung/' in href and href != url:
                if href.startswith('/'):
                    href = base_url + href
                # Only add if it's a deeper category
                if href.startswith(url) or len(href) > len(url):
                    subcats.add(href)
        
        return list(subcats)
    except Exception as e:
        print(f"Error getting subcategories from {url}: {e}")
        return []

def get_products_from_category(url):
    """Get product count from a category"""
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        products = soup.select('div.product-box')
        return len(products)
    except:
        return 0

print("=== EXPLORING CATEGORY STRUCTURE ===\n")

# Start with main categories
main_categories = [
    f"{base_url}/heizung//",
    f"{base_url}/heizung/heizkoerper//",
    f"{base_url}/heizung/gas-heizung//",
    f"{base_url}/heizung/oel-heizung//",
    f"{base_url}/heizung/holz-heizung//",
    f"{base_url}/elektro//",
    f"{base_url}/kamin//",
]

all_categories = set(main_categories)
to_explore = list(main_categories)
explored = set()

# Explore up to 3 levels deep
for level in range(3):
    print(f"\n--- LEVEL {level + 1} ---")
    next_to_explore = []
    
    for cat_url in to_explore:
        if cat_url in explored:
            continue
        
        print(f"Exploring: {cat_url}")
        explored.add(cat_url)
        
        # Get products
        product_count = get_products_from_category(cat_url)
        print(f"  Products: {product_count}")
        
        # Get subcategories
        subcats = get_subcategories(cat_url)
        if subcats:
            print(f"  Subcategories: {len(subcats)}")
            for subcat in subcats[:3]:
                print(f"    - {subcat}")
            all_categories.update(subcats)
            next_to_explore.extend(subcats)
        
        time.sleep(0.5)
    
    to_explore = next_to_explore
    if not to_explore:
        break

print(f"\n\n=== SUMMARY ===")
print(f"Total categories found: {len(all_categories)}")
print(f"\nAll categories:")
for cat in sorted(all_categories):
    print(f"  {cat}")
