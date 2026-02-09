"""
Configuration file for solar equipment scraping system.
Centralized settings for all scrapers.
"""
import os
from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CREDENTIALS_DIR = BASE_DIR / "credentials"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
CREDENTIALS_DIR.mkdir(exist_ok=True)

# ============================================================================
# GOOGLE SHEETS CONFIGURATION
# ============================================================================
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"

# Google Sheet IDs for each scraper (add your sheet IDs here)
SHEET_IDS = {
    # OLD SOLAR SCRAPERS (keeping for reference)
    "akusolar": "150WMZioC2Of6ZwICIjBc5VSFPCesXF50rWHoNJSQSxo",
    "actec": "150WMZioC2Of6ZwICIjBc5VSFPCesXF50rWHoNJSQSxo",
    "alpha": "1qOdnscsT2eEryV9RTDEUkdT_uQAsrOOHl6P-CV9bohc",
    "erneuerbar": "1qOdnscsT2eEryV9RTDEUkdT_uQAsrOOHl6P-CV9bohc",
    "czech": "1qOdnscsT2eEryV9RTDEUkdT_uQAsrOOHl6P-CV9bohc",
    "zendure": "1tTmZCl3qADSLwSVfHY81NAtASzmKOgjBD8rERsb5P1g",
    "priwatt": "1B9MAgUzNysuypwnsoAQpJxZt7BTRGac4_-WiHvRFov8",
    
    # NEW CLIENT SCRAPERS
    "meinhausshop": "1KaMWOGh9KEPvvxWQRKLu-fLr0-aSLdhn5IbdZ0XyvTQ",
    "heima24": "1nfHVN4RZM-tED-HtXUWV7bwtAWjctih7dJ2eOyTRj08",
    "sanundo": "1ygsm7nK3glzapTCoM0X7Hk3x1-xY3ieTqRCdXJN5Y8A",
    "heizungsdiscount24": "1dwls46f4xW7Td5XrV8ShvLdwsPJwQhPieH342BOEZ8o",
    "wolfonlineshop": "1IR3BAObUJf4cUxdX9OF1zka0YsOrP35c-n8F4xIl3a8",
    "st_shop24": "1inV05kOmYe53iq0ujyDafftzxZgqWVnBriRbD-BOd_k",
    "selfio": "19evdUWIJX9hLK46XYp5avvlW9KZhGayjnw6fkwn2CfE",
    "pumpe24": "1eKkepxz9FtDVQNaQmBmPfnTqTcFz7kai0dxJ0JCwuGU",
    "wasserpumpe": "1iGmt66Y4mKwC06aT0NhKzWZ8GfcCtgY0oPdYVSY4Jz4",
   
    
    # Remaining sites to implement
    "pumpen_heizung": "TBD",
    "glo24": "TBD",
    "wolf_online_shop": "11xq8HC3Fky59kFL9dU3fVfTfmUHpvwLeL1oJ9BYS004",
}

# ============================================================================
# SCRAPING CONFIGURATION
# ============================================================================

# Standard CSV columns - NEW CLIENT REQUIREMENTS
CSV_COLUMNS = [
    "manufacturer",
    "category",
    "name",
    "title",
    "article_number",
    "price_net",
    "price_gross",
    "ean",
    "product_image",
    "product_url"
]

# Request settings
REQUEST_TIMEOUT = 15  # seconds (reduced from 30)
MAX_RETRIES = 2  # reduced from 3 for faster failure handling
RETRY_DELAY = 2  # seconds between retries (reduced from 5)

# Rate limiting - OPTIMIZED FOR SPEED
# These sites can handle faster scraping since we're running at night
MIN_DELAY = 0.1  # minimum seconds between requests (reduced from 1)
MAX_DELAY = 0.3  # maximum seconds between requests (reduced from 3)

# Concurrent scraping settings
CONCURRENT_WORKERS = 10  # Number of concurrent threads per scraper (10x faster!)

# User agents for rotation (helps avoid detection)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Maximum log file size before rotation (10 MB)
MAX_LOG_SIZE = 10 * 1024 * 1024
# Number of backup log files to keep
LOG_BACKUP_COUNT = 5

