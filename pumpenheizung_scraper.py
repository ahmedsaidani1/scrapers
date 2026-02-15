"""
Pumpen-Heizung Scraper
Website: https://pumpen-heizung.de
Strategy: Use Selenium to load homepage, extract product links from featured products
Note: Website is VERY slow (25+ seconds load time), uses JTL Shop 5
"""
import sys
import re
import time
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS, SCRAPER_CONFIGS


SCRAPER_NAME = "pumpenheizung"


class PumpenheizungScraper(BaseScraper):
    """
    Scraper for Pumpen-Heizung.de (Metallhandel Jobst)
    Uses Selenium due to slow load times and JavaScript requirements
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://pumpen-heizung.de")
        
        # Selenium driver (initialized on demand)
        self.driver = None
        
        self.logger.info(f"Initialized scraper for {self.base_url}")
    
    def init_driver(self):
        """Initialize Selenium driver with regular Chrome."""
        if self.driver:
            return
        
        try:
            self.logger.info("Initializing Selenium driver...")
            
            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(120)
            
            self.logger.info("Selenium driver initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize driver: {e}")
            raise
    
    def close_driver(self):
        """Close Selenium driver."""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.logger.info("Selenium driver closed")
            except Exception as e:
                self.logger.error(f"Error closing driver: {e}")
    
    def get_product_urls(self, max_urls: int = None) -> List[str]:
        """Get product URLs (required by BaseScraper)."""
        return self.get_product_urls_from_homepage(max_urls)
    
    def get_product_urls_from_homepage(self, max_urls: int = None) -> List[str]:
        """Extract product URLs from homepage featured products."""
        product_urls = []
        
        try:
            self.init_driver()
            
            self.logger.info(f"Loading homepage (this may take 30+ seconds)...")
            start_time = time.time()
            
            self.driver.get(self.base_url)
            
            # Wait for products to load
            try:
                WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".product-wrapper"))
                )
            except:
                self.logger.warning("Timeout waiting for products, continuing anyway...")
            
            elapsed = time.time() - start_time
            self.logger.info(f"Homepage loaded in {elapsed:.1f}s")
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find all product links
            # Based on HTML analysis: <a href="product-url"> inside .product-wrapper
            product_wrappers = soup.find_all('div', class_='product-wrapper')
            self.logger.info(f"Found {len(product_wrappers)} product wrappers")
            
            for wrapper in product_wrappers:
                link = wrapper.find('a', href=True)
                if link:
                    href = link['href']
                    
                    # Clean up URL
                    if href.startswith('/'):
                        href = self.base_url + href
                    elif not href.startswith('http'):
                        href = self.base_url + '/' + href
                    
                    # Skip cart, wishlist, etc.
                    if any(skip in href.lower() for skip in ['warenkorb', 'wunschliste', 'cart', 'wishlist']):
                        continue
                    
                    if href not in product_urls and href.startswith(self.base_url):
                        product_urls.append(href)
                        
                        if max_urls and len(product_urls) >= max_urls:
                            break
            
            self.logger.info(f"Extracted {len(product_urls)} product URLs from homepage")
            return product_urls
            
        except Exception as e:
            self.logger.error(f"Failed to get product URLs: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape individual product page using Selenium."""
        try:
            self.init_driver()
            
            self.driver.get(url)
            
            # Wait for product info to load
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[itemprop='name']"))
                )
            except:
                pass  # Continue anyway
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract product data
            product = {
                'article_number': '',
                'name': '',
                'price_net': '',
                'price_gross': '',
                'availability': '',
                'url': url,
                'category': '',
                'description': '',
                'ean': '',
                'manufacturer': ''
            }
            
            # Product name - from schema.org markup
            name_elem = soup.find(itemprop='name')
            if name_elem:
                product['name'] = name_elem.get_text(strip=True)
            
            # Price - from schema.org markup
            price_elem = soup.find(itemprop='price')
            if price_elem:
                price_content = price_elem.get('content', '')
                if price_content:
                    product['price_gross'] = price_content.replace('.', ',')  # Convert to German format
            
            # If no schema price, try visible price
            if not product['price_gross']:
                price_div = soup.find('div', class_='price')
                if price_div:
                    price_text = price_div.get_text(strip=True)
                    price_match = re.search(r'(\d+[\.,]\d+)', price_text)
                    if price_match:
                        product['price_gross'] = price_match.group(1)
            
            # Article number / SKU
            sku_elem = soup.find(itemprop='sku')
            if sku_elem:
                product['article_number'] = sku_elem.get_text(strip=True)
            
            # Availability
            avail_elem = soup.find(itemprop='availability')
            if avail_elem:
                product['availability'] = avail_elem.get('content', '').replace('https://schema.org/', '')
            
            # Description
            desc_elem = soup.find(itemprop='description')
            if desc_elem:
                product['description'] = desc_elem.get_text(strip=True)[:500]
            
            # Manufacturer
            brand_elem = soup.find(itemprop='brand')
            if brand_elem:
                brand_name = brand_elem.find(itemprop='name')
                if brand_name:
                    product['manufacturer'] = brand_name.get_text(strip=True)
            
            # Only return if we have at least name and price
            if product['name'] and product['price_gross']:
                return product
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to scrape product {url}: {e}")
            return None
    
    def run(self, max_products: int = None, concurrent_workers: int = 1) -> int:
        """Run the scraper. Note: Selenium doesn't support parallel workers."""
        try:
            self.logger.info(f"Starting {SCRAPER_NAME} scraper...")
            self.logger.info(f"Max products: {max_products if max_products else 'unlimited'}")
            self.logger.info("Note: This website is VERY slow, expect 30+ seconds per page")
            
            # Get product URLs from homepage
            product_urls = self.get_product_urls_from_homepage(max_urls=max_products)
            
            if not product_urls:
                self.logger.warning("No product URLs found")
                self.close_driver()
                return 0
            
            self.logger.info(f"Found {len(product_urls)} products to scrape")
            
            # Scrape products sequentially (Selenium doesn't parallelize well)
            products = []
            for i, url in enumerate(product_urls, 1):
                self.logger.info(f"[{i}/{len(product_urls)}] Scraping: {url}")
                product = self.scrape_product(url)
                if product:
                    products.append(product)
                
                # Be nice to the server
                time.sleep(2)
            
            # Close driver
            self.close_driver()
            
            if not products:
                self.logger.warning("No products scraped")
                return 0
            
            # Save to CSV
            self.logger.info(f"Saving {len(products)} products to CSV...")
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                from config import CSV_COLUMNS
                import csv
                writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                writer.writeheader()
                for product in products:
                    # Ensure all columns are present
                    row = {col: product.get(col, '') for col in CSV_COLUMNS}
                    writer.writerow(row)
            
            self.logger.info(f"Successfully scraped {len(products)} products")
            return len(products)
            
        except Exception as e:
            self.logger.error(f"Scraper failed: {e}")
            import traceback
            traceback.print_exc()
            self.close_driver()
            return 0


if __name__ == "__main__":
    import sys
    
    # Check if user wants production mode (all products)
    if len(sys.argv) > 1 and sys.argv[1] == '--production':
        print("=" * 80)
        print("PRODUCTION MODE: Scraping ALL products (no limit)")
        print("=" * 80)
        scraper = PumpenheizungScraper()
        count = scraper.run(max_products=None)  # Scrape ALL products
        print(f"\n✓ Production run complete: {count} products scraped")
    else:
        print("=" * 80)
        print("TEST MODE: Scraping 10 products")
        print("For production mode (all products), run: python pumpenheizung_scraper.py --production")
        print("=" * 80)
        scraper = PumpenheizungScraper()
        count = scraper.run(max_products=10)  # Test with 10 products
        print(f"\n✓ Test run complete: {count} products scraped")
