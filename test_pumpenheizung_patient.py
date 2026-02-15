"""
Test with very long timeout - maybe the site is just VERY slow
"""
import undetected_chromedriver as uc
import time

print("Testing with 2-minute timeout...")
print("=" * 60)

try:
    options = uc.ChromeOptions()
    # Don't use headless - sometimes helps
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    print("\n1. Starting Chrome (visible mode)...")
    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(120)  # 2 minutes!
    
    print("2. Loading website (this may take a while)...")
    print("   Waiting up to 2 minutes...")
    
    start = time.time()
    driver.get("https://pumpen-heizung.de")
    elapsed = time.time() - start
    
    print(f"\n✓ SUCCESS! Page loaded in {elapsed:.2f}s")
    print(f"✓ Title: {driver.title}")
    print(f"✓ URL: {driver.current_url}")
    
    # Wait a bit more
    print("\n3. Waiting for page to fully render...")
    time.sleep(5)
    
    # Save screenshot
    driver.save_screenshot("pumpenheizung_screenshot.png")
    print("✓ Saved screenshot to pumpenheizung_screenshot.png")
    
    # Save HTML
    with open("pumpenheizung_success.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("✓ Saved HTML to pumpenheizung_success.html")
    
    print("\n✓ Test successful! Check the files.")
    
    input("\nPress Enter to close browser...")
    driver.quit()
    
except KeyboardInterrupt:
    print("\n\n⚠️  Interrupted by user")
    try:
        driver.quit()
    except:
        pass
    
except Exception as e:
    print(f"\n✗ Failed after waiting: {type(e).__name__}")
    print(f"   {str(e)[:200]}")
    try:
        driver.quit()
    except:
        pass

print("\n" + "=" * 60)
