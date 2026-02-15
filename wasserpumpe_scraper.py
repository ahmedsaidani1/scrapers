"""
Wasserpumpe Scraper with Selenium (JavaScript-rendered site)
Website: https://wasserpumpe.de
Platform: Vue.js SPA
"""
import sys
import re
import time
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS, SCRAPER_CONFIGS


SCRAPER_NAME = "wasserpumpe"


class WasserpumpeScraper(BaseScraper):
    """
    Scraper for Wasserpumpe.de using Selenium (Vue.js site requires JavaScript execution).
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://wasserpumpe.de")
        
        # Initialize Selenium driver with memory optimization
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Memory optimization for low-RAM environments (512MB)
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-dev-tools')
        chrome_options.add_argument('--single-process')  # Use single process (less memory)
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--metrics-recording-only')
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--safebrowsing-disable-auto-update')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--disable-accelerated-2d-canvas')
        chrome_options.add_argument('--disable-accelerated-jpeg-decoding')
        chrome_options.add_argument('--disable-accelerated-mjpeg-decode')
        chrome_options.add_argument('--disable-accelerated-video-decode')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-breakpad')
        chrome_options.add_argument('--disable-component-extensions-with-background-pages')
        chrome_options.add_argument('--disable-features=TranslateUI,BlinkGenPropertyTrees')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
        chrome_options.add_argument('--force-color-profile=srgb')
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument('--memory-pressure-off')
        chrome_options.add_argument('--disable-hang-monitor')
        chrome_options.add_argument('--disable-prompt-on-repost')
        chrome_options.add_argument('--disable-domain-reliability')
        chrome_options.add_argument('--disable-features=AudioServiceOutOfProcess')
        chrome_options.add_argument('--window-size=1024,768')  # Smaller window = less memory
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Main category URLs to scrape
        self.category_urls = [
            "https://wasserpumpe.de/tauchpumpe",
            "https://wasserpumpe.de/gartenpumpe",
            "https://wasserpumpe.de/hauswasserwerk",
        ]
        
        self.logger.info(f"Initialized Selenium driver for {self.base_url}")
    
    
    def __del__(self):
        """Cleanup Selenium driver."""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
        except:
            pass
    
    def get_product_urls(self, max_urls: int = None) -> List[str]:
        """
        Get product URLs from category pages (Vue.js site).
        """
        product_urls = []
        
        try:
            for category_url in self.category_urls:
                self.logger.info(f"Fetching category: {category_url}")
                
                self.driver.get(category_url)
                time.sleep(5)  # Wait for JavaScript to load
                
                # Find product links
                try:
                    # Look for product links in the rendered page
                    links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href]')
                    
                    for link in links:
                        href = link.get_attribute('href')
                        
                        if not href or 'wasserpumpe.de' not in href:
                            continue
                        
                        # Normalize URL
                        href = href.split('?')[0].split('#')[0]  # Remove query params and fragments
                        
                        # Filter for product pages (not categories or info pages)
                        if any(skip in href for skip in [
                            '/rechtliches', '/datenschutz', '/impressum', '/uber-uns',
                            '/allgemeine-geschaftsbedingungen', '/review-policy', 
                            '/bestsellers', '/kundenservice', '/blog', '/kontakt',
                            '/login', '/typ-wasserpumpe', '/winter-deals',
                            'b2b.wasserpumpe', '/lieferung', '/wahlhilfe',
                            '/pumpenkonfigurator', '/zubehoer'
                        ]):
                            continue
                        
                        # Skip if it's the category URL itself
                        if href == category_url or href + '/' == category_url or href == category_url + '/':
                            continue
                        
                        # Products typically have longer paths with multiple dashes
                        path = href.replace('https://www.wasserpumpe.de/', '').replace('https://wasserpumpe.de/', '')
                        
                        # Look for product-like patterns:
                        # - Has at least 3 dashes (e.g., dab-nova-up-300-m-ae-flachsauger-tauchpumpe)
                        # - Not ending with slash (categories often end with /)
                        # - Not too short (categories are usually short like /tauchpumpe)
                        if path.count('-') >= 3 and not path.endswith('/') and len(path) > 15:
                            if href not in product_urls:
                                product_urls.append(href)
                                self.logger.debug(f"Found product: {href}")
                
                except Exception as e:
                    self.logger.error(f"Error extracting links from {category_url}: {e}")
                
                if max_urls and len(product_urls) >= max_urls:
                    break
            
            self.logger.info(f"Found {len(product_urls)} product URLs")
            
        except Exception as e:
            self.logger.error(f"Error getting product URLs: {e}", exc_info=True)
        
        return product_urls[:max_urls] if max_urls else product_urls
    
    
    def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape individual product page using Selenium."""
        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for JavaScript to render
            
            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract product name/title
            product_name = ""
            try:
                h1 = self.driver.find_element(By.TAG_NAME, 'h1')
                product_name = h1.text.strip()
            except:
                product_name = self._extract_text(soup, [
                    'h1.page-title span',
                    'h1.product-name',
                    'h1[itemprop="name"]',
                    'h1'
                ])
            
            if not product_name:
                self.logger.warning(f"No product name found for {url}")
                return None
            
            manufacturer = self._extract_text(soup, [
                'a.product-manufacturer',
                'span[itemprop="brand"]',
                'div.product-brand',
                'meta[itemprop="brand"]',
                '[itemprop="brand"]'
            ])
            
            category = self._extract_text(soup, [
                'ul.breadcrumbs li:nth-last-child(2) a',
                'nav.breadcrumb li:nth-last-child(2) a',
                'div.breadcrumbs a:last-of-type'
            ])
            
            article_number = self._extract_text(soup, [
                'div.product-info-stock-sku div.value',
                'span[itemprop="sku"]',
                'div.product-sku',
                'meta[itemprop="sku"]',
                '[itemprop="sku"]'
            ])
            
            # Extract price - look for price in rendered content
            price_gross_raw = ""
            try:
                # Try to find price elements with Selenium first
                price_elements = self.driver.find_elements(By.CSS_SELECTOR, '[class*="price"]')
                for elem in price_elements:
                    text = elem.text.strip()
                    # Look for price pattern (number with comma/dot)
                    if re.search(r'\d+[,\.]\d{2}', text):
                        price_gross_raw = text
                        break
            except:
                pass
            
            # Fallback to BeautifulSoup
            if not price_gross_raw:
                price_gross_raw = self._extract_text(soup, [
                    'span.price',
                    'span[itemprop="price"]',
                    'div.product-info-price span.price',
                    'meta[itemprop="price"]'
                ])
            
            # Also check JSON-LD data
            if not price_gross_raw:
                try:
                    # Look for price in page source using regex
                    price_match = re.search(r'"price":\s*"?([\d,\.]+)"?', page_source)
                    if price_match:
                        price_gross_raw = price_match.group(1)
                except:
                    pass
            
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
                'span[itemprop="gtin13"]',
                'div.product-ean',
                'meta[itemprop="gtin13"]'
            ])
            
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
        """Clean price format - extract only the first valid price."""
        if not price_str:
            return ""
        
        # Remove currency symbols and extra whitespace
        price = price_str.replace('€', '').replace('EUR', '').strip()
        
        # Find the first price pattern (digits with comma or dot as decimal separator)
        # Match patterns like: 189,90 or 189.90
        match = re.search(r'(\d+[,\.]\d{2})', price)
        if match:
            return match.group(1)
        
        # If no decimal found, try to find just digits
        match = re.search(r'(\d+)', price)
        if match:
            return match.group(1)
        
        return ""
    
    
    def run(self, max_products: int = None, concurrent_workers: int = 1) -> int:
        """Run the scraper with optional product limit. Note: Selenium doesn't support concurrent workers."""
        try:
            self.logger.info(f"Starting {SCRAPER_NAME} scraper...")
            
            product_urls = self.get_product_urls(max_urls=max_products)
            
            if not product_urls:
                self.logger.error("No product URLs found")
                return 0
            
            self.logger.info(f"Found {len(product_urls)} products to scrape")
            
            # Scrape products sequentially (Selenium doesn't support concurrent execution well)
            success_count = 0
            
            for i, url in enumerate(product_urls, 1):
                if i % 10 == 0:
                    self.logger.info(f"Progress: {i}/{len(product_urls)} products processed")
                
                try:
                    product_data = self.scrape_product(url)
                    
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
        finally:
            # Cleanup driver
            try:
                self.driver.quit()
            except:
                pass


def main():
    """Main execution."""
    scraper = WasserpumpeScraper()
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
