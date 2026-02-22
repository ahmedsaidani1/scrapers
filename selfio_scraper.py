"""
Selfio Scraper
Website: https://www.selfio.de
Platform: Shopware 6
"""
import sys
import re
import gzip
from typing import List, Dict, Optional, Any
from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS, SCRAPER_CONFIGS


SCRAPER_NAME = "selfio"


class SelfioScraper(BaseScraper):
    """
    Scraper for Selfio (Shopware 6 platform with compressed sitemaps).
    Extracts: manufacturer, category, name, title, article_number, 
              price_net, price_gross, ean, product_image, product_url
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        # Get website-specific config
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://www.selfio.de")
        self.sitemap_url = self.config.get("sitemap_url", "https://www.selfio.de/sitemap.xml")
        
        self.logger.info(f"Initialized scraper for {self.base_url}")
    
    def get_product_urls(self, max_sitemaps: int = 5) -> List[str]:
        """
        Get list of product URLs from compressed sitemaps.
        Selfio uses gzipped sitemap files.
        
        Args:
            max_sitemaps: Maximum number of sitemap files to process (default: 5)
        """
        product_urls = []
        
        try:
            # Get main sitemap index
            self.logger.info("Fetching main sitemap index...")
            response = self.make_request(self.sitemap_url)
            
            if not response:
                self.logger.error("Failed to fetch main sitemap")
                return product_urls
            
            soup = self.parse_html(response.text)
            sitemap_locs = soup.find_all('loc')
            
            # Limit to first N sitemaps
            sitemap_locs = sitemap_locs[:max_sitemaps]
            
            self.logger.info(f"Processing first {len(sitemap_locs)} sub-sitemaps")
            
            # Process each compressed sitemap
            for i, loc in enumerate(sitemap_locs, 1):
                sitemap_gz_url = loc.text.strip()
                self.logger.info(f"Processing sitemap {i}/{len(sitemap_locs)}: {sitemap_gz_url}")
                
                try:
                    # Download and decompress
                    gz_response = self.make_request(sitemap_gz_url)
                    if not gz_response:
                        continue
                    
                    # Decompress gzip content
                    decompressed = gzip.decompress(gz_response.content).decode('utf-8')
                    
                    # Parse decompressed XML
                    sitemap_soup = self.parse_html(decompressed)
                    urls = sitemap_soup.find_all('loc')
                    
                    for url_tag in urls:
                        url = url_tag.text.strip()
                        # Filter for product pages - they contain /produkte/ in the path
                        if '/produkte/' in url and not url.endswith('/'):
                            product_urls.append(url)
                    
                    self.logger.info(f"  Extracted {len(urls)} URLs (total: {len(product_urls)})")
                    
                except Exception as e:
                    self.logger.error(f"Error processing sitemap {sitemap_gz_url}: {e}")
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
            
            # Try JSON-LD extraction first (most reliable for Selfio)
            json_ld_data = self._extract_from_json_ld(soup)
            
            # Extract product name/title
            product_name = json_ld_data.get('name', '')
            if not product_name:
                product_name = self._extract_text(soup, [
                    'h1.product-detail-name',
                    'h1[itemprop="name"]',
                    'h1.product-title',
                    'h1'
                ])
            
            title = product_name
            name = product_name
            
            # Extract manufacturer from product name (first word)
            manufacturer = ""
            if product_name:
                first_word = product_name.split()[0] if product_name.split() else ""
                # Check if first word looks like a manufacturer (capitalized)
                if first_word and (first_word[0].isupper() or first_word.isupper()):
                    manufacturer = first_word
            
            # Fallback: try from HTML elements
            if not manufacturer:
                manufacturer = self._extract_text(soup, [
                    'a.product-detail-manufacturer-link',
                    'span[itemprop="brand"]',
                    'div.product-detail-manufacturer',
                    'meta[itemprop="brand"]'
                ])
            
            # Extract article number from product name (look for number pattern)
            article_number = json_ld_data.get('article_number', '')
            if not article_number and product_name:
                # Look for article number pattern in name (e.g., "33521705")
                article_match = re.search(r'\b(\d{5,})\b', product_name)
                if article_match:
                    article_number = article_match.group(1)
            
            # Fallback: try from HTML elements
            if not article_number:
                article_number = self._extract_text(soup, [
                    'span.product-detail-ordernumber',
                    'span[itemprop="sku"]',
                    'div.product-number',
                    'meta[itemprop="sku"]'
                ])
            
            # Extract category from breadcrumbs
            category = self._extract_text(soup, [
                'nav.breadcrumb li:nth-last-child(2) a',
                'span[itemprop="category"]',
                'div.product-detail-category'
            ])
            
            # Extract price from JSON-LD
            price_gross = json_ld_data.get('price_gross', '')
            
            # Fallback: try from HTML elements
            if not price_gross:
                price_gross_raw = self._extract_text(soup, [
                    'meta[itemprop="price"]',
                    'span.product-detail-price',
                    'div.product-price .price',
                    'span[itemprop="price"]'
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
                    price_net = ""
            
            # Extract EAN from JSON-LD
            ean = json_ld_data.get('ean', '')
            
            # Fallback: try from HTML elements
            if not ean:
                ean = self._extract_text(soup, [
                    'span[itemprop="gtin13"]',
                    'div.product-detail-ean',
                    'span.ean',
                    'meta[itemprop="gtin13"]'
                ])
            
            # Extract image from JSON-LD
            product_image = json_ld_data.get('image', '')
            
            # Fallback: try from HTML elements
            if not product_image:
                product_image = self._extract_image(soup, [
                    'div.gallery-slider-item img',
                    'img.product-detail-image',
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
    
    def _extract_from_json_ld(self, soup) -> Dict[str, str]:
        """
        Extract product data from JSON-LD structured data.
        Returns dict with: name, ean, price_gross, image, article_number
        """
        result = {
            'name': '',
            'ean': '',
            'price_gross': '',
            'image': '',
            'article_number': ''
        }
        
        try:
            # Find JSON-LD script tag
            scripts = soup.find_all('script', type='application/ld+json')
            
            for script in scripts:
                if not script.string:
                    continue
                
                try:
                    import json
                    json_text = script.string.strip()
                    
                    # Remove CDATA if present
                    if json_text.startswith('<![CDATA['):
                        json_text = json_text.replace('<![CDATA[', '').replace(']]>', '')
                    
                    data = json.loads(json_text)
                    
                    # Check if it's a Product schema
                    if data.get('@type') == 'Product':
                        # Extract name
                        if 'name' in data:
                            result['name'] = data['name']
                        
                        # Extract EAN
                        if 'ean' in data:
                            result['ean'] = data['ean']
                        elif 'gtin13' in data:
                            result['ean'] = data['gtin13']
                        
                        # Extract SKU/article number
                        if 'sku' in data:
                            result['article_number'] = data['sku']
                        elif 'mpn' in data:  # Manufacturer Part Number
                            result['article_number'] = data['mpn']
                        
                        # Extract image
                        if 'image' in data:
                            image_data = data['image']
                            if isinstance(image_data, list) and len(image_data) > 0:
                                result['image'] = image_data[0]
                            elif isinstance(image_data, str):
                                result['image'] = image_data
                        
                        # Extract price from offers
                        if 'offers' in data:
                            offers = data['offers']
                            
                            # Handle AggregateOffer
                            if offers.get('@type') == 'AggregateOffer':
                                if 'lowPrice' in offers:
                                    price = str(offers['lowPrice'])
                                    # Convert to German format
                                    result['price_gross'] = price.replace('.', ',')
                            
                            # Handle single Offer
                            elif offers.get('@type') == 'Offer':
                                if 'price' in offers:
                                    price = str(offers['price'])
                                    # Convert to German format
                                    result['price_gross'] = price.replace('.', ',')
                        
                        # Extract article number from name if not found yet
                        if not result['article_number'] and result['name']:
                            # Look for article number pattern (5+ digits)
                            article_match = re.search(r'\b(\d{5,})\b', result['name'])
                            if article_match:
                                result['article_number'] = article_match.group(1)
                        
                        # Also try from description
                        if not result['article_number'] and 'description' in data:
                            desc = data['description']
                            # Look for article number pattern
                            article_match = re.search(r'\b(\d{5,})\b', desc)
                            if article_match:
                                result['article_number'] = article_match.group(1)
                        
                        break
                
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    self.logger.debug(f"Error parsing JSON-LD: {e}")
                    continue
        
        except Exception as e:
            self.logger.debug(f"Error extracting JSON-LD: {e}")
        
        return result


def main():
    """Main execution."""
    scraper = SelfioScraper()
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
