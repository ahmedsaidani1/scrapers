"""
Wasserpumpe Scraper (HTTP only, no Selenium).
Website: https://wasserpumpe.de
Strategy: sitemap-first discovery with category fallback, then parse product pages
with JSON-LD + HTML selectors.
"""
import json
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import cloudscraper

from base_scraper import BaseScraper
from config import SCRAPER_CONFIGS, SHEET_IDS
from google_sheets_helper import push_data


SCRAPER_NAME = "wasserpumpe"


class WasserpumpeScraper(BaseScraper):
    """
    Scraper for Wasserpumpe.de using cloudscraper and plain HTTP parsing.
    """

    SKIP_PATH_PARTS = [
        "/rechtliches",
        "/datenschutz",
        "/impressum",
        "/uber-uns",
        "/allgemeine-geschaftsbedingungen",
        "/review-policy",
        "/bestsellers",
        "/kundenservice",
        "/blog",
        "/kontakt",
        "/login",
        "/typ-wasserpumpe",
        "/winter-deals",
        "b2b.wasserpumpe",
        "/lieferung",
        "/wahlhilfe",
        "/pumpenkonfigurator",
        "/zubehoer",
        "/warenkorb",
        "/checkout",
        "/wishlist",
        "/account",
        "/cart",
        "/media/",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".pdf",
        # Category pages that look like products
        "dab-evosta-2-umwaelzpumpe",
        "grundfos-alpha-2",
        "wilo-yonos-pico",
    ]

    def __init__(self):
        super().__init__(SCRAPER_NAME)

        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://wasserpumpe.de").rstrip("/")
        self.sitemap_url = self.config.get("sitemap_url", f"{self.base_url}/sitemap.xml")
        self.proxy = os.getenv("WASSERPUMPE_PROXY") or self.config.get("proxy")

        self.request_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

        self.scraper = cloudscraper.create_scraper(
            browser={
                "browser": "chrome",
                "platform": "windows",
                "mobile": False,
            }
        )
        if self.proxy:
            self.scraper.proxies = {
                "http": self.proxy,
                "https": self.proxy,
            }
            self.logger.info("Using proxy for wasserpumpe requests")

        self.category_urls = [
            f"{self.base_url}/tauchpumpe",
            f"{self.base_url}/gartenpumpe",
            f"{self.base_url}/hauswasserwerk",
        ]

        self.logger.info(f"Initialized HTTP scraper for {self.base_url}")
        self._warm_up_session()

    def _warm_up_session(self) -> None:
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
                if response.status_code != 403:
                    return
            except Exception as exc:
                self.logger.debug(f"Warm-up failed for {warmup_url}: {exc}")

    def make_request(self, url: str, **kwargs):
        headers = dict(self.request_headers)
        headers.update(kwargs.pop("headers", {}))

        attempts = kwargs.pop("attempts", 3)
        timeout = kwargs.pop("timeout", 35)

        for attempt in range(1, attempts + 1):
            try:
                response = self.scraper.get(
                    url,
                    headers=headers,
                    timeout=timeout,
                    allow_redirects=True,
                    **kwargs,
                )
                if response.status_code == 403:
                    self.logger.warning(f"403 for {url} (attempt {attempt}/{attempts})")
                    self._warm_up_session()
                    time.sleep(1.5 * attempt)
                    continue

                response.raise_for_status()
                return response
            except Exception as exc:
                if attempt == attempts:
                    self.logger.error(f"Request failed for {url}: {exc}")
                else:
                    self.logger.warning(
                        f"Retrying {url} after error (attempt {attempt}/{attempts}): {exc}"
                    )
                    time.sleep(1.0 * attempt)

        return None

    def _normalize_url(self, raw_url: str) -> str:
        if not raw_url:
            return ""

        candidate = raw_url.strip()
        if not candidate:
            return ""

        if candidate.startswith("//"):
            candidate = "https:" + candidate

        normalized = urljoin(self.base_url + "/", candidate)
        parsed = urlparse(normalized)

        if parsed.scheme not in ("http", "https"):
            return ""
        if "wasserpumpe.de" not in parsed.netloc.lower():
            return ""

        clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if clean != self.base_url and clean.endswith("/"):
            clean = clean[:-1]
        return clean

    def _is_product_url(self, raw_url: str) -> bool:
        url = self._normalize_url(raw_url)
        if not url:
            return False

        path = urlparse(url).path.lower()
        if path in ("", "/"):
            return False

        if path in ("/tauchpumpe", "/gartenpumpe", "/hauswasserwerk"):
            return False

        if path.endswith(".xml") or "sitemap" in path:
            return False

        for skip_part in self.SKIP_PATH_PARTS:
            if skip_part in path:
                return False

        slug = path.strip("/").split("/")[-1]
        
        # Product URLs must be long and specific
        if len(slug) < 20:
            return False
            
        # Must have at least 3 hyphens (brand-model-details)
        if slug.count("-") < 3:
            return False
            
        # Must contain digits (model numbers)
        if not any(ch.isdigit() for ch in slug):
            return False
        
        # Must contain a known brand name (case insensitive)
        known_brands = [
            'dab', 'grundfos', 'wilo', 'espa', 'ebara', 'pedrollo', 
            'lowara', 'calpeda', 'leo', 'metabo', 'gardena', 'einhell',
            'kärcher', 'karcher', 'trotec', 'güde', 'gude', 'al-ko', 'alko'
        ]
        slug_lower = slug.lower()
        has_brand = any(brand in slug_lower for brand in known_brands)
        
        if not has_brand:
            return False

        return True

    def _extract_urls_from_text(self, text: str) -> List[str]:
        if not text:
            return []

        matches = re.findall(
            r"https?://(?:www\.)?wasserpumpe\.de/[a-zA-Z0-9\-/]+",
            text,
        )
        product_urls = []
        seen = set()
        for match in matches:
            url = self._normalize_url(match)
            if url and self._is_product_url(url) and url not in seen:
                seen.add(url)
                product_urls.append(url)
        return product_urls

    def _extract_urls_from_sitemap(self, max_urls: Optional[int] = None) -> List[str]:
        product_urls = []
        seen_products = set()
        visited_sitemaps = set()
        queue = [self.sitemap_url]
        max_sitemaps = 120

        while queue and len(visited_sitemaps) < max_sitemaps:
            sitemap = queue.pop(0)
            if sitemap in visited_sitemaps:
                continue
            visited_sitemaps.add(sitemap)

            response = self.make_request(sitemap, attempts=2, timeout=30)
            if not response:
                continue

            soup = BeautifulSoup(response.text, "xml")
            locs = [loc.get_text(strip=True) for loc in soup.find_all("loc")]

            for loc in locs:
                loc_lower = loc.lower()

                if loc_lower.endswith(".xml") or "sitemap" in loc_lower:
                    next_sitemap = self._normalize_url(loc)
                    if next_sitemap and next_sitemap not in visited_sitemaps:
                        queue.append(next_sitemap)
                    continue

                url = self._normalize_url(loc)
                if not url:
                    continue

                if self._is_product_url(url) and url not in seen_products:
                    seen_products.add(url)
                    product_urls.append(url)
                    if max_urls and len(product_urls) >= max_urls:
                        return product_urls

        return product_urls

    def _extract_urls_from_categories(self, max_urls: Optional[int] = None) -> List[str]:
        product_urls = []
        seen = set()

        for idx, category_url in enumerate(self.category_urls, 1):
            self.logger.info(
                f"[{idx}/{len(self.category_urls)}] Scraping category: {category_url}"
            )
            response = self.make_request(category_url, attempts=3, timeout=35)
            if not response:
                continue

            soup = self.parse_html(response.text)

            for anchor in soup.select("a[href]"):
                href = anchor.get("href", "")
                url = self._normalize_url(href)
                if url and self._is_product_url(url) and url not in seen:
                    seen.add(url)
                    product_urls.append(url)

            # Extra fallback: parse URLs from embedded scripts/text.
            if len(product_urls) < 10:
                script_urls = self._extract_urls_from_text(response.text)
                for url in script_urls:
                    if url not in seen:
                        seen.add(url)
                        product_urls.append(url)

            self.logger.info(
                f"  Category yielded {len(product_urls)} product URLs total"
            )

            if max_urls and len(product_urls) >= max_urls:
                return product_urls[:max_urls]

            time.sleep(1.2)

        return product_urls

    def get_product_urls(self, max_urls: int = None) -> List[str]:
        all_urls = []
        seen = set()

        self.logger.info("Fetching product URLs from sitemap...")
        sitemap_urls = self._extract_urls_from_sitemap(max_urls=max_urls)
        self.logger.info(f"Sitemap found {len(sitemap_urls)} candidate product URLs")

        for url in sitemap_urls:
            if url not in seen:
                seen.add(url)
                all_urls.append(url)

        # Category fallback if sitemap is blocked/incomplete.
        if len(all_urls) < 40:
            self.logger.info(
                f"Low URL count ({len(all_urls)}). Trying category-based discovery..."
            )
            category_urls = self._extract_urls_from_categories(max_urls=max_urls)
            for url in category_urls:
                if url not in seen:
                    seen.add(url)
                    all_urls.append(url)
                    if max_urls and len(all_urls) >= max_urls:
                        break

        self.logger.info(f"Total product URLs found: {len(all_urls)}")
        if max_urls:
            return all_urls[:max_urls]
        return all_urls

    def _extract_text(self, soup: BeautifulSoup, selectors: List[str], default: str = "") -> str:
        for selector in selectors:
            element = soup.select_one(selector)
            if not element:
                continue

            if element.name == "meta":
                value = (element.get("content") or "").strip()
            else:
                value = element.get_text(" ", strip=True).strip()

            if value:
                return value

        return default

    def _extract_image(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        for selector in selectors:
            element = soup.select_one(selector)
            if not element:
                continue

            if element.name == "meta":
                candidate = (element.get("content") or "").strip()
            else:
                candidate = ""
                for attr in ("src", "data-src", "data-lazy-src", "srcset"):
                    value = (element.get(attr) or "").strip()
                    if not value:
                        continue
                    if attr == "srcset":
                        value = value.split(",")[0].split()[0]
                    candidate = value
                    break

            if not candidate:
                continue

            if candidate.startswith("//"):
                return "https:" + candidate
            if candidate.startswith("/"):
                return self.base_url + candidate
            return candidate

        return ""

    def _clean_price(self, raw_price: str) -> str:
        if not raw_price:
            return ""

        text = str(raw_price).replace("\xa0", " ").strip()
        matches = re.findall(r"\d{1,3}(?:[.\s]\d{3})*(?:,\d+)?|\d+(?:[.,]\d+)?", text)
        if not matches:
            return ""

        candidate = matches[-1].replace(" ", "")

        if "," in candidate and "." in candidate:
            if candidate.rfind(",") > candidate.rfind("."):
                normalized = candidate.replace(".", "").replace(",", ".")
            else:
                normalized = candidate.replace(",", "")
        elif "," in candidate:
            normalized = candidate.replace(".", "").replace(",", ".")
        else:
            if candidate.count(".") > 1:
                normalized = candidate.replace(".", "")
            else:
                normalized = candidate

        try:
            value = float(normalized)
            return f"{value:.2f}".replace(".", ",")
        except ValueError:
            return ""

    def _calc_net_price(self, gross_price: str) -> str:
        if not gross_price:
            return ""
        try:
            gross = float(gross_price.replace(".", "").replace(",", "."))
            net = gross / 1.19
            return f"{net:.2f}".replace(".", ",")
        except ValueError:
            return ""

    def _extract_product_from_json_ld(self, soup: BeautifulSoup) -> Dict[str, str]:
        result = {
            "name": "",
            "manufacturer": "",
            "article_number": "",
            "price_gross": "",
            "ean": "",
            "image": "",
            "category": "",
        }

        scripts = soup.find_all("script", {"type": "application/ld+json"})
        for script in scripts:
            raw = script.string or script.get_text(strip=True)
            if not raw:
                continue

            try:
                payload = json.loads(raw)
            except Exception:
                continue

            candidates = []
            if isinstance(payload, dict):
                candidates.append(payload)
                graph = payload.get("@graph")
                if isinstance(graph, list):
                    candidates.extend(item for item in graph if isinstance(item, dict))
            elif isinstance(payload, list):
                candidates.extend(item for item in payload if isinstance(item, dict))

            for item in candidates:
                type_value = item.get("@type", "")
                if isinstance(type_value, list):
                    is_product = any(str(t).lower() == "product" for t in type_value)
                else:
                    is_product = str(type_value).lower() == "product"

                if not is_product:
                    continue

                name = item.get("name")
                if isinstance(name, str):
                    result["name"] = name.strip()

                brand = item.get("brand")
                if isinstance(brand, dict):
                    result["manufacturer"] = str(brand.get("name", "")).strip()
                elif isinstance(brand, str):
                    result["manufacturer"] = brand.strip()

                result["article_number"] = str(
                    item.get("sku") or item.get("mpn") or item.get("productID") or ""
                ).strip()

                result["ean"] = str(
                    item.get("gtin13")
                    or item.get("gtin14")
                    or item.get("gtin12")
                    or item.get("gtin8")
                    or ""
                ).strip()

                image = item.get("image")
                if isinstance(image, list) and image:
                    result["image"] = str(image[0]).strip()
                elif isinstance(image, str):
                    result["image"] = image.strip()

                result["category"] = str(item.get("category", "")).strip()

                offers = item.get("offers")
                if isinstance(offers, list) and offers:
                    offers = offers[0]
                if isinstance(offers, dict):
                    price = offers.get("price")
                    if price is not None:
                        # Price from JSON-LD is already in correct format (e.g., "369.00")
                        # Just convert to German format
                        try:
                            price_float = float(str(price))
                            result["price_gross"] = f"{price_float:.2f}".replace(".", ",")
                        except (ValueError, TypeError):
                            result["price_gross"] = self._clean_price(str(price))

                return result

        return result

    def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        response = self.make_request(url, attempts=3, timeout=35)
        if not response:
            return None

        try:
            soup = self.parse_html(response.text)
            json_ld = self._extract_product_from_json_ld(soup)

            product_name = json_ld["name"] or self._extract_text(
                soup,
                [
                    "h1.page-title span",
                    "h1.product-name",
                    "h1[itemprop='name']",
                    "h1",
                ],
            )
            if not product_name:
                return None

            # Extract manufacturer from product name first (it's usually the first word/brand)
            manufacturer = ""
            if product_name:
                first_word = product_name.split()[0] if product_name.split() else ""
                # Check if first word looks like a manufacturer (capitalized, not a common word)
                if first_word and (first_word[0].isupper() or first_word.isupper()):
                    manufacturer = first_word
            
            # Fallback: Try JSON-LD or HTML elements if not found in name
            if not manufacturer:
                manufacturer = json_ld["manufacturer"] or self._extract_text(
                    soup,
                    [
                        "a.product-manufacturer",
                        "span[itemprop='brand']",
                        "div.product-brand",
                        "meta[itemprop='brand']",
                        "[itemprop='brand'] [itemprop='name']",
                    ],
                )

            category = json_ld["category"] or self._extract_text(
                soup,
                [
                    "ul.breadcrumbs li:nth-last-child(2) a",
                    "nav.breadcrumb li:nth-last-child(2) a",
                    "div.breadcrumbs a:last-of-type",
                ],
            )

            article_number = json_ld["article_number"] or self._extract_text(
                soup,
                [
                    "div.product-info-stock-sku div.value",
                    "span[itemprop='sku']",
                    "div.product-sku",
                    "meta[itemprop='sku']",
                    "[itemprop='sku']",
                ],
            )

            price_gross = json_ld["price_gross"]
            if not price_gross:
                price_raw = self._extract_text(
                    soup,
                    [
                        "span.price",
                        "span[itemprop='price']",
                        "div.product-info-price span.price",
                        "meta[itemprop='price']",
                    ],
                )
                if not price_raw:
                    match = re.search(r"\d{1,3}(?:\.\d{3})*,\d{2}(?:\s*EUR)?", response.text)
                    if match:
                        price_raw = match.group(0)
                price_gross = self._clean_price(price_raw)

            price_net = self._calc_net_price(price_gross)

            ean = json_ld["ean"] or self._extract_text(
                soup,
                [
                    "span[itemprop='gtin13']",
                    "span[itemprop='gtin14']",
                    "div.product-ean",
                    "meta[itemprop='gtin13']",
                    "meta[itemprop='gtin14']",
                ],
            )

            product_image = json_ld["image"] or self._extract_image(
                soup,
                [
                    "meta[property='og:image']",
                    "img.gallery-placeholder__image",
                    "img[itemprop='image']",
                    "div.product-image-container img",
                ],
            )

            return {
                "manufacturer": manufacturer,
                "category": category,
                "name": product_name,
                "title": product_name,
                "article_number": article_number,
                "price_net": price_net,
                "price_gross": price_gross,
                "ean": ean,
                "product_image": product_image,
                "product_url": url,
            }

        except Exception as exc:
            self.logger.error(f"Error scraping {url}: {exc}", exc_info=True)
            return None


def main():
    scraper = WasserpumpeScraper()
    success_count = scraper.run()

    if "--push-to-sheets" in sys.argv and success_count > 0:
        sheet_id = SHEET_IDS.get(SCRAPER_NAME)
        if sheet_id and sheet_id != "TBD":
            print("\nPushing data to Google Sheets...")
            if push_data(sheet_id, scraper.get_output_file()):
                print("Successfully pushed to Google Sheets")
            else:
                print("Failed to push to Google Sheets")
        else:
            print(f"\nNo Google Sheet ID configured for {SCRAPER_NAME}")

    print(f"\n{'=' * 60}")
    print(f"Completed: {success_count} products scraped")
    print(f"Output: {scraper.get_output_file()}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
