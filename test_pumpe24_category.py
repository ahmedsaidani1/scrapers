"""
Test pumpe24 category page structure - save HTML
"""
import undetected_chromedriver as uc
import time

print("Initializing Chrome driver...")
options = uc.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')

driver = uc.Chrome(options=options, version_main=143, use_subprocess=True)

print("\nFetching category page...")
driver.get("https://www.pumpe24.de/pumpen.html")
time.sleep(8)  # Wait longer for JS to load

print(f"Page title: {driver.title}")
print(f"Page source length: {len(driver.page_source)}")

# Save HTML to file
with open('pumpe24_category.html', 'w', encoding='utf-8') as f:
    f.write(driver.page_source)

print("\nSaved HTML to pumpe24_category.html")
print("\nFirst 2000 characters:")
print(driver.page_source[:2000])

driver.quit()
