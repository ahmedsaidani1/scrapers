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
        
        # All LEAF categories (most specific, no children)
        # Removed parent categories to avoid duplicates
        # This ensures we get all unique products without overlap
        self.all_categories = [
            # Elektro (leaf category)
            f"{self.base_url}/elektro//",
            
            # Heizung leaf categories (removed parent "heizung")
            f"{self.base_url}/heizung/brennstoffzelle//",
            f"{self.base_url}/heizung/ersatzteile//",
            
            # Fussbodenheizung leaf categories (removed parent "fussbodenheizung")
            f"{self.base_url}/heizung/fussbodenheizung/duennschichtsystem//",
            f"{self.base_url}/heizung/fussbodenheizung/elektro-fussbodenheizung//",
            f"{self.base_url}/heizung/fussbodenheizung/noppensystem//",
            f"{self.base_url}/heizung/fussbodenheizung/rohr-zubehoer//",
            f"{self.base_url}/heizung/fussbodenheizung/tackersystem//",
            f"{self.base_url}/heizung/fussbodenheizung/trockenbausystem//",
            
            # Gas-heizung leaf categories (removed parent "gas-heizung")
            f"{self.base_url}/heizung/gas-heizung/gasbrenner//",
            f"{self.base_url}/heizung/gas-heizung/gaskessel//",
            f"{self.base_url}/heizung/gas-heizung/gastherme//",
            
            # Heizkoerper-zubehoer leaf categories (removed parent)
            f"{self.base_url}/heizung/heizkoerper-zubehoer/bad-vertikalheizkoerper//",
            f"{self.base_url}/heizung/heizkoerper-zubehoer/kompaktheizkoerper//",
            f"{self.base_url}/heizung/heizkoerper-zubehoer/ventilheizkoerper//",
            
            # Heizkoerper leaf categories (removed parent "heizkoerper")
            f"{self.base_url}/heizung/heizkoerper/austauschheizkoerper//",
            f"{self.base_url}/heizung/heizkoerper/badheizkoerper//",
            f"{self.base_url}/heizung/heizkoerper/designheizkoerper//",
            f"{self.base_url}/heizung/heizkoerper/elektroheizkoerper//",
            f"{self.base_url}/heizung/heizkoerper/kompaktheizkoerper//",
            f"{self.base_url}/heizung/heizkoerper/niedertemperaturheizkoerper//",
            f"{self.base_url}/heizung/heizkoerper/paneelheizkoerper//",
            f"{self.base_url}/heizung/heizkoerper/roehrenradiatoren//",
            f"{self.base_url}/heizung/heizkoerper/ventilheizkoerper//",
            f"{self.base_url}/heizung/heizkoerper/vertikalheizkoerper//",
            
            f"{self.base_url}/heizung/heizstaebe//",
            
            # Holz-heizung leaf categories (removed parent "holz-heizung")
            f"{self.base_url}/heizung/holz-heizung/hackschnitzel//",
            f"{self.base_url}/heizung/holz-heizung/holzvergaser/holzkessel-zubehoer//",
            f"{self.base_url}/heizung/holz-heizung/holzvergaser/holzkessel//",
            f"{self.base_url}/heizung/holz-heizung/pelletheizung//",
            
            f"{self.base_url}/heizung/hybridsysteme//",
            
            # Installation leaf categories (removed parent "installation")
            f"{self.base_url}/heizung/installation/abgassysteme-schornstein//",
            f"{self.base_url}/heizung/installation/armaturen//",
            f"{self.base_url}/heizung/installation/ausdehnungsgefaesse//",
            f"{self.base_url}/heizung/installation/befestigungstechnik//",
            f"{self.base_url}/heizung/installation/c-stahlrohr-fittinge//",
            f"{self.base_url}/heizung/installation/edelstahlrohr-fittinge//",
            f"{self.base_url}/heizung/installation/fuehler-sensoren-regler//",
            f"{self.base_url}/heizung/installation/isolierung//",
            f"{self.base_url}/heizung/installation/kondensatpumpen//",
            f"{self.base_url}/heizung/installation/kupferrohr-fittinge//",
            f"{self.base_url}/heizung/installation/verbundrohr//",
            f"{self.base_url}/heizung/installation/werkzeug//",
            
            # Oel-heizung leaf categories (removed parent "oel-heizung")
            f"{self.base_url}/heizung/oel-heizung/oelbrenner//",
            f"{self.base_url}/heizung/oel-heizung/oelkessel//",
            f"{self.base_url}/heizung/oel-heizung/oeltanks-zubehoer//",
            
            f"{self.base_url}/heizung/pumpen//",
            
            # Waermepumpen leaf categories (removed parent "waermepumpen")
            f"{self.base_url}/heizung/waermepumpen/wp-brauchwasser//",
            f"{self.base_url}/heizung/waermepumpen/wp-erdwaerme-sole//",
            f"{self.base_url}/heizung/waermepumpen/wp-luft-wasser//",
            f"{self.base_url}/heizung/waermepumpen/wp-split//",
            f"{self.base_url}/heizung/waermepumpen/wp-zubehoer//",
            
            f"{self.base_url}/heizung/wandheizung//",
            
            # Warmwasserspeicher leaf categories (removed parent)
            f"{self.base_url}/heizung/warmwasserspeicher/speicher-zubehoer//",
            f"{self.base_url}/heizung/warmwasserspeicher/speicher//",
            
            # Kamin (leaf category)
            f"{self.base_url}/kamin//",
        ]
        
        self.logger.info(f"Initialized scraper for {self.base_url}")
    
    def _parse_category_from_url(self, category_url: str) -> str:
        """
        Parse category name from category URL.
        Example: https://www.heat-store.de/heizung/gas-heizung/gastherme// -> Gastherme
        """
        # Remove base URL and trailing slashes
        path = category_url.replace(self.base_url, '').strip('/')
        
        # Split by / and get the last meaningful part
        parts = [p for p in path.split('/') if p]
        if parts:
            # Get last part and clean it up
            category = parts[-1].replace('-', ' ').title()
            return category
        return ""
    
    def get_product_urls(self, max_urls: int = None) -> List[str]:
        """
        Get list of product URLs by scraping all known categories with pagination.
        """
        product_urls = []
        seen = set()
        
        # Initialize category mapping
        self._product_category_map = {}
        
        try:
            self.logger.info(f"Scraping {len(self.all_categories)} categories...")
            
            # Scrape products from each category with pagination
            for i, category_url in enumerate(self.all_categories, 1):
                self.logger.info(f"[{i}/{len(self.all_categories)}] Scraping: {category_url}")
                
                # Scrape all pages in this category
                page = 1
                category_has_products = False
                
                while True:
                    # Shopware pagination format: ?p=1, ?p=2, etc.
                    if page == 1:
                        page_url = category_url
                    else:
                        separator = '&' if '?' in category_url else '?'
                        page_url = f"{category_url}{separator}p={page}"
                    
                    if page > 1:
                        self.logger.info(f"  Page {page}: {page_url}")
                    
                    response = self.make_request(page_url)
                    if not response:
                        self.logger.warning(f"  Failed to fetch page {page}")
                        break
                    
                    soup = self.parse_html(response.text)
                    
                    # Find product links (Shopware 6 uses a.product-name for products)
                    product_links = soup.select('a.product-name')
                    
                    # Debug: if no products found, check HTML
                    if not product_links and page == 1:
                        # Check if page has product boxes
                        product_boxes = soup.select('div.product-box')
                        if product_boxes:
                            self.logger.warning(f"  Found {len(product_boxes)} product-box divs but no product-name links!")
                            # Save HTML for debugging
                            debug_file = f"debug_no_products_{i}.html"
                            with open(debug_file, 'w', encoding='utf-8') as f:
                                f.write(response.text)
                            self.logger.warning(f"  Saved HTML to {debug_file}")
                    
                    # Extract product URLs
                    page_products = 0
                    # Extract category name from URL for mapping
                    category_name = self._parse_category_from_url(category_url)
                    
                    for link in product_links:
                        href = link.get('href', '')
                        if href:
                            # Make absolute URL
                            if href.startswith('/'):
                                href = self.base_url + href
                            elif not href.startswith('http'):
                                href = self.base_url + '/' + href
                            
                            if href not in seen:
                                seen.add(href)
                                product_urls.append(href)
                                # Store category mapping
                                self._product_category_map[href] = category_name
                                page_products += 1
                                category_has_products = True
                    
                    if page == 1:
                        self.logger.info(f"  Found {page_products} products")
                    else:
                        self.logger.info(f"  Page {page}: Found {page_products} products")
                    
                    # Check if we've reached the limit
                    if max_urls and len(product_urls) >= max_urls:
                        self.logger.info(f"Reached max_urls limit of {max_urls}")
                        return product_urls[:max_urls]
                    
                    # Check if there's a next page
                    # Shopware 6 uses li.page-item.page-next (not disabled means there's a next page)
                    next_button = soup.select_one('li.page-item.page-next:not(.disabled)')
                    if not next_button or page_products == 0:
                        break
                    
                    page += 1
                    
                    # Small delay between pages
                    import time
                    time.sleep(0.5)
                
                # Small delay between categories to avoid rate limiting
                if i < len(self.all_categories):
                    import time
                    time.sleep(1)
                
                if max_urls and len(product_urls) >= max_urls:
                    break
            
            self.logger.info(f"\nTotal product URLs found: {len(product_urls)}")
            
        except Exception as e:
            self.logger.error(f"Error getting product URLs: {e}", exc_info=True)
        
        return product_urls[:max_urls] if max_urls else product_urls
    
    def _extract_category_from_url(self, url: str, product_url: str) -> str:
        """
        Extract category from the category URL that led to this product.
        Stores mapping during URL collection and retrieves during scraping.
        """
        # Check if we have a stored category for this product
        if hasattr(self, '_product_category_map') and product_url in self._product_category_map:
            return self._product_category_map[product_url]
        return ""
    
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
            
            # Extract manufacturer from product name first (it's usually the first word/brand)
            manufacturer = ""
            if product_name:
                first_word = product_name.split()[0] if product_name.split() else ""
                # Check if first word looks like a manufacturer (capitalized, not a common word)
                if first_word and (first_word[0].isupper() or first_word.isupper()):
                    manufacturer = first_word
            
            # Fallback: Try HTML elements if not found in name
            if not manufacturer:
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
            
            # Extract category from URL mapping first (most reliable)
            category = self._extract_category_from_url(url, url)
            
            # Fallback: Extract from breadcrumbs if not in mapping
            if not category:
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
