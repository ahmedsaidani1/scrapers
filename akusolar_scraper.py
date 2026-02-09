"""
Akusolar Scraper - No Login Required
Website: https://www.akusolar.cz
"""
import sys
import re
from typing import List, Dict, Optional, Any
from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS, SCRAPER_CONFIGS


SCRAPER_NAME = "akusolar"


class AkusolarScraper(BaseScraper):
    """
    Scraper for Akusolar solar equipment website.
    No login required.
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        # Get website-specific config
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        # The actual e-shop redirects to akusolar.fcostry3.cz
        self.base_url = "https://akusolar.fcostry3.cz"
        
        # Disable SSL warnings for this site (expired certificate)
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.logger.info(f"Initialized scraper for {self.base_url}")
    
    def get_product_urls(self) -> List[str]:
        """
        Get list of product URLs to scrape.
        
        Strategy:
        1. Scrape homepage for product links
        2. Use known product URLs (this site has very few products)
        """
        product_urls = []
        
        # Scrape homepage for product links
        self.logger.info("Scraping homepage for product links...")
        response = self.make_request(self.base_url, verify=False)
        
        if response:
            soup = self.parse_html(response.text)
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
                    'baterie'
                ]):
                    # Make absolute URL
                    if href.startswith('/'):
                        href = self.base_url + href
                    elif not href.startswith('http'):
                        continue
                    
                    # Avoid duplicates
                    if href not in product_urls and self.base_url in href:
                        product_urls.append(href)
            
            self.logger.info(f"Found {len(product_urls)} product URLs from homepage")
        
        # Add known products if we didn't find any
        if not product_urls:
            self.logger.info("No products found, using known product URLs...")
            known_products = [
                f"{self.base_url}/kompletni-certifikovana-rozvodnicova-skrin-rs-fve-dc1",
                f"{self.base_url}/kompletni-certifikovana-rozvodnicova-skrin-rs-fve-dc2",
            ]
            product_urls.extend(known_products)
        
        return product_urls
    
    def _scrape_category_pages(self) -> List[str]:
        """Fallback: scrape product links from category/listing pages."""
        product_urls = []
        
        # Common category URLs for solar equipment (based on actual site structure)
        category_urls = [
            f"{self.base_url}/fotovoltaicke-panely",
            f"{self.base_url}/tasky-pro-fve",
            f"{self.base_url}/menic",
            f"{self.base_url}/baterie",
        ]
        
        for category_url in category_urls:
            self.logger.info(f"Scraping category: {category_url}")
            response = self.make_request(category_url, verify=False)  # Disable SSL verification
            
            if response:
                soup = self.parse_html(response.text)
                
                # Find all links that look like product pages
                all_links = soup.find_all('a', href=True)
                
                for link in all_links:
                    href = link.get('href', '')
                    
                    # Filter for product pages (based on actual site structure)
                    if any(keyword in href.lower() for keyword in ['fotovoltaicky-panel', 'menic', 'baterie', 'invertor']):
                        # Make absolute URL
                        if href.startswith('/'):
                            href = self.base_url + href
                        elif not href.startswith('http'):
                            href = self.base_url + '/' + href
                        
                        # Avoid duplicates
                        if href not in product_urls and self.base_url in href:
                            product_urls.append(href)
        
        self.logger.info(f"Found {len(product_urls)} product URLs from categories")
        return product_urls
    
    def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape individual product page.
        
        Extracts:
        - product_name
        - sku
        - category
        - price
        - availability
        - description
        - product_image
        - product_url
        """
        response = self.make_request(url, verify=False)  # Disable SSL verification
        if not response:
            return None
        
        try:
            soup = self.parse_html(response.text)
            
            # Extract product name (try multiple selectors)
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
                'div.sku'
            ])
            
            # Extract category
            category = self._extract_text(soup, [
                'span.category',
                'a.breadcrumb-item:last-child',
                '[itemprop="category"]',
                'nav.breadcrumb a:last-child'
            ])
            
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
                'div.popis'
            ])
            # Limit description length
            if description and len(description) > 500:
                description = description[:497] + "..."
            
            # Extract image
            product_image = self._extract_image(soup, [
                'img.product-image',
                '[itemprop="image"]',
                'img.main-image',
                'div.product-image img'
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
            self.logger.error(f"Error parsing {url}: {e}", exc_info=True)
            return None
    
    def _extract_text(self, soup, selectors: List[str], default: str = "") -> str:
        """Try multiple selectors and return first match."""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.text.strip()
        return default
    
    def _extract_image(self, soup, selectors: List[str]) -> str:
        """Extract image URL from multiple possible selectors."""
        for selector in selectors:
            img = soup.select_one(selector)
            if img:
                # Try different image attributes
                for attr in ['src', 'data-src', 'data-lazy-src']:
                    if attr in img.attrs:
                        url = img[attr]
                        # Make absolute URL if needed
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
        
        # Remove currency symbols and extra text
        # Keep numbers, decimal points, commas
        price = re.sub(r'[^\d,.]', '', price_str)
        
        return price.strip()


def main():
    """Main execution."""
    scraper = AkusolarScraper()
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
