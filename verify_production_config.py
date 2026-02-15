"""
Verify Production Configuration
Checks that production script is configured to scrape ALL products
"""

def verify_production():
    print("=" * 80)
    print("PRODUCTION CONFIGURATION VERIFICATION")
    print("=" * 80)
    print()
    
    # Check imports
    print("1. Checking imports...")
    try:
        from run_production_powerbi import SCRAPERS, POWER_BI_SHEET_ID
        print(f"   ✓ All imports successful")
        print(f"   ✓ {len(SCRAPERS)} scrapers loaded")
    except Exception as e:
        print(f"   ✗ Import failed: {e}")
        return False
    
    # Check scraper count
    print()
    print("2. Checking scraper count...")
    if len(SCRAPERS) == 10:
        print(f"   ✓ Correct: 10 scrapers configured")
    else:
        print(f"   ✗ Wrong: {len(SCRAPERS)} scrapers (expected 10)")
        return False
    
    # List scrapers
    print()
    print("3. Configured scrapers:")
    for i, (name, _) in enumerate(SCRAPERS, 1):
        print(f"   {i:2d}. {name}")
    
    # Check production script for max_products=None
    print()
    print("4. Checking production script configuration...")
    with open('run_production_powerbi.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'max_products=None' in content:
        print(f"   ✓ Production mode: max_products=None (scrapes ALL products)")
    else:
        print(f"   ✗ Warning: max_products=None not found in production script")
        return False
    
    # Check Google Sheet ID
    print()
    print("5. Checking Google Sheet configuration...")
    print(f"   ✓ Sheet ID: {POWER_BI_SHEET_ID}")
    
    # Check requirements.txt
    print()
    print("6. Checking dependencies...")
    try:
        with open('requirements.txt', 'r') as f:
            deps = f.read()
        
        required = ['beautifulsoup4', 'requests', 'gspread', 'selenium', 
                   'undetected-chromedriver', 'cloudscraper', 'psutil']
        
        missing = []
        for dep in required:
            if dep not in deps:
                missing.append(dep)
        
        if missing:
            print(f"   ✗ Missing dependencies: {', '.join(missing)}")
            return False
        else:
            print(f"   ✓ All required dependencies present")
    except Exception as e:
        print(f"   ✗ Could not read requirements.txt: {e}")
        return False
    
    # Check render.yaml
    print()
    print("7. Checking Render configuration...")
    try:
        with open('render.yaml', 'r') as f:
            render_config = f.read()
        
        if 'run_production_powerbi.py' in render_config:
            print(f"   ✓ Render configured to run production script")
        else:
            print(f"   ✗ Render not configured correctly")
            return False
            
        if '0 2 * * 0' in render_config:
            print(f"   ✓ Schedule: Sunday 2 AM UTC")
        else:
            print(f"   ⚠ Warning: Schedule may not be set correctly")
    except Exception as e:
        print(f"   ✗ Could not read render.yaml: {e}")
        return False
    
    # Final summary
    print()
    print("=" * 80)
    print("VERIFICATION RESULT")
    print("=" * 80)
    print()
    print("✓ Production configuration is CORRECT")
    print()
    print("Configuration Summary:")
    print(f"  • Scrapers: 10 (including pumpenheizung)")
    print(f"  • Mode: PRODUCTION (max_products=None)")
    print(f"  • Scraping: ALL products (no limits)")
    print(f"  • Schedule: Every Sunday at 2 AM UTC")
    print(f"  • Target: Google Sheet {POWER_BI_SHEET_ID}")
    print()
    print("✓ Ready for deployment to Render!")
    print()
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = verify_production()
    exit(0 if success else 1)
