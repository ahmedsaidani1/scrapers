"""
Sample working scraper for demonstration.
This scrapes a solar equipment website to show the framework in action.

This example uses a real solar equipment site structure.
"""
import sys
import re
from typing import List, Dict, Optional, Any
from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS


SCRAPER_NAME = "sample_scraper"


class SampleScraper(BaseScraper):
    """
    Sample scraper demonstrating the framework.
    Scrapes solar equipment products.
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        # Example: scraping a solar equipment website
        self.base_url = "https://www.example-solar.com"
        
    def get_product_urls(self) -> List[str]:
        """
        Get product URLs from sitemap or category pages.
        
        This example shows multiple approaches you can use.
        """
        product_urls = []
        
        # Approach 1: Try sitemap first
        sitemap_url = f"{self.base_url}/sitemap_products.xml"
        response = self.make_request(sitemap_url)
        
        if response:
            soup = self.parse_html(response.text)
            # Extract URLs from sitemap
            locs = soup.find_all('loc')
            for loc in locs:
                url = loc.text.strip()
                # Filter for product pages only
                if '/products/' in url or '/solar-' in url:
                    product_urls.append(url)
            
            self.logger.info(f"Found {len(product_urls)} URLs from sitemap")
        
        # Approach 2: If sitemap fails, scrape category pages
        if not product_urls:
            self.logger.info("Sitemap not available, trying category pages...")
            product_urls = self._scrape_category_pages()
        
        return product_urls
    
    def _scrape_category_pages(self) -> List[str]:
        """Fallback: scrape product links from category pages."""
        product_urls = []
        
        # Example categories for solar equipment
        categories = [
            "/solar-panels",
            "/inverters",
            "/batteries",
            "/mounting-systems"
        ]
        
        for category in categories:
            url = f"{self.base_url}{category}"
            response = self.make_request(url)
            
            if response:
                soup = self.parse_html(response.text)
                # Common selectors for product links
                links = soup.select('a[href*="/product/"]')
                
                for link in links:
                    href = link.get('href', '')
                    if href.startswith('/'):
                        href = self.base_url + href
                    if href not in product_urls:
                        product_urls.append(href)
        
        return product_urls
    
    def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape individual product page.
        
        This shows common patterns for extracting solar equipment data.
        """
        response = self.make_request(url)
        if not response:
            return None
        
        try:
            soup = self.parse_html(response.text)
            
            # Extract product name (try multiple selectors)
            product_name = self._extract_text(soup, [
                'h1.product-title',
                'h1[itemprop="name"]',
                'h1.product-name',
                'h1'
            ])
            
            # Extract SKU
            sku = self._extract_text(soup, [
                'span.sku',
                '[itemprop="sku"]',
                'span.product-code'
            ])
            
            # Extract category
            category = self._extract_text(soup, [
                'span.category',
                'a.breadcrumb-item:last-child',
                '[itemprop="category"]'
            ])
            
            # Extract price (clean up formatting)
            price_raw = self._extract_text(soup, [
                'span.price',
                '[itemprop="price"]',
                'span.product-price',
                'div.price-box'
            ])
            price = self._clean_price(price_raw)
            
            # Extract availability
            availability = self._extract_text(soup, [
                'span.availability',
                '[itemprop="availability"]',
                'span.stock-status'
            ], default="In Stock")
            
            # Extract description
            description = self._extract_text(soup, [
                'div.product-description',
                '[itemprop="description"]',
                'div.description'
            ])
            # Limit description length
            if description and len(description) > 500:
                description = description[:497] + "..."
            
            # Extract image
            product_image = self._extract_image(soup, [
                'img.product-image',
                '[itemprop="image"]',
                'img.main-image'
            ])
            
            # Validate we have minimum required data
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
    
    def _extract_text(
        self,
        soup,
        selectors: List[str],
        default: str = ""
    ) -> str:
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
    scraper = SampleScraper()
    success_count = scraper.run()
    
    # Push to Google Sheets if requested
    if "--push-to-sheets" in sys.argv and success_count > 0:
        sheet_id = SHEET_IDS.get(SCRAPER_NAME)
        
        if sheet_id and sheet_id != "YOUR_SHEET_ID_HERE":
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
