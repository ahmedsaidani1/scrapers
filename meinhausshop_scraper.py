"""
MeinHausShop Scraper
Website: https://www.meinhausshop.de
Platform: Shopware
"""
import sys
import os
import re
import gzip
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS, SCRAPER_CONFIGS


SCRAPER_NAME = "meinhausshop"


class MeinHausShopScraper(BaseScraper):
    """
    Scraper for MeinHausShop (Shopware platform).
    Extracts: manufacturer, category, name, title, article_number, 
              price_net, price_gross, ean, product_image, product_url
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        # Get website-specific config
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://www.meinhausshop.de")
        
        self.logger.info(f"Initialized scraper for {self.base_url}")

    def _normalize_url(self, raw_url: str) -> str:
        if not raw_url:
            return ""
        url = raw_url.strip().split("?")[0].split("#")[0]
        if url.endswith("/") and url != self.base_url + "/":
            url = url[:-1]
        return url

    def _is_product_url(self, raw_url: str) -> bool:
        url = self._normalize_url(raw_url)
        if not url:
            return False
        if "meinhausshop.de" not in url:
            return False
        if "/web/" in url or "/konto/" in url or "/checkout/" in url:
            return False
        if url in (self.base_url, self.base_url + "/"):
            return False
        lower_url = url.lower()
        skip_parts = [
            "/impressum",
            "/datenschutz",
            "/agb",
            "/widerruf",
            "/versand",
            "/kontakt",
            "/hilfe",
            "/service",
            "/blog",
            "/sitemap",
        ]
        if any(part in lower_url for part in skip_parts):
            return False
        path = lower_url.replace(self.base_url.lower(), "").strip("/")
        if not path:
            return False
        if len(path) < 8:
            return False
        return True
    
    def get_product_urls(self) -> List[str]:
        """
        Get list of product URLs from compressed sitemaps.
        MeinHausShop uses gzipped sitemap files.
        """
        product_urls = []
        seen_urls = set()
        
        try:
            # Get main sitemap index
            self.logger.info("Fetching main sitemap index...")
            sitemap_url = "https://meinhausshop.de/sitemap.xml"
            response = self.make_request(sitemap_url)
            
            if not response:
                self.logger.error("Failed to fetch main sitemap")
                return product_urls
            
            soup = BeautifulSoup(response.text, "xml")
            sitemap_locs = soup.find_all('loc')
            selected_parts = self._get_selected_sitemap_parts(len(sitemap_locs))
            if selected_parts:
                self.logger.info(
                    f"Sitemap part filter active: processing parts {sorted(selected_parts)} only"
                )
             
            self.logger.info(f"Found {len(sitemap_locs)} sub-sitemaps")
             
            # Process each compressed sitemap
            for i, loc in enumerate(sitemap_locs, 1):
                if selected_parts and i not in selected_parts:
                    continue
                sitemap_gz_url = loc.text.strip()
                self.logger.info(f"Processing sitemap {i}/{len(sitemap_locs)}: {sitemap_gz_url}")
                
                try:
                    # Download and decompress
                    gz_response = self.make_request(sitemap_gz_url)
                    if not gz_response:
                        continue
                    
                    # Decompress gzip content
                    decompressed = gzip.decompress(gz_response.content).decode('utf-8')

                    # Regex parsing is faster than full DOM build on very large sitemap files.
                    urls = re.findall(r"<loc>([^<]+)</loc>", decompressed)
                    added = 0
                    for raw_url in urls:
                        url = self._normalize_url(raw_url)
                        if not url:
                            continue
                        if not self._is_product_url(url):
                            continue
                        if url in seen_urls:
                            continue
                        seen_urls.add(url)
                        product_urls.append(url)
                        added += 1

                    self.logger.info(f"Extracted {added} unique product URLs from this sitemap")
                    
                except Exception as e:
                    self.logger.error(f"Error processing sitemap {sitemap_gz_url}: {e}")
                    continue
            
            self.logger.info(f"Total product URLs found: {len(product_urls)}")
            
        except Exception as e:
            self.logger.error(f"Error getting product URLs: {e}", exc_info=True)
        
        return product_urls

    def _get_selected_sitemap_parts(self, total_parts: int) -> Optional[set]:
        """
        Parse optional env filter for sitemap parts.
        Example: MEINHAUSSHOP_SITEMAP_PARTS="1,2" or "4"
        """
        raw = (os.getenv("MEINHAUSSHOP_SITEMAP_PARTS") or "").strip()
        if not raw:
            return None

        selected = set()
        for piece in raw.split(","):
            token = piece.strip()
            if not token:
                continue
            try:
                idx = int(token)
            except ValueError:
                continue
            if 1 <= idx <= total_parts:
                selected.add(idx)
        return selected or None
    
    def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape individual product page.
        
        Extracts all required fields for new client requirements.
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
            
            # For this site, name and title are the same
            title = product_name
            name = product_name
            
            # Extract manufacturer/brand
            manufacturer = self._extract_text(soup, [
                'span[itemprop="brand"]',
                'a.product-detail-manufacturer-link',
                'div.product-detail-manufacturer',
                'meta[itemprop="brand"]'
            ])
            
            # Extract article number/SKU
            article_number = self._extract_text(soup, [
                'span.product-detail-ordernumber',
                'span[itemprop="sku"]',
                'div.product-number',
                'span.sku'
            ])
            
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
    scraper = MeinHausShopScraper()
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
