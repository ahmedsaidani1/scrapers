"""
ST-Shop24 Scraper
Website: https://st-shop24.de
Platform: Magento
"""
import sys
import re
from typing import List, Dict, Optional, Any
from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS, SCRAPER_CONFIGS


SCRAPER_NAME = "st_shop24"


class StShop24Scraper(BaseScraper):
    """
    Scraper for ST-Shop24 (Magento platform).
    Extracts: manufacturer, category, name, title, article_number, 
              price_net, price_gross, ean, product_image, product_url
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        # Get website-specific config
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://st-shop24.de")
        self.sitemap_url = self.config.get("sitemap_url", "https://st-shop24.de/sitemap.xml")
        
        self.logger.info(f"Initialized scraper for {self.base_url}")
    
    def get_product_urls(self, max_categories: int = 50) -> List[str]:
        """
        Get list of product URLs by scraping category pages.
        Magento sites don't have products in sitemap, only categories.
        
        Args:
            max_categories: Maximum number of categories to scrape (default: 50)
        """
        product_urls = []
        
        try:
            # Get category URLs from sitemap
            self.logger.info("Fetching category URLs from sitemap...")
            response = self.make_request(self.sitemap_url)
            
            if not response:
                self.logger.error("Failed to fetch sitemap")
                return product_urls
            
            soup = self.parse_html(response.text)
            locs = soup.find_all('loc')
            
            # Filter for category pages (not too deep, has .html)
            category_urls = []
            for loc in locs:
                url = loc.text.strip()
                # Categories typically have 3-5 slashes and end with .html
                if url.endswith('.html') and 3 <= url.count('/') <= 5:
                    category_urls.append(url)
            
            # Limit to first N categories
            category_urls = category_urls[:max_categories]
            
            self.logger.info(f"Scraping first {len(category_urls)} categories")
            
            # Scrape products from each category
            for i, category_url in enumerate(category_urls, 1):
                self.logger.info(f"Scraping category {i}/{len(category_urls)}: {category_url}")
                
                try:
                    cat_response = self.make_request(category_url)
                    if not cat_response:
                        continue
                    
                    cat_soup = self.parse_html(cat_response.text)
                    
                    # Find product items (Magento uses .product-item class)
                    product_items = cat_soup.select('.product-item')
                    
                    for item in product_items:
                        link = item.select_one('a')
                        if link and link.get('href'):
                            product_url = link.get('href')
                            
                            # Make absolute URL
                            if product_url.startswith('/'):
                                product_url = self.base_url + product_url
                            elif not product_url.startswith('http'):
                                product_url = self.base_url + '/' + product_url
                            
                            # Avoid duplicates
                            if product_url not in product_urls:
                                product_urls.append(product_url)
                    
                    self.logger.info(f"  Found {len(product_items)} products (total: {len(product_urls)})")
                    
                except Exception as e:
                    self.logger.error(f"Error processing category {category_url}: {e}")
                    continue
            
            self.logger.info(f"Total product URLs found: {len(product_urls)}")
            
        except Exception as e:
            self.logger.error(f"Error getting product URLs: {e}", exc_info=True)
        
        return product_urls
    
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
                'div.product-name h1',
                'h1[itemprop="name"]',
                'h1'
            ])
            
            title = product_name
            name = product_name
            
            # Extract manufacturer/brand
            manufacturer = self._extract_text(soup, [
                'span[itemprop="brand"]',
                'div.product-brand',
                'a.brand-link',
                'meta[itemprop="brand"]'
            ])
            
            # Try meta tag for brand
            if not manufacturer:
                brand_meta = soup.select_one('meta[itemprop="brand"]')
                if brand_meta:
                    manufacturer = brand_meta.get('content', '')
            
            # Extract article number/SKU
            # For st-shop24, the article number is typically at the end of the product title
            # Example: "Grundfos Kit Gleitringdichtung für CRT2/4 - AUUV - 96513599"
            article_number = ""
            
            if product_name:
                # Try to extract article number from product name (usually at the end)
                # Look for patterns like: 8-digit numbers, alphanumeric codes
                import re
                
                # Try 8-digit number (most common)
                match = re.search(r'\b(\d{8})\b', product_name)
                if match:
                    article_number = match.group(1)
                else:
                    # Try alphanumeric code at the end (e.g., "ABC-123", "XYZ123")
                    match = re.search(r'[-\s]([A-Z0-9]{3,}[-]?[A-Z0-9]+)$', product_name)
                    if match:
                        article_number = match.group(1)
            
            # If not found in title, try standard SKU selectors
            if not article_number:
                sku_selectors = [
                    'span[itemprop="sku"]',
                    'div.sku span',
                    'span.sku',
                    'meta[itemprop="sku"]'
                ]
                
                for selector in sku_selectors:
                    if selector.startswith('meta'):
                        sku_meta = soup.select_one(selector)
                        if sku_meta and sku_meta.get('content'):
                            article_number = sku_meta.get('content', '').strip()
                            break
                    else:
                        sku_elem = soup.select_one(selector)
                        if sku_elem:
                            article_number = sku_elem.text.strip()
                            break
            
            # Extract category from breadcrumbs
            category = self._extract_text(soup, [
                'div.breadcrumbs li:nth-last-child(2) a',
                'nav.breadcrumbs li:nth-last-child(2) a',
                'span[itemprop="category"]'
            ])
            
            # Extract price (gross - with VAT) - Magento structure
            price_gross_raw = self._extract_text(soup, [
                'span.price',
                'div.price-box span.price',
                'span[data-price-type="finalPrice"]',
                'meta[itemprop="price"]'
            ])
            
            # Try meta tag
            if not price_gross_raw:
                price_meta = soup.select_one('meta[itemprop="price"]')
                if price_meta:
                    price_gross_raw = price_meta.get('content', '')
            
            price_gross = self._clean_price(price_gross_raw)
            
            # Calculate net price (German VAT is 19%)
            price_net = ""
            if price_gross:
                try:
                    gross_float = float(price_gross.replace(',', '.'))
                    net_float = gross_float / 1.19
                    price_net = f"{net_float:.2f}".replace('.', ',')
                except:
                    price_net = ""
            
            # Extract EAN
            ean = self._extract_text(soup, [
                'span[itemprop="gtin13"]',
                'div.ean span',
                'span.ean',
                'meta[itemprop="gtin13"]'
            ])
            
            # Try meta tag
            if not ean:
                ean_meta = soup.select_one('meta[itemprop="gtin13"]')
                if ean_meta:
                    ean = ean_meta.get('content', '')
            
            # Extract image (Magento structure)
            product_image = self._extract_image(soup, [
                'div.gallery-placeholder img',
                'img.product-image-photo',
                'div.product-image img',
                'img[itemprop="image"]',
                'meta[property="og:image"]'
            ])
            
            # Validate minimum required data
            if not product_name:
                self.logger.warning(f"No product name found for {url}")
                return None
            
            product_data = {
                'manufacturer': manufacturer,
                'category': category,
                'name': name,
                'title': title,
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
                    for attr in ['src', 'data-src', 'data-lazy-src', 'srcset']:
                        if attr in img.attrs:
                            url = img[attr]
                            if attr == 'srcset':
                                url = url.split(',')[0].split()[0]
                            if url.startswith('//'):
                                url = 'https:' + url
                            elif url.startswith('/'):
                                url = self.base_url + url
                            return url
        return ""
    
    def _clean_price(self, price_str: str) -> str:
        """Clean and standardize price format (German format: 1.234,56)."""
        if not price_str:
            return ""
        # Remove currency symbols and extra text, keep numbers, dots, commas
        price = re.sub(r'[^\d,.]', '', price_str)
        return price.strip()


def main():
    """Main execution."""
    scraper = StShop24Scraper()
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
