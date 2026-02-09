"""
Akusolar Scraper with Selenium - For JavaScript-rendered content
Website: https://www.akusolar.cz / https://akusolar.fcostry3.cz
"""
import sys
import re
import time
from typing import List, Dict, Optional, Any
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS, SCRAPER_CONFIGS


SCRAPER_NAME = "akusolar"


class AkusolarSeleniumScraper(BaseScraper):
    """
    Scraper for Akusolar using Selenium for JavaScript-rendered content.
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        # Get website-specific config
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = "https://akusolar.fcostry3.cz"
        
        # Setup Selenium
        self.driver = None
        self._setup_selenium()
        
        self.logger.info(f"Initialized Selenium scraper for {self.base_url}")
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver with Chrome."""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--allow-insecure-localhost')
            
            # Add user agent
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Setup driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.logger.info("Selenium WebDriver initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Selenium: {e}")
            raise
    
    def get_product_urls(self) -> List[str]:
        """
        Get list of product URLs using Selenium to handle JavaScript.
        """
        product_urls = []
        
        try:
            self.logger.info(f"Loading homepage with Selenium: {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find all links
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '')
                
                # Look for product-like URLs
                if any(keyword in href.lower() for keyword in [
                    'rozvodnicova-skrin',
                    'fotovoltaicky-panel',
                    'panel',
                    'invertor',
                    'menic',
                    'baterie',
                    'produkt'
                ]):
                    # Make absolute URL
                    if href.startswith('/'):
                        href = self.base_url + href
                    elif not href.startswith('http'):
                        continue
                    
                    # Avoid duplicates
                    if href not in product_urls and self.base_url in href:
                        product_urls.append(href)
            
            self.logger.info(f"Found {len(product_urls)} product URLs")
            
            # If still no products, try to find any product cards or listings
            if not product_urls:
                self.logger.info("Trying to find product cards...")
                product_cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(k in str(x).lower() for k in ['product', 'item', 'card']))
                self.logger.info(f"Found {len(product_cards)} potential product cards")
                
                for card in product_cards:
                    link = card.find('a', href=True)
                    if link:
                        href = link.get('href')
                        if href.startswith('/'):
                            href = self.base_url + href
                        if href not in product_urls:
                            product_urls.append(href)
            
        except Exception as e:
            self.logger.error(f"Error getting product URLs: {e}", exc_info=True)
        
        return product_urls
    
    def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape individual product page using Selenium.
        """
        try:
            self.logger.info(f"Loading product page: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract product name
            product_name = self._extract_text(soup, [
                'h1.product-title',
                'h1[itemprop="name"]',
                'h1.product-name',
                'h1.title',
                'h1'
            ])
            
            # Extract SKU
            sku = self._extract_text(soup, [
                'span.sku',
                '[itemprop="sku"]',
                'span.product-code',
                'div.product-number'
            ])
            
            # Extract category
            category = self._extract_text(soup, [
                'span.category',
                'a.breadcrumb-item:last-child',
                '[itemprop="category"]',
                'nav.breadcrumb a:last-child'
            ])
            
            # Infer category from URL if not found
            if not category:
                if 'rozvodnicova' in url.lower():
                    category = "Rozvodnicová skříň"
                elif 'panel' in url.lower():
                    category = "Fotovoltaický panel"
            
            # Extract price
            price_raw = self._extract_text(soup, [
                'span.price',
                '[itemprop="price"]',
                'span.product-price',
                'div.price',
                'span.cena'
            ])
            price = self._clean_price(price_raw)
            
            # Extract availability
            availability = self._extract_text(soup, [
                'span.availability',
                '[itemprop="availability"]',
                'span.stock-status',
                'div.dostupnost'
            ], default="In Stock")
            
            # Extract description
            description = self._extract_text(soup, [
                'div.product-description',
                '[itemprop="description"]',
                'div.description',
                'div.popis',
                'meta[name="description"]'
            ])
            
            # Try meta description
            if not description:
                meta_desc = soup.select_one('meta[name="description"]')
                if meta_desc and meta_desc.get('content'):
                    description = meta_desc.get('content')
            
            # Limit description length
            if description and len(description) > 500:
                description = description[:497] + "..."
            
            # Extract image
            product_image = self._extract_image(soup, [
                'img.product-image',
                '[itemprop="image"]',
                'img.main-image',
                'div.product-image img',
                'meta[property="og:image"]'
            ])
            
            # Validate minimum required data
            if not product_name:
                self.logger.warning(f"No product name found for {url}")
                return None
            
            product_data = {
                'product_name': product_name,
                'sku': sku,
                'category': category,
                'price': price,
                'availability': availability,
                'description': description,
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
                    return meta.get('content')
            else:
                element = soup.select_one(selector)
                if element:
                    return element.text.strip()
        return default
    
    def _extract_image(self, soup, selectors: List[str]) -> str:
        """Extract image URL from multiple possible selectors."""
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
        """Clean and standardize price format."""
        if not price_str:
            return ""
        price = re.sub(r'[^\d,.]', '', price_str)
        return price.strip()
    
    def run(self) -> int:
        """Override run method to ensure driver cleanup."""
        try:
            return super().run()
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("Selenium WebDriver closed")


def main():
    """Main execution."""
    scraper = AkusolarSeleniumScraper()
    success_count = scraper.run()
    
    # Push to Google Sheets if requested
    if "--push-to-sheets" in sys.argv and success_count > 0:
        sheet_id = SHEET_IDS.get(SCRAPER_NAME)
        
        if sheet_id:
            print(f"\nPushing data to Google Sheets...")
            if push_data(sheet_id, scraper.get_output_file()):
                print("✓ Successfully pushed to Google Sheets")
            else:
                print("✗ Failed to push to Google Sheets")
        else:
            print(f"\n⚠ No Google Sheet ID configured")
    
    print(f"\n{'='*60}")
    print(f"Completed: {success_count} products scraped")
    print(f"Output: {scraper.get_output_file()}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
