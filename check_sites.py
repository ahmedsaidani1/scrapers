"""Check remaining sites to identify easiest to scrape"""
import requests
from bs4 import BeautifulSoup

sites = [
    "https://pumpen-heizung.de",
    "https://pumpe24.de",
    "https://wasserpumpe.de",
    "https://st-shop24.de",
    "https://selfio.de",
    "https://glo24.de"
]

for site in sites:
    try:
        print(f"\n{'='*60}")
        print(f"Checking: {site}")
        print('='*60)
        
        r = requests.get(site, timeout=10, allow_redirects=True)
        print(f"Status: {r.status_code}")
        print(f"Final URL: {r.url}")
        
        # Check for platform indicators
        text_lower = r.text.lower()
        
        if 'shopware' in text_lower:
            print("Platform: Shopware ✓ (Easy)")
        elif 'woocommerce' in text_lower or 'wp-content' in text_lower:
            print("Platform: WooCommerce/WordPress ✓ (Easy)")
        elif 'magento' in text_lower:
            print("Platform: Magento (Medium)")
        elif 'jtl' in text_lower:
            print("Platform: JTL-Shop ✓ (Easy)")
        else:
            print("Platform: Unknown/Custom")
        
        # Check for sitemap
        sitemap_url = site + "/sitemap.xml"
        try:
            s = requests.get(sitemap_url, timeout=5)
            if s.status_code == 200:
                print(f"Sitemap: Available ✓")
                soup = BeautifulSoup(s.text, 'xml')
                urls = soup.find_all('loc')
                product_urls = [u.text for u in urls if 'product' in u.text.lower() or '.html' in u.text]
                print(f"Product URLs in sitemap: ~{len(product_urls)}")
            else:
                print(f"Sitemap: Not found")
        except:
            print("Sitemap: Not accessible")
            
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*60)
print("RECOMMENDATION: Start with sites that have Shopware/WooCommerce + Sitemap")
print("="*60)
