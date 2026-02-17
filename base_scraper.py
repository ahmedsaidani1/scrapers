"""
Base scraper class for solar equipment price scraping.
All individual scrapers should inherit from this class.
"""
import csv
import os
import time
import random
import logging
import requests
from pathlib import Path
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup   
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter

from config import (
    DATA_DIR, LOGS_DIR, CSV_COLUMNS, REQUEST_TIMEOUT,
    MAX_RETRIES, RETRY_DELAY, MIN_DELAY, MAX_DELAY,
    USER_AGENTS, LOG_FORMAT, LOG_DATE_FORMAT,
    MAX_LOG_SIZE, LOG_BACKUP_COUNT, LOG_LEVEL
)


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    
    Provides common functionality:
    - HTTP requests with retry logic
    - Rate limiting
    - User agent rotation
    - CSV output
    - Logging
    - Error handling
    
    To create a new scraper:
    1. Inherit from this class
    2. Implement get_product_urls() method
    3. Implement scrape_product() method
    4. Optionally override other methods for custom behavior
    """
    
    def __init__(self, scraper_name: str):
        """
        Initialize base scraper.
        
        Args:
            scraper_name: Unique name for this scraper (e.g., "priwatt")
        """
        self.scraper_name = scraper_name
        self.session = requests.Session()

        # Per-job tuning knobs (useful for very large scrapes on dedicated cron jobs).
        self.request_timeout = float(os.getenv("SCRAPER_REQUEST_TIMEOUT", REQUEST_TIMEOUT))
        self.max_retries = max(int(os.getenv("SCRAPER_MAX_RETRIES", MAX_RETRIES)), 1)
        self.retry_delay = float(os.getenv("SCRAPER_RETRY_DELAY", RETRY_DELAY))
        self.scrape_min_delay = float(os.getenv("SCRAPER_MIN_DELAY", 0.01))
        self.scrape_max_delay = float(os.getenv("SCRAPER_MAX_DELAY", 0.05))
        if self.scrape_max_delay < self.scrape_min_delay:
            self.scrape_min_delay, self.scrape_max_delay = self.scrape_max_delay, self.scrape_min_delay

        pool_connections = max(int(os.getenv("SCRAPER_HTTP_POOL_CONNECTIONS", "100")), 10)
        pool_maxsize = max(int(os.getenv("SCRAPER_HTTP_POOL_MAXSIZE", "100")), 10)
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=0,
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.output_file = DATA_DIR / f"{scraper_name}.csv"
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize CSV file with headers
        self._initialize_csv()
        
        self.logger.info(f"Initialized {scraper_name} scraper")
    
    def _setup_logging(self) -> logging.Logger:
        """
        Setup logging with rotating file handler.
        
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(self.scraper_name)
        logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # File handler with rotation
        log_file = LOGS_DIR / f"{self.scraper_name}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=MAX_LOG_SIZE,
            backupCount=LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(
            logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        )
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _initialize_csv(self) -> None:
        """Initialize CSV file with standard headers."""
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                writer.writeheader()
            self.logger.debug(f"Initialized CSV file: {self.output_file}")
        except Exception as e:
            self.logger.error(f"Failed to initialize CSV: {e}")
            raise
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent from the pool."""
        return random.choice(USER_AGENTS)
    
    def _random_delay(self) -> None:
        """Add random delay between requests to be respectful."""
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        time.sleep(delay)
    
    def make_request(
        self,
        url: str,
        method: str = "GET",
        **kwargs
    ) -> Optional[requests.Response]:
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional arguments for requests
        
        Returns:
            Response object if successful, None otherwise
        """
        headers = kwargs.pop('headers', {})
        headers['User-Agent'] = self._get_random_user_agent()
        timeout = kwargs.pop("timeout", self.request_timeout)
        
        # Disable SSL verification if needed (for sites with expired certs)
        verify_ssl = kwargs.pop('verify', True)
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method,
                    url,
                    headers=headers,
                    timeout=timeout,
                    verify=verify_ssl,
                    **kwargs
                )
                response.raise_for_status()
                
                self.logger.debug(f"Successfully fetched: {url}")
                return response
                
            except requests.exceptions.HTTPError as e:
                self.logger.warning(
                    f"HTTP error {e.response.status_code} for {url} "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )
                
                # Don't retry on 404 or 403
                if e.response.status_code in [404, 403]:
                    return None
                    
            except requests.exceptions.Timeout:
                self.logger.warning(
                    f"Timeout for {url} (attempt {attempt + 1}/{self.max_retries})"
                )
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(
                    f"Request failed for {url}: {e} "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )
            
            # Wait before retrying
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        self.logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content with BeautifulSoup.
        
        Args:
            html: HTML string to parse
        
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'html.parser')
    
    def _map_product_row(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map arbitrary scraper keys to canonical CSV columns.
        """

        def pick(*keys):
            for key in keys:
                value = product_data.get(key)
                if value is not None and str(value).strip() != "":
                    return value
            return ""

        row = {
            "Hersteller": pick("Hersteller", "manufacturer", "brand"),
            "Kategorie": pick("Kategorie", "category"),
            "Name": pick("Name", "name", "Titel", "title"),
            "Titel": pick("Titel", "title", "Name", "name"),
            "Artikelnummer": pick("Artikelnummer", "article_number", "sku", "mpn"),
            "Preis_Netto": pick("Preis_Netto", "price_net"),
            "Preis_Brutto": pick("Preis_Brutto", "price_gross"),
            "EAN": pick("EAN", "ean", "gtin13", "gtin"),
            "Produktbild": pick("Produktbild", "product_image", "image", "image_url"),
            "Produkt_URL": pick("Produkt_URL", "product_url", "url", "link"),
        }

        # Keep strict column order and include any future columns as empty by default.
        return {col: row.get(col, "") for col in CSV_COLUMNS}

    def save_product(self, product_data: Dict[str, Any]) -> None:
        """
        Save one product row.
        """
        self.save_products([product_data])

    def save_products(self, products: List[Dict[str, Any]]) -> None:
        """
        Save multiple product rows in one append operation.
        """
        if not products:
            return
        try:
            rows = [self._map_product_row(product_data) for product_data in products]
            with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                writer.writerows(rows)
            self.logger.debug(f"Saved {len(rows)} products")
        except Exception as e:
            self.logger.error(f"Failed to save products batch: {e}")
    
    @abstractmethod
    def get_product_urls(self) -> List[str]:
        """
        Get list of product URLs to scrape.
        
        This method MUST be implemented by each scraper.
        
        Common approaches:
        - Parse sitemap.xml
        - Scrape category pages
        - Use API endpoints
        
        Returns:
            List of product URLs
        """
        pass
    
    @abstractmethod
    def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single product page.
        
        This method MUST be implemented by each scraper.
        
        Args:
            url: Product page URL
        
        Returns:
            Dictionary with product data matching CSV_COLUMNS structure:
            {
                'product_name': str,
                'sku': str,
                'category': str,
                'price': str,
                'availability': str,
                'description': str,
                'product_image': str,
                'product_url': str
            }
            
            Return None if scraping fails.
        """
        pass
    
    def run(self, max_products: Optional[int] = None, concurrent_workers: int = 10) -> int:
        """
        Main execution method - runs the complete scraping process.
        
        Args:
            max_products: Maximum number of products to scrape (None for all)
            concurrent_workers: Number of concurrent threads for scraping (default: 10)
        
        Returns:
            Number of products successfully scraped
        """
        self.logger.info(f"Starting {self.scraper_name} scraper")
        start_time = time.time()
        
        try:
            # Get product URLs
            self.logger.info("Fetching product URLs...")
            product_urls = self.get_product_urls()
            
            # Limit products if specified
            if max_products and max_products < len(product_urls):
                product_urls = product_urls[:max_products]
                self.logger.info(f"Limited to first {max_products} products")
            
            self.logger.info(f"Found {len(product_urls)} products to scrape")
            
            if not product_urls:
                self.logger.warning("No product URLs found")
                return 0
            
            # Scrape products concurrently with bounded in-flight futures.
            # This avoids creating one Future per URL (large memory spike).
            success_count = 0
            processed_count = 0
            total_products = len(product_urls)
            max_in_flight = max(concurrent_workers * 4, concurrent_workers)
            csv_buffer_size = max(int(os.getenv("SCRAPER_CSV_BUFFER_SIZE", "250")), 1)
            output_buffer: List[Dict[str, Any]] = []

            with ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
                url_iter = iter(product_urls)
                future_to_url = {}

                # Prime queue
                for _ in range(max_in_flight):
                    try:
                        url = next(url_iter)
                    except StopIteration:
                        break
                    future_to_url[executor.submit(self._scrape_with_retry, url)] = url

                while future_to_url:
                    # Process one completed future at a time, then refill queue
                    future = next(as_completed(future_to_url))
                    url = future_to_url.pop(future)
                    processed_count += 1

                    if processed_count % 100 == 0:
                        self.logger.info(
                            f"Progress: {processed_count}/{total_products} products processed"
                        )

                    try:
                        product_data = future.result()

                        if product_data:
                            output_buffer.append(product_data)
                            if len(output_buffer) >= csv_buffer_size:
                                self.save_products(output_buffer)
                                output_buffer = []
                            success_count += 1
                        else:
                            self.logger.warning(f"No data extracted from {url}")

                    except Exception as e:
                        self.logger.error(f"Error processing {url}: {e}")

                    try:
                        next_url = next(url_iter)
                        future_to_url[executor.submit(self._scrape_with_retry, next_url)] = next_url
                    except StopIteration:
                        pass

            if output_buffer:
                self.save_products(output_buffer)
            
            # Summary
            elapsed_time = time.time() - start_time
            self.logger.info(
                f"Scraping completed: {success_count}/{total_products} products "
                f"in {elapsed_time:.2f} seconds ({success_count/elapsed_time:.1f} products/sec)"
            )
            
            return success_count
            
        except Exception as e:
            self.logger.error(f"Scraper failed: {e}", exc_info=True)
            return 0
        
        finally:
            self.session.close()
    
    def _scrape_with_retry(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single product with minimal delay (for concurrent execution).
        
        Args:
            url: Product URL to scrape
        
        Returns:
            Product data dictionary or None
        """
        try:
            # Small random delay to avoid hammering the server.
            if self.scrape_max_delay > 0:
                time.sleep(random.uniform(self.scrape_min_delay, self.scrape_max_delay))
            return self.scrape_product(url)
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None
    
    def get_output_file(self) -> Path:
        """Get path to output CSV file."""
        return self.output_file
