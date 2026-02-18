"""
Pumpen-Heizung Scraper (HTTP only, no Selenium).
Website: https://pumpen-heizung.de
Strategy: crawl sitemap first, then fall back to homepage/category link discovery.
"""
import json
import gzip
import os
import re
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import cloudscraper

from base_scraper import BaseScraper
from config import SCRAPER_CONFIGS, SHEET_IDS
from google_sheets_helper import push_data


SCRAPER_NAME = "pumpenheizung"


class PumpenheizungScraper(BaseScraper):
    """
    Scraper for Pumpen-Heizung.de using plain HTTP requests.
    """

    SKIP_URL_PARTS = [
        "/impressum",
        "/datenschutz",
        "/agb",
        "/kontakt",
        "/widerruf",
        "/versand",
        "/zahlung",
        "/customer",
        "/account",
        "/login",
        "/register",
        "/warenkorb",
        "/checkout",
        "/wunschliste",
        "/blog",
        "/news",
        "/service",
        "/jobs",
        "/karriere",
        "/sitemap",
    ]

    def __init__(self):
        super().__init__(SCRAPER_NAME)
        self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
        self.base_url = self.config.get("base_url", "https://pumpen-heizung.de").rstrip("/")
        self.sitemap_url = self.config.get(
            "sitemap_url",
            f"{self.base_url}/sitemap.xml",
        )
        self.proxy = os.getenv("PUMPENHEIZUNG_PROXY") or self.config.get("proxy")
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
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
        if self.proxy:
            self.scraper.proxies = {"http": self.proxy, "https": self.proxy}
            self.logger.info("Using proxy for pumpenheizung requests")
        self.logger.info(f"Initialized scraper for {self.base_url}")
        self._warm_up_session()

    def _warm_up_session(self) -> None:
        warmup_urls = [self.base_url, f"{self.base_url}/robots.txt"]
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
                self.logger.debug(f"Warm-up request failed for {warmup_url}: {exc}")

    def make_request(self, url: str, method: str = "GET", **kwargs):
        headers = dict(self.request_headers)
        headers.update(kwargs.pop("headers", {}))
        attempts = kwargs.pop("attempts", 3)
        timeout = kwargs.pop("timeout", 30)

        for attempt in range(1, attempts + 1):
            try:
                if method.upper() != "GET":
                    response = self.scraper.request(
                        method.upper(),
                        url,
                        headers=headers,
                        timeout=timeout,
                        allow_redirects=True,
                        **kwargs,
                    )
                else:
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

        return None

    def _decode_sitemap_content(self, url: str, response) -> str:
        content = response.content or b""
        if not content:
            return response.text or ""

        is_gzip = url.lower().endswith(".gz") or content[:2] == b"\x1f\x8b"
        if is_gzip:
            try:
                return gzip.decompress(content).decode("utf-8", errors="ignore")
            except Exception:
                pass

        try:
            return content.decode(response.encoding or "utf-8", errors="ignore")
        except Exception:
            return response.text or ""

    def _normalize_url(self, url: str) -> str:
        if not url:
            return ""

        url = url.strip()
        if not url:
            return ""

        if url.startswith("//"):
            url = "https:" + url

        normalized = urljoin(self.base_url + "/", url)
        parsed = urlparse(normalized)

        if parsed.scheme not in ("http", "https"):
            return ""
        if "pumpen-heizung.de" not in parsed.netloc.lower():
            return ""

        clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if clean != self.base_url and clean.endswith("/"):
            clean = clean[:-1]
        return clean

    def _is_product_url(self, url: str) -> bool:
        normalized = self._normalize_url(url)
        if not normalized:
            return False

        path = urlparse(normalized).path.lower()
        if path in ("", "/"):
            return False
        if path.endswith(".xml"):
            return False

        for skip_part in self.SKIP_URL_PARTS:
            if skip_part in path:
                return False

        segments = [part for part in path.split("/") if part]
        if not segments:
            return False

        last = segments[-1]
        if last in ("index.php", "index.html", "startseite"):
            return False

        # Heuristic: product pages are usually specific slugs.
        if len(segments) == 1 and last.count("-") < 2 and not any(ch.isdigit() for ch in last):
            return False

        if len(last) < 8:
            return False

        return True

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

            sitemap_text = self._decode_sitemap_content(sitemap, response)
            soup = BeautifulSoup(sitemap_text, "xml")
            locs = [loc.get_text(strip=True) for loc in soup.find_all("loc")]

            for loc in locs:
                loc_lower = loc.lower()

                if loc_lower.endswith(".xml") or "sitemap" in loc_lower:
                    sitemap_candidate = self._normalize_url(loc)
                    if sitemap_candidate and sitemap_candidate not in visited_sitemaps:
                        queue.append(sitemap_candidate)
                    continue

                normalized = self._normalize_url(loc)
                if not normalized:
                    continue

                if self._is_product_url(normalized) and normalized not in seen_products:
                    seen_products.add(normalized)
                    product_urls.append(normalized)
                    if max_urls and len(product_urls) >= max_urls:
                        return product_urls

        return product_urls

    def _extract_internal_links(self, soup: BeautifulSoup) -> List[str]:
        links = []
        seen = set()
        for anchor in soup.select("a[href]"):
            href = anchor.get("href", "").strip()
            normalized = self._normalize_url(href)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            links.append(normalized)
        return links

    def _extract_urls_from_pages(self, max_urls: Optional[int] = None) -> List[str]:
        response = self.make_request(self.base_url)
        if not response:
            return []

        homepage = self.parse_html(response.text)
        all_links = self._extract_internal_links(homepage)

        product_urls = []
        seen_products = set()

        for link in all_links:
            if self._is_product_url(link):
                seen_products.add(link)
                product_urls.append(link)
                if max_urls and len(product_urls) >= max_urls:
                    return product_urls

        # Crawl likely category pages and pull product links from there.
        candidate_pages = []
        for link in all_links:
            if self._is_product_url(link):
                continue
            path = urlparse(link).path.lower()
            if any(skip in path for skip in self.SKIP_URL_PARTS):
                continue
            if path.count("/") > 4:
                continue
            candidate_pages.append(link)

        for page_url in candidate_pages[:40]:
            page_response = self.make_request(page_url)
            if not page_response:
                continue

            page_soup = self.parse_html(page_response.text)
            for link in self._extract_internal_links(page_soup):
                if self._is_product_url(link) and link not in seen_products:
                    seen_products.add(link)
                    product_urls.append(link)
                    if max_urls and len(product_urls) >= max_urls:
                        return product_urls

        return product_urls

    def get_product_urls(self, max_urls: int = None) -> List[str]:
        product_urls = []
        seen = set()

        self.logger.info("Fetching product URLs from sitemap...")
        sitemap_urls = self._extract_urls_from_sitemap(max_urls=max_urls)
        self.logger.info(f"Sitemap yielded {len(sitemap_urls)} candidate product URLs")

        for url in sitemap_urls:
            if url not in seen:
                seen.add(url)
                product_urls.append(url)

        # Fallback for sites where sitemap is missing/incomplete.
        if not product_urls:
            self.logger.info("Sitemap did not return product URLs. Falling back to page discovery...")
            page_urls = self._extract_urls_from_pages(max_urls=max_urls)
            for url in page_urls:
                if url not in seen:
                    seen.add(url)
                    product_urls.append(url)

        self.logger.info(f"Total product URLs found: {len(product_urls)}")
        if not product_urls and not self.proxy:
            self.logger.warning(
                "No product URLs found and no proxy configured. "
                "pumpen-heizung.de may block Render datacenter IPs. "
                "Set PUMPENHEIZUNG_PROXY to a residential/rotating proxy."
            )
        if max_urls:
            return product_urls[:max_urls]
        return product_urls

    def _extract_text(self, soup: BeautifulSoup, selectors: List[str], default: str = "") -> str:
        for selector in selectors:
            element = soup.select_one(selector)
            if not element:
                continue

            if element.name == "meta":
                value = element.get("content", "").strip()
            else:
                value = (element.get("content") or element.get_text(" ", strip=True) or "").strip()

            if value:
                return value
        return default

    def _extract_image(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        for selector in selectors:
            element = soup.select_one(selector)
            if not element:
                continue

            if element.name == "meta":
                candidate = element.get("content", "").strip()
            else:
                candidate = ""
                for attr in ("src", "data-src", "data-lazy-src", "srcset"):
                    value = element.get(attr, "")
                    if not value:
                        continue
                    if attr == "srcset":
                        value = value.split(",")[0].split()[0]
                    candidate = value.strip()
                    break

            if not candidate:
                continue

            return self._normalize_url(candidate) or candidate

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
            # Dot can be decimal separator or thousands separator.
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
                        result["price_gross"] = self._clean_price(str(price))

                return result

        return result

    def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        response = self.make_request(url)
        if not response:
            return None

        try:
            soup = self.parse_html(response.text)
            json_ld = self._extract_product_from_json_ld(soup)

            product_name = json_ld["name"] or self._extract_text(
                soup,
                [
                    "h1[itemprop='name']",
                    "h1.product-title",
                    "h1.page-title",
                    "h1",
                ],
            )
            if not product_name:
                return None

            manufacturer = json_ld["manufacturer"] or self._extract_text(
                soup,
                [
                    "[itemprop='brand'] [itemprop='name']",
                    "span[itemprop='brand']",
                    "a.product-manufacturer",
                    "meta[itemprop='brand']",
                ],
            )

            category = json_ld["category"] or self._extract_text(
                soup,
                [
                    "ul.breadcrumb li:nth-last-child(2) a",
                    "nav.breadcrumb li:nth-last-child(2) a",
                    "div.breadcrumbs a:last-of-type",
                ],
            )

            article_number = json_ld["article_number"] or self._extract_text(
                soup,
                [
                    "span[itemprop='sku']",
                    "[itemprop='mpn']",
                    "div.product-sku",
                    "meta[itemprop='sku']",
                ],
            )

            price_gross = json_ld["price_gross"]
            if not price_gross:
                price_raw = self._extract_text(
                    soup,
                    [
                        "span[itemprop='price']",
                        "meta[itemprop='price']",
                        "span.price",
                        "div.price",
                    ],
                )
                if not price_raw:
                    all_text = soup.get_text(" ", strip=True)
                    match = re.search(r"\d{1,3}(?:\.\d{3})*,\d{2}(?:\s*EUR)?", all_text)
                    if match:
                        price_raw = match.group(0)
                price_gross = self._clean_price(price_raw)

            price_net = self._calc_net_price(price_gross)

            ean = json_ld["ean"] or self._extract_text(
                soup,
                [
                    "span[itemprop='gtin13']",
                    "span[itemprop='gtin14']",
                    "meta[itemprop='gtin13']",
                    "meta[itemprop='gtin14']",
                ],
            )

            product_image = json_ld["image"] or self._extract_image(
                soup,
                [
                    "meta[property='og:image']",
                    "img[itemprop='image']",
                    "div.product-image img",
                    "img",
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
                "product_url": self._normalize_url(url) or url,
            }

        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}", exc_info=True)
            return None


def main():
    scraper = PumpenheizungScraper()
    is_production = "--production" in sys.argv
    max_products = None if is_production else 10

    if is_production:
        print("=" * 80)
        print("PRODUCTION MODE: Scraping all products")
        print("=" * 80)
    else:
        print("=" * 80)
        print("TEST MODE: Scraping first 10 products")
        print("Use --production for a full run")
        print("=" * 80)

    success_count = scraper.run(max_products=max_products, concurrent_workers=1)

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
