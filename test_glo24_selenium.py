"""
Test glo24.de with Selenium
"""
import undetected_chromedriver as uc
import time

print("Initializing Chrome driver...")
options = uc.ChromeOptions()
# Don't use headless - let's see what happens
# options.add_argument('--headless=new')
options.add_argument('--no-sandbox')

driver = uc.Chrome(options=options, version_main=143, use_subprocess=True)

print("\nTesting glo24.de homepage...")
driver.get("https://glo24.de")
time.sleep(5)

print(f"Page title: {driver.title}")
print(f"Current URL: {driver.current_url}")
print(f"Page source length: {len(driver.page_source)}")
print(f"\nFirst 500 characters:")
print(driver.page_source[:500])

if "403" in driver.page_source or "Forbidden" in driver.page_source:
    print("\n❌ Still getting 403 Forbidden")
else:
    print("\n✓ Successfully accessed!")

input("\nPress Enter to close browser...")
driver.quit()