# ============================================================================
# WEBSITE-SPECIFIC CONFIGURATIONS
# ============================================================================
# Add custom settings for each website here
SCRAPER_CONFIGS = {
    "akusolar": {
        "base_url": "https://www.akusolar.cz",
        "sitemap_url": "https://www.akusolar.cz/sitemap.xml",
        "requires_login": False,
        "custom_headers": {},
        "delay_override": None,
    },
    "actec": {
        "base_url": "https://www.actec-solar.de",
        "sitemap_url": "https://www.actec-solar.de/sitemap.xml",
        "requires_login": False,
        "custom_headers": {},
        "delay_override": None,
    },
    "alpha": {
        "base_url": "https://www.alpha-solar.info",
        "sitemap_url": "https://www.alpha-solar.info/sitemap.xml",
        "requires_login": True,
        "login_url": "https://www.alpha-solar.info/login",
        "login_email": "asaidani19@gmail.com",
        "login_password": "C48.AV6URhMHN4g",
        "custom_headers": {},
        "delay_override": None,
    },
    "erneuerbar": {
        "base_url": "https://erneuerbar24.de",
        "sitemap_url": "https://erneuerbar24.de/sitemap.xml",
        "requires_login": False,
        "custom_headers": {},
        "delay_override": None,
    },
    "czech": {
        "base_url": "https://shop.czech.solar",
        "sitemap_url": "https://shop.czech.solar/sitemap.xml",
        "requires_login": False,
        "custom_headers": {},
        "delay_override": None,
    },
    "zendure": {
        "base_url": "https://eu.zendure.com",
        "sitemap_url": "https://eu.zendure.com/sitemap.xml",
        "requires_login": False,
        "custom_headers": {},
        "delay_override": None,
    },
    "priwatt": {
        "base_url": "https://priwatt.de",
        "sitemap_url": "https://priwatt.de/sitemap.xml",
        "requires_login": True,
        "custom_headers": {},
        "delay_override": None,
    },
    
    # NEW CLIENT WEBSITES
    "meinhausshop": {
        "base_url": "https://www.meinhausshop.de",
        "sitemap_url": "https://meinhausshop.de/sitemap.xml",
        "requires_login": False,
        "platform": "Shopware",
        "custom_headers": {},
        "delay_override": None,
    },
    "heima24": {
        "base_url": "https://www.heima24.de",
        "sitemap_url": "https://heima24.de/sitemap.xml",
        "requires_login": False,
        "platform": "Custom",
        "custom_headers": {},
        "delay_override": None,
    },
    "sanundo": {
        "base_url": "https://sanundo.de",
        "sitemap_url": "https://sanundo.de/sitemap.xml",
        "requires_login": False,
        "platform": "Shopware",
        "custom_headers": {},
        "delay_override": None,
    },
    "heizungsdiscount24": {
        "base_url": "https://www.heizungsdiscount24.de",
        "sitemap_url": "https://www.heizungsdiscount24.de/sitemap.xml",
        "requires_login": False,
        "platform": "JTL-Shop",
        "custom_headers": {},
        "delay_override": None,
    },
    "st_shop24": {
        "base_url": "https://st-shop24.de",
        "sitemap_url": "https://st-shop24.de/sitemap.xml",
        "requires_login": False,
        "platform": "Magento",
        "custom_headers": {},
        "delay_override": None,
    },
    "st_shop24": {
        "base_url": "https://st-shop24.de",
        "sitemap_url": "https://st-shop24.de/sitemap.xml",
        "requires_login": False,
        "platform": "Magento",
        "custom_headers": {},
        "delay_override": None,
    },
    "wolfonlineshop": {
        "base_url": "https://www.heat-store.de",
        "sitemap_url": "https://www.heat-store.de/sitemap.xml",
        "requires_login": False,
        "platform": "Shopware 6",
        "custom_headers": {},
        "delay_override": None,
    },
    "selfio": {
        "base_url": "https://www.selfio.de",
        "sitemap_url": "https://www.selfio.de/sitemap.xml",
        "requires_login": False,
        "platform": "Shopware 6",
        "custom_headers": {},
        "delay_override": None,
    },
    "pumpe24": {
        "base_url": "https://www.pumpe24.de",
        "sitemap_url": "https://www.pumpe24.de/sitemap.xml",
        "requires_login": False,
        "platform": "Magento (Cloudflare protected - uses cloudscraper)",
        "custom_headers": {},
        "delay_override": None,
    },
    "wasserpumpe": {
        "base_url": "https://wasserpumpe.de",
        "sitemap_url": "https://wasserpumpe.de/sitemap.xml",
        "requires_login": False,
        "platform": "Magento (Cloudflare protected - uses cloudscraper)",
        "custom_headers": {},
        "delay_override": None,
    },
    "glo24": {
        "base_url": "https://glo24.de",
        "sitemap_url": "https://glo24.de/sitemap.xml",
        "requires_login": False,
        "platform": "Unknown (Cloudflare protected - uses cloudscraper)",
        "custom_headers": {},
        "delay_override": None,
        # German VPN/Proxy configuration (required - site only accessible from Germany)
        # Options:
        # 1. HTTP/HTTPS proxy: "http://username:password@proxy-server:port"
        # 2. SOCKS5 proxy: "socks5://username:password@proxy-server:port"
        # Example: "proxy": "http://user:pass@de-proxy.example.com:8080"
        "proxy": None,  # Set your German proxy here
    },
    "wolf_online_shop": {
        "base_url": "https://www.wolf-online-shop.de",
        "sitemap_url": "https://www.wolf-online-shop.de/sitemap.xml",
        "requires_login": False,
        "platform": "Custom (Heating/HVAC parts shop - Cloudflare protected)",
        "custom_headers": {},
        "delay_override": None,
    },
}

# ============================================================================
# ENVIRONMENT-SPECIFIC SETTINGS
# ============================================================================
# Set to True when running on production server
IS_PRODUCTION = os.getenv("SCRAPER_ENV", "development") == "production"

# Email notifications (optional - for production alerts)
ENABLE_EMAIL_ALERTS = False
ALERT_EMAIL = "your-email@example.com"
