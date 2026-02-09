"""
Glo24 Scraper with Cloudscraper (bypasses Cloudflare protection)
Website: https://glo24.de
Platform: Unknown (Cloudflare protected)
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


SCRAPER_NAME = "glo24"


class Glo24Scraper(BaseScraper):
    """
    Scraper for Glo24.de using cloudscraper to bypass Cloudflare protection.
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://glo24.de")
        
        # German proxy configuration (if needed)
        # Option 1: Set proxy in environment variables or config
        # Option 2: Pass directly to cloudscraper
        self.proxy = self.config.get("proxy", None)  # e.g., "http://proxy-server:port"
        
        # Initialize cloudscraper session
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        # Configure proxy if provided
        if self.proxy:
            self.scraper.proxies = {
                'http': self.proxy,
                'https': self.proxy
            }
            self.logger.info(f"Using proxy: {self.proxy}")
        
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
        Get product URLs from sitemap.
        """
        product_urls = []
        
        try:
            self.logger.info("Fetching sitemap...")
            response = self.make_request(f"{self.base_url}/sitemap.xml")
            
            if not response:
                self.logger.error("Failed to fetch sitemap")
                return product_urls
            
            soup = BeautifulSoup(response.text, 'xml')
            
            # Check if it's a sitemap index
            sitemap_locs = soup.find_all('sitemap')
            
            if sitemap_locs:
                self.logger.info(f"Found {len(sitemap_locs)} sub-sitemaps")
                
                # Process first few sitemaps
                for i, sitemap in enumerate(sitemap_locs[:5], 1):
                    loc = sitemap.find('loc')
                    if loc:
                        sub_url = loc.text.strip()
                        self.logger.info(f"Processing sitemap {i}: {sub_url}")
                        
                        sub_response = self.make_request(sub_url)
                        if sub_response:
                            sub_soup = BeautifulSoup(sub_response.text, 'xml')
                            urls = sub_soup.find_all('loc')
                            
                            for url_tag in urls:
                                url = url_tag.text.strip()
                                if self._is_product_url(url):
                                    product_urls.append(url)
                            
                            self.logger.info(f"  Found {len(urls)} URLs (total products: {len(product_urls)})")
                            
                            if max_urls and len(product_urls) >= max_urls:
                                break
                        
                        time.sleep(1)
            else:
                # Direct sitemap
                urls = soup.find_all('loc')
                self.logger.info(f"Found {len(urls)} URLs in sitemap")
                
                for url_tag in urls:
                    url = url_tag.text.strip()
                    if self._is_product_url(url):
                        product_urls.append(url)
            
            self.logger.info(f"Total product URLs found: {len(product_urls)}")
            
        except Exception as e:
            self.logger.error(f"Error getting product URLs: {e}", exc_info=True)
        
        return product_urls[:max_urls] if max_urls else product_urls
    
    def _is_product_url(self, url: str) -> bool:
        """Determine if URL is a product page."""
        # Skip info pages
        skip_patterns = [
            '/impressum', '/datenschutz', '/agb', '/kontakt',
            '/uber-uns', '/rechtliches', '/versand', '/zahlung'
        ]
        
        for pattern in skip_patterns:
            if pattern in url.lower():
                return False
        
        # Skip homepage
        if url == self.base_url or url == f"{self.base_url}/":
            return False
        
        # Skip categories (ending with /)
        if url.endswith('/'):
            return False
        
        return True
    
    def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape individual product page."""
        response = self.make_request(url)
        if not response:
            return None
        
        try:
            soup = self.parse_html(response.text)
            
            # Extract product name/title
            product_name = self._extract_text(soup, [
                'h1.product-name',
                'h1.product-title',
                'h1[itemprop="name"]',
                'h1.page-title',
                'h1'
            ])
            
            if not product_name:
                self.logger.warning(f"No product name found for {url}")
                return None
            
            manufacturer = self._extract_text(soup, [
                'span.manufacturer',
                'a.brand',
                'span[itemprop="brand"]',
                'div.product-manufacturer',
                'meta[itemprop="brand"]'
            ])
            
            category = self._extract_text(soup, [
                'nav.breadcrumb li:nth-last-child(2) a',
                'ul.breadcrumbs li:nth-last-child(2) a',
                'div.breadcrumbs a:last-of-type'
            ])
            
            article_number = self._extract_text(soup, [
                'span.sku',
                'span[itemprop="sku"]',
                'div.article-number',
                'div.product-sku',
                'meta[itemprop="sku"]'
            ])
            
            price_gross_raw = self._extract_text(soup, [
                'span.price',
                'span[itemprop="price"]',
                'div.product-price',
                'meta[itemprop="price"]'
            ])
            
            price_gross = self._clean_price(price_gross_raw)
            
            # Calculate net price
            price_net = ""
            if price_gross:
                try:
                    gross_float = float(price_gross.replace(',', '.'))
                    net_float = gross_float / 1.19
                    price_net = f"{net_float:.2f}".replace('.', ',')
                except:
                    pass
            
            ean = self._extract_text(soup, [
                'span.ean',
                'span[itemprop="gtin13"]',
                'div.product-ean',
                'meta[itemprop="gtin13"]'
            ])
            
            product_image = self._extract_image(soup, [
                'img.product-image',
                'img[itemprop="image"]',
                'div.product-gallery img',
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
    
    def run(self, max_products: int = None) -> int:
        """Run the scraper with optional product limit."""
        try:
            self.logger.info(f"Starting {SCRAPER_NAME} scraper...")
            
            product_urls = self.get_product_urls(max_urls=max_products)
            
            if not product_urls:
                self.logger.error("No product URLs found")
                return 0
            
            self.logger.info(f"Found {len(product_urls)} products to scrape")
            
            success_count = 0
            
            for i, url in enumerate(product_urls, 1):
                self.logger.info(f"[{i}/{len(product_urls)}] Processing: {url}")
                
                product_data = self.scrape_product(url)
                
                if product_data:
                    self.save_product(product_data)
                    success_count += 1
                
                self._random_delay()
            
            self.logger.info(f"Scraping completed: {success_count}/{len(product_urls)} products")
            
            return success_count
            
        except Exception as e:
            self.logger.error(f"Error in run: {e}", exc_info=True)
            return 0


def main():
    """Main execution."""
    scraper = Glo24Scraper()
    success_count = scraper.run()
    
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
