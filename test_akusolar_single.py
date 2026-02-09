"""Quick test to scrape one Akusolar product"""
from akusolar_scraper import AkusolarScraper

# Test with the one product we found
scraper = AkusolarScraper()

test_url = "https://www.eshop.akusolar.cz/fotovoltaicky-panel-et-solar-450-144-m-hf-cerny-ram-35-mm-svt-31-629"

print(f"Testing scraper with: {test_url}\n")

product_data = scraper.scrape_product(test_url)

if product_data:
    print("✓ Successfully scraped product!")
    print("\nProduct Data:")
    print("="*60)
    for key, value in product_data.items():
        print(f"{key}: {value[:100] if isinstance(value, str) and len(value) > 100 else value}")
    print("="*60)
    
    # Save it
    scraper.save_product(product_data)
    print(f"\n✓ Saved to: {scraper.get_output_file()}")
else:
    print("✗ Failed to scrape product")
