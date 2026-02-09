"""
Wolfonlineshop (Heat-Store) Scraper
Website: https://www.heat-store.de (redirects from wolfonlineshop.de)
Platform: Shopware 6
"""
import sys
import re
from typing import List, Dict, Optional, Any
from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS, SCRAPER_CONFIGS


SCRAPER_NAME = "wolfonlineshop"


class WolfonlineshopScraper(BaseScraper):
    """
    Scraper for Wolfonlineshop/Heat-Store (Shopware 6 platform).
    Extracts: manufacturer, category, name, title, article_number, 
              price_net, price_gross, ean, product_image, product_url
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        # Get website-specific config
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://www.heat-store.de")
        
        # Known category URLs to scrape
        self.category_urls = [
            f"{self.base_url}/heizung/heizkoerper/badheizkoerper//",
            f"{self.base_url}/heizung/heizkoerper/paneelheizkoerper//",
            f"{self.base_url}/heizung/gas-heizung//",
            f"{self.base_url}/heizung/oel-heizung/oelkessel//",
            f"{self.base_url}/heizung/holz-heizung/holzvergaser/holzkessel//",
            f"{self.base_url}/elektro//",
            f"{self.base_url}/kamin//",
        ]
        
        self.logger.info(f"Initialized scraper for {self.base_url}")
    
    def get_product_urls(self) -> List[str]:
        """
        Get list of product URLs by scraping category pages.
        Heat-Store doesn't have product URLs in sitemap, so we scrape categories.
        """
        product_urls = []
        
        try:
            self.logger.info(f"Scraping {len(self.category_urls)} category pages...")
            
            for i, category_url in enumerate(self.category_urls, 1):
                self.logger.info(f"Processing category {i}/{len(self.category_urls)}: {category_url}")
                
                try:
                    response = self.make_request(category_url)
                    if not response:
                        continue
                    
                    soup = self.parse_html(response.text)
                    
                    # Find product links (they have 'product' in class name)
                    product_links = soup.find_all('a', class_=lambda x: x and 'product' in str(x).lower())
                    
                    for link in product_links:
                        href = link.get('href')
                        if href and href.endswith('.html'):
                            # Make absolute URL
                            if href.startswith('/'):
                                href = self.base_url + href
                            elif not href.startswith('http'):
                                href = self.base_url + '/' + href
                            
                            # Avoid duplicates
                            if href not in product_urls:
                                product_urls.append(href)
                    
                    self.logger.info(f"Found {len(product_links)} products in this category")
                    
                except Exception as e:
                    self.logger.error(f"Error processing category {category_url}: {e}")
                    continue
            
            self.logger.info(f"Total product URLs found: {len(product_urls)}")
            
        except Exception as e:
            self.logger.error(f"Error getting product URLs: {e}", exc_info=True)
        
        return product_urls
    
    def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape individual product page.
        """
        response = self.make_request(url)
        if not response:
            return None
        
        try:
            soup = self.parse_html(response.text)
            
            # Extract product name/title
            product_name = self._extract_text(soup, [
                'h1.product-detail-name',
                'h1[itemprop="name"]',
                'h1.product-title',
                'h1'
            ])
            
            title = product_name
            name = product_name
            
            # Extract manufacturer/brand
            manufacturer = self._extract_text(soup, [
                'span[itemprop="brand"]',
                'a.product-detail-manufacturer-link',
                'div.product-detail-manufacturer',
                'meta[itemprop="brand"]'
            ])
            
            # Try meta tag for brand
            if not manufacturer:
                brand_meta = soup.select_one('meta[itemprop="brand"]')
                if brand_meta:
                    manufacturer = brand_meta.get('content', '')
            
            # Extract article number/SKU
            article_number = self._extract_text(soup, [
                'span.product-detail-ordernumber',
                'span[itemprop="sku"]',
                'div.product-number',
                'span.sku'
            ])
            
            # Try meta tag for SKU
            if not article_number:
                sku_meta = soup.select_one('meta[itemprop="sku"]')
                if sku_meta:
                    article_number = sku_meta.get('content', '')
            
            # Extract category from breadcrumbs
            category = self._extract_text(soup, [
                'nav.breadcrumb li:nth-last-child(2) a',
                'span[itemprop="category"]',
                'div.product-detail-category'
            ])
            
            # Extract price (gross - with VAT)
            price_gross_raw = self._extract_text(soup, [
                'meta[itemprop="price"]',
                'span.product-detail-price',
                'div.product-price'
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
                'span.product-detail-ean',
                'meta[itemprop="gtin13"]'
            ])
            
            # Try meta tag
            if not ean:
                ean_meta = soup.select_one('meta[itemprop="gtin13"]')
                if ean_meta:
                    ean = ean_meta.get('content', '')
            
            # Extract image
            product_image = self._extract_image(soup, [
                'img.product-detail-image',
                'img[itemprop="image"]',
                'div.gallery-slider-item img',
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
    scraper = WolfonlineshopScraper()
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
