"""
Test Selenium access to pumpe24.de
"""
import undetected_chromedriver as uc
import time

print("Initializing Chrome driver...")
options = uc.ChromeOptions()
# Don't use headless for testing - let's see what happens
# options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = uc.Chrome(options=options, version_main=143, use_subprocess=True)

print("\nTesting pumpe24.de homepage...")
driver.get("https://pumpe24.de")
time.sleep(5)

print(f"Page title: {driver.title}")
print(f"Current URL: {driver.current_url}")
print(f"\nPage source length: {len(driver.page_source)}")
print(f"\nFirst 500 characters of page:")
print(driver.page_source[:500])

print("\n\nTesting sitemap...")
driver.get("https://pumpe24.de/sitemap.xml")
time.sleep(3)

print(f"Sitemap page source length: {len(driver.page_source)}")
print(f"\nFirst 1000 characters:")
print(driver.page_source[:1000])

input("\nPress Enter to close browser...")
driver.quit()
