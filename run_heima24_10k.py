"""
Run heima24 scraper with 10,000 products limit
"""
import sys
from heima24_scraper import Heima24Scraper


def main():
    """Run heima24 scraper with 10k limit."""
    print("="*60)
    print("Running heima24 scraper - 10,000 products")
    print("="*60)
    
    scraper = Heima24Scraper()
    
    # Override max_products
    scraper.max_products = 10000
    
    # Run scraper
    success_count = scraper.run()
    
    print(f"\n{'='*60}")
    print(f"Completed: {success_count} products scraped")
    print(f"Output: {scraper.get_output_file()}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
