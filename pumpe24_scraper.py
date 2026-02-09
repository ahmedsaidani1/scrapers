"""
Pumpe24 Scraper with Cloudscraper (bypasses Cloudflare protection)
Website: https://www.pumpe24.de
Platform: Magento (Cloudflare protected)
Strategy: Scrape from category pages using cloudscraper
"""
import sys
import re
import time
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
import cloudscraper
from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS, SCRAPER_CONFIGS


SCRAPER_NAME = "pumpe24"


class Pumpe24Scraper(BaseScraper):
    """
    Scraper for Pumpe24 using cloudscraper to bypass Cloudflare protection.
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://www.pumpe24.de")
        
        # Initialize cloudscraper session
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        # Main category URLs to scrape
        self.category_urls = [
            "https://www.pumpe24.de/pumpen.html",
            "https://www.pumpe24.de/hauswasserwerke.html",
            "https://www.pumpe24.de/druckbehaelter.html",
            "https://www.pumpe24.de/zubehoer.html",
            "https://www.pumpe24.de/rohre-fittings.html",
        ]
        
        self.logger.info(f"Initialized cloudscraper for {self.base_url}")
    
    def make_request(self, url: str, **kwargs):
        """Override to use cloudscraper instead of requests."""
        try:
            response = self.scraper.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None
    
    def get_product_urls(self, max_urls: int = None) -> List[str]:
        """
        Get product URLs by scraping category pages and finding actual products.
        """
        product_urls = []
        
        try:
            self.logger.info(f"Scraping {len(self.category_urls)} category pages...")
            
            for i, category_url in enumerate(self.category_urls, 1):
                self.logger.info(f"[{i}/{len(self.category_urls)}] Scraping category: {category_url}")
                
                response = self.make_request(category_url)
                if not response:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find product links (Magento structure)
                # Look for actual product item links (not subcategories)
                product_links = soup.select('a.product-item-link')
                
                for link in product_links:
                    href = link.get('href', '')
                    # Real products have longer URLs and don't end with just category names
                    # They typically have product-specific identifiers
                    if href and href.startswith('http') and '.html' in href:
                        # Skip if it looks like a subcategory (short path, generic name)
                        path_parts = href.replace(self.base_url, '').split('/')
                        # Products usually have longer, more specific URLs
                        if len(path_parts) > 2 or any(char.isdigit() for char in href):
                            if href not in product_urls:
                                product_urls.append(href)
                
                self.logger.info(f"  Found {len(product_links)} links, {len(product_urls)} total products")
                
                if max_urls and len(product_urls) >= max_urls:
                    break
                
                time.sleep(2)
            
            self.logger.info(f"Total product URLs found: {len(product_urls)}")
            
        except Exception as e:
            self.logger.error(f"Error getting product URLs: {e}", exc_info=True)
        
        return product_urls[:max_urls] if max_urls else product_urls
    
    def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape individual product page."""
        response = self.make_request(url)
        if not response:
            return None
        
        try:
            soup = self.parse_html(response.text)
            
            # Extract product name/title (Magento structure)
            product_name = self._extract_text(soup, [
                'h1.page-title span',
                'h1.product-name',
                'h1[itemprop="name"]',
                'h1'
            ])
            
            if not product_name:
                self.logger.warning(f"No product name found for {url}")
                return None
            
            # Extract manufacturer/brand
            manufacturer = self._extract_text(soup, [
                'a.product-manufacturer',
                'span[itemprop="brand"]',
                'div.product-brand',
                'meta[itemprop="brand"]'
            ])
            
            # Extract category from breadcrumbs
            category = self._extract_text(soup, [
                'ul.breadcrumbs li:nth-last-child(2) a',
                'nav.breadcrumb li:nth-last-child(2) a',
                'div.breadcrumbs a:last-of-type'
            ])
            
            # Extract article number/SKU
            article_number = self._extract_text(soup, [
                'div.product-info-stock-sku div.value',
                'span[itemprop="sku"]',
                'div.product-sku',
                'meta[itemprop="sku"]'
            ])
            
            # Extract price (gross - with VAT)
            price_gross_raw = self._extract_text(soup, [
                'span.price',
                'span[itemprop="price"]',
                'div.product-info-price span.price',
                'meta[itemprop="price"]'
            ])
            
            price_gross = self._clean_price(price_gross_raw)
            
            # Calculate net price (German VAT is 19%)
            price_net = ""
            if price_gross:
                try:
                    gross_float = float(price_gross.replace(',', '.'))
                    net_float = gross_float / 1.19
                    price_net = f"{net_float:.2f}".replace('.', ',')
                except:
                    pass
            
            # Extract EAN
            ean = self._extract_text(soup, [
                'span[itemprop="gtin13"]',
                'div.product-ean',
                'meta[itemprop="gtin13"]'
            ])
            
            # Extract image
            product_image = self._extract_image(soup, [
                'img.gallery-placeholder__image',
                'img[itemprop="image"]',
                'div.product-image-container img',
                'meta[property="og:image"]'
            ])
            
            product_data = {
                'manufacturer': manufacturer,
                'category': category,
                'name': product_name,
                'title': product_name,
                'article_number': article_number,
                'price_net': price_net,
                'price_gross': price_gross,
                'ean': ean,
                'product_image': product_image,
                'product_url': url
            }
            
            return product_data
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}", exc_info=True)
            return None
    
    def _extract_text(self, soup, selectors: List[str], default: str = "") -> str:
        """Try multiple selectors and return first match."""
        for selector in selectors:
            if selector.startswith('meta'):
                meta = soup.select_one(selector)
                if meta and meta.get('content'):
                    return meta.get('content').strip()
            else:
                element = soup.select_one(selector)
                if element:
                    text = element.text.strip() if hasattr(element, 'text') else element.get('content', '')
                    if text:
                        return text.strip()
        return default
    
    def _extract_image(self, soup, selectors: List[str]) -> str:
        """Extract image URL."""
        for selector in selectors:
            if selector.startswith('meta'):
                meta = soup.select_one(selector)
                if meta and meta.get('content'):
                    url = meta.get('content')
                    if url.startswith('//'):
                        url = 'https:' + url
                    elif url.startswith('/'):
                        url = self.base_url + url
                    return url
            else:
                img = soup.select_one(selector)
                if img:
                    for attr in ['src', 'data-src', 'data-lazy-src']:
                        if attr in img.attrs:
                            url = img[attr]
                            if url.startswith('//'):
                                url = 'https:' + url
                            elif url.startswith('/'):
                                url = self.base_url + url
                            return url
        return ""
    
    def _clean_price(self, price_str: str) -> str:
        """Clean price format."""
        if not price_str:
            return ""
        price = re.sub(r'[^\d,.]', '', price_str)
        return price.strip()
    
    def run(self, max_products: int = None, concurrent_workers: int = 10) -> int:
        """Run the scraper with optional product limit and concurrent workers."""
        try:
            self.logger.info(f"Starting {SCRAPER_NAME} scraper...")
            
            # Get product URLs
            product_urls = self.get_product_urls(max_urls=max_products)
            
            if not product_urls:
                self.logger.error("No product URLs found")
                return 0
            
            self.logger.info(f"Found {len(product_urls)} products to scrape")
            
            # Use parent class concurrent scraping
            from concurrent.futures import ThreadPoolExecutor, as_completed
            import time
            import random
            
            success_count = 0
            
            with ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
                future_to_url = {
                    executor.submit(self._scrape_with_delay, url): url 
                    for url in product_urls
                }
                
                for i, future in enumerate(as_completed(future_to_url), 1):
                    url = future_to_url[future]
                    
                    if i % 10 == 0:
                        self.logger.info(f"Progress: {i}/{len(product_urls)} products processed")
                    
                    try:
                        product_data = future.result()
                        
                        if product_data:
                            self.save_product(product_data)
                            success_count += 1
                    
                    except Exception as e:
                        self.logger.error(f"Error processing {url}: {e}")
            
            self.logger.info(f"Scraping completed: {success_count}/{len(product_urls)} products")
            
            return success_count
            
        except Exception as e:
            self.logger.error(f"Error in run: {e}", exc_info=True)
            return 0
    
    def _scrape_with_delay(self, url: str):
        """Scrape with minimal delay for concurrent execution."""
        try:
            import time, random
            time.sleep(random.uniform(0.05, 0.15))
            return self.scrape_product(url)
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None


def main():
    """Main execution."""
    scraper = Pumpe24Scraper()
    success_count = scraper.run()
    
    # Push to Google Sheets if requested
    if "--push-to-sheets" in sys.argv and success_count > 0:
        sheet_id = SHEET_IDS.get(SCRAPER_NAME)
        
        if sheet_id and sheet_id != "TBD":
            print(f"\nPushing data to Google Sheets...")
            if push_data(sheet_id, scraper.get_output_file()):
                print("✓ Successfully pushed to Google Sheets")
            else:
                print("✗ Failed to push to Google Sheets")
        else:
            print(f"\n⚠ No Google Sheet ID configured for {SCRAPER_NAME}")
    
    print(f"\n{'='*60}")
    print(f"Completed: {success_count} products scraped")
    print(f"Output: {scraper.get_output_file()}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
