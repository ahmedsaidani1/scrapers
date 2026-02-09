"""
TEMPLATE for creating new scrapers.

INSTRUCTIONS:
1. Copy this file and rename it (e.g., priwatt_scraper.py)
2. Update SCRAPER_NAME constant
3. Implement get_product_urls() method
4. Implement scrape_product() method
5. Add configuration to config.py SCRAPER_CONFIGS
6. Add Google Sheet ID to config.py SHEET_IDS
7. Test locally before deploying

EXAMPLE USAGE:
    python scraper_template.py
    
    # Or with Google Sheets push:
    python scraper_template.py --push-to-sheets
"""
import sys
from typing import List, Dict, Optional, Any
from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS, SCRAPER_CONFIGS


# ============================================================================
# CONFIGURATION - CUSTOMIZE THIS SECTION
# ============================================================================
SCRAPER_NAME = "sample_scraper"  # Change this to your scraper name


class TemplateScraper(BaseScraper):
    """
    Template scraper - customize for your specific website.
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        # Get website-specific config
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "")
        
        self.logger.info(f"Initialized scraper for {self.base_url}")
    
    def get_product_urls(self) -> List[str]:
        """
        Get list of product URLs to scrape.
        
        CUSTOMIZE THIS METHOD based on the website structure:
        
        Option 1: Parse sitemap.xml
        Option 2: Scrape category pages
        Option 3: Use API endpoints
        
        Returns:
            List of product URLs
        """
        product_urls = []
        
        # EXAMPLE: Parse sitemap.xml
        # sitemap_url = self.config.get("sitemap_url")
        # response = self.make_request(sitemap_url)
        # if response:
        #     soup = self.parse_html(response.text)
        #     urls = soup.find_all('loc')
        #     product_urls = [url.text for url in urls if '/product/' in url.text]
        
        # EXAMPLE: Scrape category page
        # category_url = f"{self.base_url}/products"
        # response = self.make_request(category_url)
        # if response:
        #     soup = self.parse_html(response.text)
        #     links = soup.select('a.product-link')
        #     product_urls = [self.base_url + link['href'] for link in links]
        
        # TODO: Implement your logic here
        self.logger.warning("get_product_urls() not implemented yet")
        
        return product_urls
    
    def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single product page.
        
        CUSTOMIZE THIS METHOD to extract data from your specific website.
        
        Args:
            url: Product page URL
        
        Returns:
            Dictionary with product data or None if failed
        """
        response = self.make_request(url)
        if not response:
            return None
        
        try:
            soup = self.parse_html(response.text)
            
            # TODO: Customize these selectors for your website
            # Use browser DevTools to find the right CSS selectors
            
            # EXAMPLE selectors (replace with actual ones):
            product_name = soup.select_one('h1.product-title')
            product_name = product_name.text.strip() if product_name else ""
            
            sku = soup.select_one('span.sku')
            sku = sku.text.strip() if sku else ""
            
            category = soup.select_one('span.category')
            category = category.text.strip() if category else ""
            
            price = soup.select_one('span.price')
            price = price.text.strip() if price else ""
            
            availability = soup.select_one('span.availability')
            availability = availability.text.strip() if availability else "In Stock"
            
            description = soup.select_one('div.description')
            description = description.text.strip() if description else ""
            
            image = soup.select_one('img.product-image')
            product_image = image['src'] if image and 'src' in image.attrs else ""
            
            # Build product data dictionary
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
            self.logger.error(f"Error parsing product page {url}: {e}")
            return None


# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    """Main execution function."""
    # Initialize and run scraper
    scraper = TemplateScraper()
    success_count = scraper.run()
    
    # Push to Google Sheets if requested
    if "--push-to-sheets" in sys.argv and success_count > 0:
        sheet_id = SHEET_IDS.get(SCRAPER_NAME)
        
        if sheet_id and sheet_id != "YOUR_SHEET_ID_HERE":
            print(f"\nPushing data to Google Sheets...")
            output_file = scraper.get_output_file()
            
            if push_data(sheet_id, output_file):
                print("✓ Successfully pushed to Google Sheets")
            else:
                print("✗ Failed to push to Google Sheets")
        else:
            print(f"\n⚠ No Google Sheet ID configured for {SCRAPER_NAME}")
            print(f"Add it to config.py SHEET_IDS dictionary")
    
    print(f"\n{'='*60}")
    print(f"Scraping completed: {success_count} products")
    print(f"Output file: {scraper.get_output_file()}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
