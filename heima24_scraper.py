"""
Heima24 Scraper
Website: https://www.heima24.de
Platform: Custom (Bad, Heizung & Sanitär)
"""
import sys
import re
from typing import List, Dict, Optional, Any
from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS, SCRAPER_CONFIGS


SCRAPER_NAME = "heima24"


class Heima24Scraper(BaseScraper):
    """
    Scraper for Heima24 (heating, plumbing, sanitary products).
    Extracts: manufacturer, category, name, title, article_number, 
              price_net, price_gross, ean, product_image, product_url
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        # Get website-specific config
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://www.heima24.de")
        
        self.logger.info(f"Initialized scraper for {self.base_url}")
    
    def get_product_urls(self) -> List[str]:
        """
        Get list of product URLs from sitemap.
        """
        product_urls = []
        
        try:
            self.logger.info("Fetching sitemap...")
            sitemap_url = "https://heima24.de/sitemap.xml"
            response = self.make_request(sitemap_url)
            
            if not response:
                self.logger.error("Failed to fetch sitemap")
                return product_urls
            
            soup = self.parse_html(response.text)
            locs = soup.find_all('loc')
            
            skip_terms = [
                "stellenangebot",
                "ueber-uns",
                "retourenabwicklung",
                "widerruf",
                "datenschutz",
                "impressum",
                "kontakt",
                "versand",
                "zahlungs",
                "agb",
                "climatechange",
                "renewableenergy",
                "neue-angebote",
                "ust-regelung",
            ]

            for loc in locs:
                url = loc.text.strip()
                # Filter for product pages (they have .html extension)
                if not url.endswith('.html'):
                    continue
                if url == self.base_url + '/':
                    continue
                url_l = url.lower()
                if any(term in url_l for term in skip_terms):
                    continue
                if '/blog/' in url_l or '/ratgeber/' in url_l:
                    continue
                if url_l.count('-') < 2 and '/shop/' not in url_l:
                    # Heuristic: product URLs on this site are usually descriptive slugs.
                    continue
                if url not in product_urls:
                    product_urls.append(url)
            
            self.logger.info(f"Found {len(product_urls)} product URLs")
            
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
            product_name = ''
            manufacturer = ''
            article_number = ''
            ean = ''
            price_gross = ''
            product_image = ''
            
            # Try to extract from JSON-LD structured data first (most reliable)
            json_ld = soup.find('script', {'type': 'application/ld+json'})
            if json_ld:
                try:
                    import json
                    import html
                    data = json.loads(json_ld.string)
                    
                    # Some pages expose a list of schemas; keep only Product node.
                    if isinstance(data, list):
                        data = next(
                            (item for item in data if isinstance(item, dict) and item.get('@type') == 'Product'),
                            {}
                        )

                    # Check if it's a Product schema
                    if isinstance(data, dict) and data.get('@type') == 'Product':
                        product_name = html.unescape(data.get('name', ''))
                        manufacturer = data.get('brand', {}).get('name', '') if isinstance(data.get('brand'), dict) else ''
                        article_number = data.get('mpn', '') or data.get('sku', '')
                        ean = data.get('gtin8', '') or data.get('gtin13', '') or data.get('gtin14', '')

                        # Get price from offers
                        offers = data.get('offers', {})
                        price_gross_raw = str(offers.get('price', '')) if isinstance(offers, dict) else ''
                        price_gross = price_gross_raw.replace('.', ',') if price_gross_raw else ''

                        # Get image
                        images = data.get('image', [])
                        product_image = images[0] if isinstance(images, list) and images else ''

                        self.logger.info(f"Extracted from JSON-LD: {product_name}, EAN: {ean}")
                except Exception as e:
                    self.logger.warning(f"Failed to parse JSON-LD: {e}")
            
            # Fallback to HTML extraction if JSON-LD didn't work
            if not product_name:
                product_name = self._extract_text(soup, [
                    'h1',
                    'div.product-name h1',
                    'span[itemprop="name"]'
                ])
            
            title = product_name
            name = product_name
            
            # Extract manufacturer/brand from HTML if not in JSON-LD
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
            
            # Extract article number from HTML if not in JSON-LD
            if not article_number:
                # Look for "Artikel-Nr.:" in text
                article_div = soup.find('div', class_='text-left')
                if article_div:
                    text = article_div.get_text()
                    if 'Artikel-Nr.:' in text:
                        match = re.search(r'Artikel-Nr\.:\s*([A-Z0-9]+)', text)
                        if match:
                            article_number = match.group(1)
                
                # Fallback: Look for article number in table rows
                if not article_number:
                    table_rows = soup.find_all('tr')
                    for row in table_rows:
                        cells = row.find_all('td')
                        if cells and len(cells) > 0:
                            first_cell_text = cells[0].text.strip()
                            # Article numbers are usually alphanumeric codes
                            if re.match(r'^[A-Z0-9]{5,}$', first_cell_text):
                                article_number = first_cell_text
                                break
            
            # Extract price from HTML if not in JSON-LD
            if not price_gross:
                price_gross_raw = ""
                
                # Look for price in the "Bei uns:" section
                price_section = soup.find(text=re.compile(r'Bei uns:'))
                if price_section:
                    parent = price_section.find_parent()
                    if parent:
                        price_text = parent.text
                        price_match = re.search(r'([\d,\.]+)\s*EUR', price_text)
                        if price_match:
                            price_gross_raw = price_match.group(1)
                
                # Fallback: look for any EUR price
                if not price_gross_raw:
                    price_elements = soup.find_all(text=re.compile(r'[\d,\.]+\s*EUR'))
                    if price_elements:
                        for elem in price_elements:
                            price_match = re.search(r'([\d,\.]+)\s*EUR', elem)
                            if price_match:
                                price_gross_raw = price_match.group(1)
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
            
            # Extract EAN from HTML if not in JSON-LD
            if not ean:
                # Method 1: Look for "EAN:" in the text-left div (e.g., "Artikel-Nr.: XXX | EAN: YYY")
                article_div = soup.find('div', class_='text-left')
                if article_div:
                    text = article_div.get_text()
                    if 'EAN:' in text:
                        match = re.search(r'EAN:\s*(\d+)', text)
                        if match:
                            ean = match.group(1)
                
                # Method 2: Look for EAN in table rows
                if not ean:
                    table_rows = soup.find_all('tr')
                    for row in table_rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            label = cells[0].get_text(strip=True)
                            if label == 'EAN:':
                                ean = cells[1].get_text(strip=True)
                                break
                
                # Method 3: Fallback to standard selectors
                if not ean:
                    ean = self._extract_text(soup, [
                        'span[itemprop="gtin13"]',
                        'span.ean',
                        'meta[itemprop="gtin13"]'
                    ])
            
            # Extract image from HTML if not in JSON-LD
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
    scraper = Heima24Scraper()
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
