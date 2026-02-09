"""Find real product URLs from wasserpumpe.de"""
import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)

# Get sitemap
sitemap_url = 'https://www.wasserpumpe.de/sitemap.xml'
response = scraper.get(sitemap_url, timeout=30)
soup = BeautifulSoup(response.text, 'xml')

urls = soup.find_all('loc')
print(f'Total URLs in sitemap: {len(urls)}')

# Look for product URLs (typically have brand names or model numbers)
product_urls = []
category_urls = []

for url_tag in urls:
    url = url_tag.text.strip()
    path = url.replace('https://www.wasserpumpe.de/', '').replace('https://wasserpumpe.de/', '')
    
    # Skip obvious non-products
    if any(skip in path for skip in [
        'rechtliches', 'datenschutz', 'impressum', 'uber-uns',
        'allgemeine-geschaftsbedingungen', 'review-policy', 'bestsellers',
        'pumpenkonfigurator'
    ]):
        continue
    
    # Skip homepage
    if not path or path == '/':
        continue
    
    # Products typically have:
    # - Brand names (dab, grundfos, etc.)
    # - Model numbers
    # - Longer paths with multiple dashes
    # - Specific patterns like "p-" prefix
    
    if path.startswith('p-') or path.startswith('product-'):
        product_urls.append(url)
    elif path.count('-') >= 4:  # Likely a product with detailed name
        product_urls.append(url)
    elif any(brand in path.lower() for brand in ['dab-', 'grundfos-', 'ebara-', 'pedrollo-', 'wilo-']):
        product_urls.append(url)
    else:
        category_urls.append(url)

print(f'\nPotential product URLs: {len(product_urls)}')
print(f'Category/info URLs: {len(category_urls)}')

# Test a few product URLs
print('\n' + '='*60)
print('Testing potential product URLs:')
print('='*60)

for test_url in product_urls[:5]:
    print(f'\nTesting: {test_url}')
    
    try:
        response = scraper.get(test_url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for product indicators
        h1 = soup.select_one('h1')
        title = h1.get_text(strip=True) if h1 else 'No title'
        
        # Look for price
        price_found = False
        for selector in ['span.price', 'div.price', '[class*="price"]']:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                if '€' in price_text or ',' in price_text:
                    print(f'  ✓ Title: {title[:50]}')
                    print(f'  ✓ Price: {price_text}')
                    price_found = True
                    break
        
        if not price_found:
            print(f'  ✗ Title: {title[:50]}')
            print(f'  ✗ No price found')
            
            # Check if it's actually a category page
            if 'kaufen' in title.lower() or 'top-deals' in title.lower():
                print(f'  → This looks like a category page')
    
    except Exception as e:
        print(f'  Error: {e}')

# If no products found, let's try to navigate from a category
if not product_urls:
    print('\n' + '='*60)
    print('No product URLs found in sitemap. Trying to find products from category pages...')
    print('='*60)
    
    # Try a category page
    category_url = 'https://www.wasserpumpe.de/tauchpumpe'
    print(f'\nFetching category: {category_url}')
    
    response = scraper.get(category_url, timeout=30)
    
    # Save HTML for inspection
    with open('wasserpumpe_category.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print('Saved HTML to wasserpumpe_category.html for inspection')
    
    # Look for product links in the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for common product link patterns
    all_links = soup.find_all('a', href=True)
    print(f'\nFound {len(all_links)} total links')
    
    # Filter for product-like links
    for link in all_links[:20]:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        if href and 'wasserpumpe.de' in href and text:
            print(f'  {href[:60]} -> {text[:40]}')
