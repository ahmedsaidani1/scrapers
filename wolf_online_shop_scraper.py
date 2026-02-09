"""
Wolf-Online-Shop Scraper
Website: https://www.wolf-online-shop.de
Platform: Custom (Heating/HVAC parts shop) - Cloudflare protected
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


SCRAPER_NAME = "wolf_online_shop"


class WolfOnlineShopScraper(BaseScraper):
    """
    Scraper for Wolf-Online-Shop.de (heating/HVAC parts) using cloudscraper.
    Extracts: manufacturer, category, name, title, article_number, 
              price_net, price_gross, ean, product_image, product_url
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://www.wolf-online-shop.de")
        
        # Initialize cloudscraper session
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
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
        Get product URLs by crawling categories.
        The site has category pages with products that need to be discovered.
        """
        product_urls = []
        category_urls = set()
        
        try:
            self.logger.info("Discovering categories and products...")
            response = self.make_request(self.base_url)
            
            if not response:
                self.logger.error("Failed to fetch homepage")
                return product_urls
            
            soup = self.parse_html(response.text)
            links = soup.find_all('a', href=True)
            
            # First pass: collect all category URLs (with :::)
            for link in links:
                href = link.get('href')
                if not href:
                    continue
                
                # Make absolute URL
                if href.startswith('/'):
                    url = self.base_url + href
                elif not href.startswith('http'):
                    url = self.base_url + '/' + href
                else:
                    url = href
                
                # Category pages have ::: pattern
                if ':::' in url and '.html' in url:
                    category_urls.add(url)
                # Product pages have :: pattern
                elif self._is_product_url(url):
                    if url not in product_urls:
                        product_urls.append(url)
            
            self.logger.info(f"Found {len(product_urls)} products on homepage")
            self.logger.info(f"Found {len(category_urls)} category pages to explore")
            
            # Now crawl each category page to find products
            for i, cat_url in enumerate(sorted(category_urls), 1):
                if max_urls and len(product_urls) >= max_urls:
                    break
                
                self.logger.info(f"[{i}/{len(category_urls)}] Crawling category: {cat_url}")
                
                try:
                    cat_response = self.make_request(cat_url)
                    if not cat_response:
                        continue
                    
                    cat_soup = self.parse_html(cat_response.text)
                    cat_links = cat_soup.find_all('a', href=True)
                    
                    products_in_category = 0
                    for link in cat_links:
                        href = link.get('href')
                        if not href:
                            continue
                        
                        # Make absolute URL
                        if href.startswith('/'):
                            url = self.base_url + href
                        elif not href.startswith('http'):
                            url = self.base_url + '/' + href
                        else:
                            url = href
                        
                        # Check if it's a product page
                        if self._is_product_url(url) and url not in product_urls:
                            product_urls.append(url)
                            products_in_category += 1
                            
                            if max_urls and len(product_urls) >= max_urls:
                                break
                    
                    self.logger.info(f"  Found {products_in_category} products (total: {len(product_urls)})")
                    
                    # Small delay between category requests
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logger.error(f"Error crawling category {cat_url}: {e}")
                    continue
            
            self.logger.info(f"Total product URLs found: {len(product_urls)}")
            
        except Exception as e:
            self.logger.error(f"Error getting product URLs: {e}", exc_info=True)
        
        return product_urls[:max_urls] if max_urls else product_urls
    
    def _is_product_url(self, url: str) -> bool:
        """Determine if URL is a product page."""
        # Skip info pages
        skip_patterns = [
            '/impressum', '/datenschutz', '/agb', '/kontakt',
            '/ueber-uns', '/rechtliches', '/versand', '/zahlung',
            '/widerrufsrecht', '/lieferung', '/service',
            'products_new.php', 'index.php', 'login.php',
            'shopping_cart.php', 'checkout', 'account',
            'popup_content.php', 'create_account', 'password'
        ]
        
        for pattern in skip_patterns:
            if pattern in url.lower():
                return False
        
        # Skip homepage
        if url == self.base_url or url == f"{self.base_url}/":
            return False
        
        # Product pages have pattern: /Product-Name::ID.html (double colon)
        # Category pages have pattern: /Category:::ID.html (triple colon) - skip these
        if ':::' in url:
            return False
        
        if '::' in url and '.html' in url:
            return True
        
        return False
    
    def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape individual product page."""
        response = self.make_request(url)
        if not response:
            return None
        
        try:
            soup = self.parse_html(response.text)
            
            # Try to extract from JSON-LD structured data first (most reliable)
            json_ld = soup.find('script', {'type': 'application/ld+json'})
            if json_ld:
                try:
                    import json
                    data = json.loads(json_ld.string)
                    
                    # Check if it's a Product schema
                    if isinstance(data, dict) and data.get('@type') == 'Product':
                        import html
                        product_name = html.unescape(data.get('name', ''))
                        manufacturer = data.get('brand', {}).get('name', '') if isinstance(data.get('brand'), dict) else ''
                        article_number = data.get('mpn', '') or data.get('sku', '')
                        ean = data.get('gtin8', '') or data.get('gtin13', '')
                        
                        # Get price from offers
                        offers = data.get('offers', {})
                        price_gross_raw = str(offers.get('price', '')) if isinstance(offers, dict) else ''
                        price_gross = price_gross_raw.replace('.', ',') if price_gross_raw else ''
                        
                        # Get image
                        images = data.get('image', [])
                        product_image = images[0] if isinstance(images, list) and images else ''
                        
                        self.logger.info(f"Extracted from JSON-LD: {product_name}, {manufacturer}")
                except Exception as e:
                    self.logger.warning(f"Failed to parse JSON-LD: {e}")
                    manufacturer = ''
                    article_number = ''
                    ean = ''
                    price_gross = ''
                    product_image = ''
                    product_name = ''
            else:
                manufacturer = ''
                article_number = ''
                ean = ''
                price_gross = ''
                product_image = ''
                product_name = ''
            
            # Fallback to HTML extraction if JSON-LD didn't work
            if not product_name:
                product_name = self._extract_text(soup, [
                    'h1.product-name',
                    'h1.product-title',
                    'h1[itemprop="name"]',
                    'div.product-name',
                    'h1'
                ])
            
            if not product_name:
                self.logger.warning(f"No product name found for {url}")
                return None
            
            # Extract manufacturer from HTML if not in JSON-LD
            if not manufacturer:
                # Look for "Hersteller:" label
                manufacturer_elem = soup.find('strong', string=lambda x: x and 'Hersteller' in x)
                if manufacturer_elem and manufacturer_elem.parent:
                    # Get the next span or text
                    span = manufacturer_elem.parent.find('span')
                    if span:
                        manufacturer = span.get_text(strip=True)
                
                # Fallback to other selectors
                if not manufacturer:
                    manufacturer = self._extract_text(soup, [
                        'span.manufacturer',
                        'a.brand',
                        'span[itemprop="brand"]',
                        'div.product-manufacturer',
                        'meta[itemprop="brand"]'
                    ])
            
            # Extract category
            category = self._extract_text(soup, [
                'nav.breadcrumb li:nth-last-child(2) a',
                'ul.breadcrumbs li:nth-last-child(2) a',
                'div.breadcrumbs a:last-of-type',
                'span[itemprop="category"]'
            ])
            
            # Extract article number from HTML if not in JSON-LD
            if not article_number:
                # Look for "HAN:" label
                han_elem = soup.find('strong', string=lambda x: x and 'HAN:' in x)
                if han_elem and han_elem.parent:
                    # Get text after the strong tag
                    text = han_elem.parent.get_text()
                    if 'HAN:' in text:
                        article_number = text.split('HAN:')[1].strip().split()[0]
                
                # Fallback
                if not article_number:
                    article_number = self._extract_text(soup, [
                        'span.sku',
                        'span[itemprop="sku"]',
                        'div.article-number',
                        'div.product-sku',
                        'meta[itemprop="sku"]'
                    ])
            
            # Extract price from HTML if not in JSON-LD
            if not price_gross:
                price_gross_raw = self._extract_text(soup, [
                    'span.value_price',
                    'span.price',
                    'span[itemprop="price"]',
                    'div.product-price',
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
            
            # Extract EAN from HTML if not in JSON-LD
            if not ean:
                ean = self._extract_text(soup, [
                    'span.ean',
                    'span[itemprop="gtin13"]',
                    'div.product-ean',
                    'meta[itemprop="gtin13"]'
                ])
            
            # Extract product image from HTML if not in JSON-LD
            if not product_image:
                product_image = self._extract_image(soup, [
                    'img.product-image',
                    'img[itemprop="image"]',
                    'div.product-gallery img',
                    'meta[property="og:image"]',
                    'img.main-image'
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
        # Remove currency symbols and extra text
        price = re.sub(r'[^\d,.]', '', price_str)
        return price.strip()


def main():
    """Main execution."""
    scraper = WolfOnlineShopScraper()
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
