"""
Erneuerbar24 Scraper
Website: https://erneuerbar24.de
"""
import sys
import re
from typing import List, Dict, Optional, Any
from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS, SCRAPER_CONFIGS


SCRAPER_NAME = "erneuerbar"


class ErneuerbarScraper(BaseScraper):
    """
    Scraper for Erneuerbar24 solar equipment website (Shopify store).
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        # Get website-specific config
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://erneuerbar24.de")
        
        self.logger.info(f"Initialized scraper for {self.base_url}")
    
    def get_product_urls(self) -> List[str]:
        """
        Get list of product URLs to scrape.
        
        Strategy:
        1. Try sitemap.xml first
        2. If that fails, scrape category pages
        """
        product_urls = []
        
        # Try sitemap first
        self.logger.info("Attempting to fetch product URLs from sitemap...")
        sitemap_url = f"{self.base_url}/sitemap.xml"
        response = self.make_request(sitemap_url)
        
        if response:
            soup = self.parse_html(response.text)
            locs = soup.find_all('loc')
            
            for loc in locs:
                url = loc.text.strip()
                # Filter for product pages (Shopify uses /products/)
                if '/products/' in url.lower():
                    product_urls.append(url)
            
            self.logger.info(f"Found {len(product_urls)} product URLs from sitemap")
        
        # If sitemap didn't work, try category pages
        if not product_urls:
            self.logger.info("Sitemap didn't work, trying category pages...")
            product_urls = self._scrape_category_pages()
        
        return product_urls
    
    def _scrape_category_pages(self) -> List[str]:
        """Fallback: scrape product links from category/listing pages."""
        product_urls = []
        
        # Common category URLs for Erneuerbar24 (Shopify collections)
        category_urls = [
            f"{self.base_url}/collections/photovoltaik-module",
            f"{self.base_url}/collections/photovoltaik-komplettset",
            f"{self.base_url}/collections/pv-sets-speicher-wechselrichter",
            f"{self.base_url}/collections/photovoltaik-wechselrichter",
            f"{self.base_url}/collections/photovoltaik-batterien-und-speicher",
        ]
        
        for category_url in category_urls:
            self.logger.info(f"Scraping category: {category_url}")
            response = self.make_request(category_url)
            
            if response:
                soup = self.parse_html(response.text)
                
                # Find all links
                all_links = soup.find_all('a', href=True)
                
                for link in all_links:
                    href = link.get('href', '')
                    
                    # Filter for product pages (Shopify uses /products/)
                    if '/products/' in href.lower():
                        # Make absolute URL
                        if href.startswith('/'):
                            href = self.base_url + href
                        elif not href.startswith('http'):
                            href = self.base_url + '/' + href
                        
                        # Avoid duplicates
                        if href not in product_urls:
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
                'h1.title',
                'h1.product-detail-name',
                'h1'
            ])
            
            # Extract SKU (Priwatt uses SW codes)
            sku = self._extract_text(soup, [
                'span.sku',
                '[itemprop="sku"]',
                'span.product-code',
                'div.product-detail-ordernumber',
                'span.product-number'
            ])
            
            # If no SKU found, try to extract from URL
            if not sku and '/SW' in url:
                sku_match = re.search(r'SW\d+', url)
                if sku_match:
                    sku = sku_match.group()
            
            # Extract category
            category = self._extract_text(soup, [
                'span.category',
                'a.breadcrumb-item:last-child',
                '[itemprop="category"]',
                'nav.breadcrumb a:last-child',
                'span.product-detail-category'
            ])
            
            # If no category, infer from URL
            if not category:
                if 'balkonkraftwerk-800' in url.lower():
                    category = "Balkonkraftwerk 800W"
                elif 'balkonkraftwerk-speicher' in url.lower():
                    category = "Balkonkraftwerk mit Speicher"
                elif 'balkonkraftwerk' in url.lower():
                    category = "Balkonkraftwerk"
            
            # Extract price
            price_raw = self._extract_text(soup, [
                'span.price',
                '[itemprop="price"]',
                'span.product-price',
                'div.price',
                'span.product-detail-price',
                'meta[itemprop="price"]'
            ])
            
            # Also try meta tag
            if not price_raw:
                price_meta = soup.select_one('meta[itemprop="price"]')
                if price_meta and price_meta.get('content'):
                    price_raw = price_meta.get('content')
            
            price = self._clean_price(price_raw)
            
            # Extract availability
            availability = self._extract_text(soup, [
                'span.availability',
                '[itemprop="availability"]',
                'span.stock-status',
                'div.product-detail-delivery-information',
                'span.delivery-status'
            ], default="In Stock")
            
            # Extract description
            description = self._extract_text(soup, [
                'div.product-description',
                '[itemprop="description"]',
                'div.description',
                'div.product-detail-description',
                'meta[name="description"]'
            ])
            
            # Try meta description if no description found
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
                'img.product-detail-image',
                'meta[property="og:image"]'
            ])
            
            # Try og:image meta tag
            if not product_image:
                og_image = soup.select_one('meta[property="og:image"]')
                if og_image and og_image.get('content'):
                    product_image = og_image.get('content')
            
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
                text = element.text.strip() if hasattr(element, 'text') else element.get('content', '')
                if text:
                    return text
        return default
    
    def _extract_image(self, soup, selectors: List[str]) -> str:
        """Extract image URL from multiple possible selectors."""
        for selector in selectors:
            if selector.startswith('meta'):
                # Handle meta tags
                meta = soup.select_one(selector)
                if meta and meta.get('content'):
                    url = meta.get('content')
                    if url.startswith('//'):
                        url = 'https:' + url
                    elif url.startswith('/'):
                        url = self.base_url + url
                    return url
            else:
                # Handle img tags
                img = soup.select_one(selector)
                if img:
                    # Try different image attributes
                    for attr in ['src', 'data-src', 'data-lazy-src', 'srcset']:
                        if attr in img.attrs:
                            url = img[attr]
                            # Handle srcset (take first URL)
                            if attr == 'srcset':
                                url = url.split(',')[0].split()[0]
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
    scraper = ErneuerbarScraper()
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
