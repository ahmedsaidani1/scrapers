"""
Pumpe24 Scraper with Cloudscraper (bypasses Cloudflare protection)
Website: https://www.pumpe24.de
Platform: Magento (Cloudflare protected)
Strategy: Scrape from category pages using cloudscraper
"""
import sys
import re
import time
import os
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
import cloudscraper
from base_scraper import BaseScraper
from google_sheets_helper import push_data
from config import SHEET_IDS, SCRAPER_CONFIGS


SCRAPER_NAME = "pumpe24"


class Pumpe24Scraper(BaseScraper):
    """
    Scraper for Pumpe24 using cloudscraper to bypass Cloudflare protection.
    """
    
    def __init__(self):
        super().__init__(SCRAPER_NAME)
        
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://www.pumpe24.de")
        self.proxy = os.getenv("PUMPE24_PROXY") or self.config.get("proxy")
        self.request_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
        
        # Initialize cloudscraper session
        self.scraper = self._create_scraper_session()
        if self.proxy:
            self.logger.info("Using proxy for pumpe24 requests")
        
        # Main category URLs to scrape
        self.category_urls = [
            "https://www.pumpe24.de/pumpen.html",
            "https://www.pumpe24.de/steuerungen.html",
            "https://www.pumpe24.de/brunnenbau.html",
            "https://www.pumpe24.de/beregnung.html",
            "https://www.pumpe24.de/rohre.html",
            "https://www.pumpe24.de/fittinge.html",
            "https://www.pumpe24.de/industrie.html",
            "https://www.pumpe24.de/zubehoer.html",
            "https://www.pumpe24.de/geothermie.html",
            "https://www.pumpe24.de/ersatzteile.html"
        ]
        
        self.logger.info(f"Initialized cloudscraper for {self.base_url}")
        self._warm_up_session()

    def _create_scraper_session(self):
        """Create a cloudscraper session with optional proxy."""
        scraper = cloudscraper.create_scraper(
            browser={
                "browser": "chrome",
                "platform": "windows",
                "mobile": False,
            }
        )
        if self.proxy:
            scraper.proxies = {
                "http": self.proxy,
                "https": self.proxy,
            }
        return scraper

    def _warm_up_session(self):
        """
        Warm up Cloudflare cookies before scraping categories.
        This improves success rate on protected sites.
        """
        warmup_urls = [
            self.base_url,
            f"{self.base_url}/robots.txt",
        ]
        for warmup_url in warmup_urls:
            try:
                response = self.scraper.get(
                    warmup_url,
                    headers=self.request_headers,
                    timeout=20,
                    allow_redirects=True,
                )
                self.logger.info(f"Warm-up {warmup_url}: HTTP {response.status_code}")
                # Stop after first non-403 response
                if response.status_code != 403:
                    return
            except Exception as e:
                self.logger.debug(f"Warm-up request failed for {warmup_url}: {e}")
    
    def make_request(self, url: str, **kwargs):
        """Override to use cloudscraper instead of requests."""
        request_headers = dict(self.request_headers)
        request_headers.update(kwargs.pop("headers", {}))

        attempts = kwargs.pop("attempts", 3)
        for attempt in range(1, attempts + 1):
            try:
                response = self.scraper.get(
                    url,
                    timeout=30,
                    headers=request_headers,
                    allow_redirects=True,
                    **kwargs,
                )

                if response.status_code == 403:
                    self.logger.warning(f"403 for {url} (attempt {attempt}/{attempts})")
                    # Refresh cookies before next retry
                    self._warm_up_session()
                    time.sleep(1.5 * attempt)
                    continue

                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == attempts:
                    self.logger.error(f"Request failed for {url}: {e}")
                else:
                    self.logger.warning(
                        f"Request retry for {url} after error (attempt {attempt}/{attempts}): {e}"
                    )
                    time.sleep(1.0 * attempt)
        return None

    def _is_product_url(self, url: str) -> bool:
        """Determine if a URL is likely a product page."""
        if not url or "pumpe24.de" not in url:
            return False
        if not url.endswith(".html"):
            return False

        # Exclude known non-product/category pages
        skip_parts = [
            "/impressum",
            "/datenschutz",
            "/agb",
            "/kontakt",
            "/versand",
            "/zahlung",
            "/widerruf",
            "/pumpen.html",
            "/hauswasserwerke.html",
            "/druckbehaelter.html",
            "/zubehoer.html",
            "/rohre-fittings.html",
        ]
        lower_url = url.lower()
        for part in skip_parts:
            if part in lower_url:
                return False

        # Product URLs are usually long/specific and often contain hyphens/numbers
        path = lower_url.replace("https://www.pumpe24.de/", "")
        return len(path) > 20 and ("-" in path or any(ch.isdigit() for ch in path))

    def _get_product_urls_from_sitemap(self, max_urls: int = None) -> List[str]:
        """
        Fallback: fetch product URLs from sitemap when categories are blocked.
        """
        product_urls = []
        seen = set()

        self.logger.info("Category scraping yielded no URLs; trying sitemap fallback...")
        sitemap_response = self.make_request(f"{self.base_url}/sitemap.xml", attempts=2)
        if not sitemap_response:
            return []

        soup = BeautifulSoup(sitemap_response.text, "xml")
        sitemap_locs = [loc.get_text(strip=True) for loc in soup.find_all("loc")]
        if not sitemap_locs:
            return []

        # If this is a sitemap index, process sub-sitemaps. Otherwise, process as direct URL list.
        targets = sitemap_locs
        if any("sitemap" in loc for loc in sitemap_locs):
            targets = sitemap_locs[:20]

        for target in targets:
            # Direct URL rows from urlset
            if target.endswith(".html"):
                if self._is_product_url(target) and target not in seen:
                    seen.add(target)
                    product_urls.append(target)
                continue

            # Sub-sitemap rows
            if "sitemap" not in target:
                continue

            sub_response = self.make_request(target, attempts=2)
            if not sub_response:
                continue

            sub_soup = BeautifulSoup(sub_response.text, "xml")
            for loc in sub_soup.find_all("loc"):
                url = loc.get_text(strip=True)
                if self._is_product_url(url) and url not in seen:
                    seen.add(url)
                    product_urls.append(url)
                    if max_urls and len(product_urls) >= max_urls:
                        return product_urls

        return product_urls
    
    def _get_subcategories(self, category_url: str) -> List[str]:
        """Get subcategory URLs from a main category page."""
        subcategories = []
        
        response = self.make_request(category_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all product-item-link elements
        links = soup.select('a.product-item-link')
        
        for link in links:
            href = link.get('href', '')
            # Subcategories typically have shorter paths and end with category names
            # e.g., /pumpen/gartenpumpen.html (subcategory) vs /pumpe-espa-aspri-15-5m-gg.html (product)
            if href and href.endswith('.html'):
                # Count path segments - subcategories have fewer
                path_segments = href.replace('https://www.pumpe24.de/', '').count('/')
                # Subcategories typically have 1 slash (e.g., pumpen/gartenpumpen.html)
                # Products have 0 slashes or very long names with many hyphens
                if path_segments >= 1 and href not in subcategories:
                    subcategories.append(href)
        
        return subcategories

    def get_product_urls(self, max_urls: int = None) -> List[str]:
        """
        Get product URLs by scraping category pages and finding actual products.
        Handles two-level structure: main categories -> subcategories -> products.
        Handles pagination to get all products from each subcategory.
        """
        product_urls = []
        seen = set()
        
        try:
            self.logger.info(f"Scraping {len(self.category_urls)} main category pages...")
            
            # First, collect all subcategories from main categories
            all_subcategories = []
            for i, category_url in enumerate(self.category_urls, 1):
                self.logger.info(f"[{i}/{len(self.category_urls)}] Finding subcategories in: {category_url}")
                subcats = self._get_subcategories(category_url)
                all_subcategories.extend(subcats)
                self.logger.info(f"  Found {len(subcats)} subcategories")
                time.sleep(1)
            
            self.logger.info(f"\nTotal subcategories found: {len(all_subcategories)}")
            self.logger.info(f"Now scraping products from subcategories...\n")
            
            # Now scrape products from each subcategory with pagination
            for i, subcategory_url in enumerate(all_subcategories, 1):
                self.logger.info(f"[{i}/{len(all_subcategories)}] Scraping subcategory: {subcategory_url}")
                
                # Scrape all pages in this subcategory
                page = 1
                while True:
                    # Magento pagination format: ?p=1, ?p=2, etc.
                    if page == 1:
                        page_url = subcategory_url
                    else:
                        separator = '&' if '?' in subcategory_url else '?'
                        page_url = f"{subcategory_url}{separator}p={page}"
                    
                    if page > 1:
                        self.logger.info(f"  Scraping page {page}: {page_url}")
                    
                    response = self.make_request(page_url)
                    if not response:
                        break
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find product links (Magento structure)
                    product_links = soup.select('a.product-item-link')
                    
                    if not product_links:
                        self.logger.info(f"  No products found on page {page}")
                        break
                    
                    page_products = 0
                    for link in product_links:
                        href = link.get('href', '')
                        if self._is_product_url(href) and href not in seen:
                            seen.add(href)
                            product_urls.append(href)
                            page_products += 1
                    
                    if page == 1:
                        self.logger.info(f"  Found {page_products} products on first page")
                    else:
                        self.logger.info(f"  Page {page}: Found {page_products} new products")
                    
                    # Check if we've reached the limit
                    if max_urls and len(product_urls) >= max_urls:
                        self.logger.info(f"Reached max_urls limit of {max_urls}")
                        return product_urls[:max_urls]
                    
                    # Check if there's a next page
                    next_page = soup.select_one('a.action.next')
                    if not next_page or page_products == 0:
                        break
                    
                    page += 1
                    time.sleep(1)
                
                self.logger.info(f"  Subcategory complete. Total products so far: {len(product_urls)}")
                
                if max_urls and len(product_urls) >= max_urls:
                    break
                
                time.sleep(1)
            
            if not product_urls:
                self.logger.info("No products found via categories, trying sitemap fallback...")
                product_urls = self._get_product_urls_from_sitemap(max_urls=max_urls)
                if product_urls:
                    self.logger.info(f"Sitemap fallback found {len(product_urls)} products")

            self.logger.info(f"\nTotal product URLs found: {len(product_urls)}")

            if not product_urls and not self.proxy:
                self.logger.warning(
                    "No product URLs found and no proxy configured. "
                    "Pumpe24 may block Render datacenter IPs. "
                    "Set PUMPE24_PROXY to a residential/rotating proxy."
                )
            
        except Exception as e:
            self.logger.error(f"Error getting product URLs: {e}", exc_info=True)
        
        return product_urls[:max_urls] if max_urls else product_urls
    
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
                'h1[itemprop="name"]',
                'h1'
            ])
            
            if not product_name:
                self.logger.warning(f"No product name found for {url}")
                return None
            
            # Extract manufacturer from product name first (it's usually the first word/brand)
            # Pumpe24 products typically have format: "Pumpe [Brand] [Model]"
            manufacturer = ""
            if product_name:
                words = product_name.split()
                # If name starts with "Pumpe", the brand is usually the second word
                if len(words) >= 2 and words[0].lower() == "pumpe":
                    manufacturer = words[1]
                # Otherwise, try first word
                elif len(words) >= 1:
                    first_word = words[0]
                    if first_word and (first_word[0].isupper() or first_word.isupper()):
                        manufacturer = first_word
            
            # Fallback: Try HTML elements if not found in name
            if not manufacturer:
                manufacturer = self._extract_text(soup, [
                    'a.product-manufacturer',
                    'span[itemprop="brand"]',
                    'div.product-brand',
                    'meta[itemprop="brand"]'
                ])
            
            # Extract category from breadcrumbs
            category = self._extract_text(soup, [
                'ul.breadcrumbs li:nth-last-child(2) a',
                'nav.breadcrumb li:nth-last-child(2) a',
                'div.breadcrumbs a:last-of-type'
            ])
            
            # Extract article number/SKU
            # Try standard selectors first
            article_number = self._extract_text(soup, [
                'div.product-info-stock-sku div.value',
                'span[itemprop="sku"]',
                'div.product-sku',
                'meta[itemprop="sku"]'
            ])
            
            # Pumpe24 specific: Look for "Artikelnummer Hersteller" in product details
            if not article_number:
                artikel_elem = soup.find(string=lambda t: t and 'Artikelnummer Hersteller' in t)
                if artikel_elem:
                    parent = artikel_elem.parent
                    if parent:
                        grandparent = parent.parent
                        if grandparent:
                            text = grandparent.get_text(strip=True)
                            # Extract number after "Artikelnummer Hersteller"
                            # Stop at: +, lowercase letter, &nbsp, capital letter followed by lowercase (like "Besonderheit")
                            import re
                            match = re.search(r'Artikelnummer\s+Hersteller\s*([A-Z0-9\-]+?)(?:\+|[a-z]|&nbsp|[A-Z][a-z]|$)', text)
                            if match:
                                article_number = match.group(1)
            
            # Extract price (gross - with VAT)
            price_gross_raw = self._extract_text(soup, [
                'span.price',
                'span[itemprop="price"]',
                'div.product-info-price span.price',
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
            
            # Extract EAN
            ean = self._extract_text(soup, [
                'span[itemprop="gtin13"]',
                'div.product-ean',
                'meta[itemprop="gtin13"]'
            ])
            
            # Extract image
            product_image = self._extract_image(soup, [
                'img.gallery-placeholder__image',
                'img[itemprop="image"]',
                'div.product-image-container img',
                'meta[property="og:image"]'
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
        price = re.sub(r'[^\d,.]', '', price_str)
        return price.strip()
    
    def run(self, max_products: int = None, concurrent_workers: int = 10) -> int:
        """Run using the bounded-concurrency logic from BaseScraper."""
        return super().run(max_products=max_products, concurrent_workers=concurrent_workers)


def main():
    """Main execution."""
    scraper = Pumpe24Scraper()
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
