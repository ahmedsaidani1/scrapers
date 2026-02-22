"""
Heizungsdiscount24 Scraper
Website: https://www.heizungsdiscount24.de
Platform: JTL-Shop
"""
import sys
import re
from typing import List, Dict, Optional, Any
from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS, SCRAPER_CONFIGS


SCRAPER_NAME = "heizungsdiscount24"


class Heizungsdiscount24Scraper(BaseScraper):
    """
    Scraper for Heizungsdiscount24 (JTL-Shop platform - heating equipment).
    Extracts: manufacturer, category, name, title, article_number, 
              price_net, price_gross, ean, product_image, product_url
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        # Get website-specific config
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://www.heizungsdiscount24.de")
        
        self.logger.info(f"Initialized scraper for {self.base_url}")
    
    def get_product_urls(self) -> List[str]:
        """
        Get list of product URLs from multiple sitemaps.
        """
        product_urls = []
        
        try:
            self.logger.info("Fetching main sitemap...")
            sitemap_url = "https://www.heizungsdiscount24.de/sitemap.xml"
            response = self.make_request(sitemap_url)
            
            if not response:
                self.logger.error("Failed to fetch main sitemap")
                return product_urls
            
            soup = self.parse_html(response.text)
            sitemap_locs = soup.find_all('loc')
            
            # Filter for product sitemaps (sitemap_imgs*.xml)
            product_sitemaps = [loc.text for loc in sitemap_locs if 'sitemap_imgs' in loc.text]
            
            self.logger.info(f"Found {len(product_sitemaps)} product sitemaps")
            
            # Process each product sitemap
            for i, sitemap_url in enumerate(product_sitemaps, 1):
                self.logger.info(f"Processing sitemap {i}/{len(product_sitemaps)}: {sitemap_url}")
                
                try:
                    sitemap_response = self.make_request(sitemap_url)
                    if not sitemap_response:
                        continue
                    
                    sitemap_soup = self.parse_html(sitemap_response.text)
                    urls = sitemap_soup.find_all('loc')
                    
                    for url_tag in urls:
                        url = url_tag.text.strip()
                        if url.endswith('.html'):  # Product pages end with .html
                            product_urls.append(url)
                    
                    self.logger.info(f"Extracted {len(urls)} URLs from this sitemap")
                    
                except Exception as e:
                    self.logger.error(f"Error processing sitemap {sitemap_url}: {e}")
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
                'h1',
                'div.product-name h1',
                'span[itemprop="name"]'
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
            
            # Fallback: try from breadcrumbs or meta
            if not manufacturer:
                manufacturer = self._extract_text(soup, [
                    'span[itemprop="brand"]',
                    'div.manufacturer',
                    'a.brand-link'
                ])
            
            # Extract category from breadcrumbs or URL
            category = self._extract_text(soup, [
                'div.breadcrumb a:nth-last-child(2)',
                'span[itemprop="category"]'
            ])
            
            # Infer category from URL if not found
            if not category and '/' in url:
                parts = url.split('/')
                if len(parts) > 3:
                    category = parts[3].replace('-', ' ').title()
            
            # Extract article number from dataLayer or page
            article_number = ""
            # Try to find in dataLayer script
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'dataLayer' in script.string and '"id"' in script.string:
                    # Extract ID from dataLayer
                    id_match = re.search(r'"id"\s*:\s*"([^"]+)"', script.string)
                    if id_match:
                        article_number = id_match.group(1)
                        break
            
            # Extract EAN from JSON-LD structured data
            ean = ""
            product_image = ""
            for script in scripts:
                if script.string and '"@type"' in script.string and '"Product"' in script.string:
                    try:
                        # Try to parse JSON-LD
                        import json
                        json_text = script.string.strip()
                        if json_text.startswith('<![CDATA['):
                            json_text = json_text.replace('<![CDATA[', '').replace(']]>', '')
                        product_data = json.loads(json_text)
                        
                        # Extract EAN (gtin13)
                        if 'gtin13' in product_data:
                            ean = product_data['gtin13']
                        
                        # Extract image
                        if 'image' in product_data:
                            image_data = product_data['image']
                            if isinstance(image_data, list) and len(image_data) > 0:
                                product_image = image_data[0]
                            elif isinstance(image_data, str):
                                product_image = image_data
                        
                        break
                    except:
                        pass
            
            # Fallback: Try HTML elements for EAN if not found in JSON-LD
            if not ean:
                ean = self._extract_text(soup, [
                    'span[itemprop="gtin13"]',
                    'span.ean',
                    'meta[itemprop="gtin13"]'
                ])
            
            # Extract price (gross - with VAT)
            price_gross_raw = ""
            
            # Look for price in text containing EUR or €
            price_elements = soup.find_all(text=re.compile(r'[\d,\.]+\s*(EUR|€)'))
            for elem in price_elements:
                # Skip dataLayer script
                if 'dataLayer' not in str(elem):
                    price_match = re.search(r'([\d,\.]+)\s*(?:EUR|€)', elem)
                    if price_match:
                        price_gross_raw = price_match.group(1)
                        break
            
            # Also try dataLayer for price
            if not price_gross_raw:
                for script in scripts:
                    if script.string and 'dataLayer' in script.string and '"price"' in script.string:
                        price_match = re.search(r'"price"\s*:\s*"([\d\.]+)"', script.string)
                        if price_match:
                            price_gross_raw = price_match.group(1).replace('.', ',')
                            break
            
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
            
            # Fallback: Extract image from HTML if not found in JSON-LD
            if not product_image:
                product_image = self._extract_image(soup, [
                    'img[itemprop="image"]',
                    'div.product-image img',
                    'img.main-image',
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
    scraper = Heizungsdiscount24Scraper()
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
