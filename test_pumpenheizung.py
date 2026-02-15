"""
Test Pumpenheizung Scraper
Tests the scraper with 10 products
"""
from pumpenheizung_scraper import PumpenheizungScraper

def test_pumpenheizung():
    print("=" * 80)
    print("TESTING PUMPENHEIZUNG SCRAPER")
    print("=" * 80)
    print()
    print("Note: This website is VERY slow (30+ seconds per page)")
    print("Testing with 10 products...")
    print()
    
    scraper = PumpenheizungScraper()
    count = scraper.run(max_products=10)
    
    print()
    print("=" * 80)
    print(f"RESULT: Scraped {count} products")
    print("=" * 80)
    
    if count > 0:
        print()
        print("✓ Scraper is working!")
        print(f"✓ Data saved to: data/pumpenheizung.csv")
        print()
        print("To scrape more products, run:")
        print("  python pumpenheizung_scraper.py")
    else:
        print()
        print("✗ Scraper failed - no products found")
        print("Check logs/pumpenheizung.log for details")

if __name__ == "__main__":
    test_pumpenheizung()
