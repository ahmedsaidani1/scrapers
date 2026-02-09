"""Test what Selenium sees on Akusolar"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--ignore-certificate-errors')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("=== Testing Akusolar with Selenium ===\n")
    
    # Test homepage
    url = "https://akusolar.fcostry3.cz/"
    print(f"Loading: {url}")
    driver.get(url)
    time.sleep(3)
    
    print(f"Current URL: {driver.current_url}")
    print(f"Page title: {driver.title}")
    
    # Get page source
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find h1
    h1_tags = soup.find_all('h1')
    print(f"\nFound {len(h1_tags)} h1 tags:")
    for h1 in h1_tags[:3]:
        print(f"  - {h1.text.strip()[:100]}")
    
    # Find links
    links = soup.find_all('a', href=True)
    product_links = [a.get('href') for a in links if 'rozvodnicova' in a.get('href', '').lower()]
    print(f"\nFound {len(product_links)} product links:")
    for link in product_links:
        print(f"  - {link}")
    
    # Test a product page
    if product_links:
        test_url = product_links[0]
        if test_url.startswith('/'):
            test_url = 'https://akusolar.fcostry3.cz' + test_url
        
        print(f"\n=== Testing product page ===")
        print(f"Loading: {test_url}")
        driver.get(test_url)
        time.sleep(3)
        
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        h1 = soup.find('h1')
        print(f"H1: {h1.text.strip() if h1 else 'Not found'}")
        
        # Check if it's a 404 page
        if '404' in driver.title or '404' in page_source[:1000]:
            print("⚠ This appears to be a 404 page")
        
        # Print first 500 chars of body
        body = soup.find('body')
        if body:
            print(f"\nFirst 500 chars of body:")
            print(body.text.strip()[:500])

finally:
    driver.quit()
    print("\n=== Test complete ===")
