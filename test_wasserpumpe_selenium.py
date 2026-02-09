"""Test wasserpumpe with Selenium to handle JavaScript"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

print('Starting Chrome driver...')
driver = webdriver.Chrome(options=chrome_options)

try:
    # Test a category page
    url = 'https://www.wasserpumpe.de/tauchpumpe'
    print(f'\nFetching: {url}')
    driver.get(url)
    
    # Wait for page to load
    print('Waiting for page to load...')
    time.sleep(5)
    
    # Check page title
    print(f'Page title: {driver.title}')
    
    # Look for product elements
    print('\nLooking for product elements...')
    
    # Try different selectors for products
    selectors = [
        'div.product-item',
        'div.product',
        'a.product-link',
        '[data-testid="product"]',
        'div[class*="product"]',
        'li.item'
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f'\nFound {len(elements)} elements with selector: {selector}')
                
                # Get first few product links
                for i, elem in enumerate(elements[:3], 1):
                    try:
                        # Try to find link
                        link = elem.find_element(By.TAG_NAME, 'a')
                        href = link.get_attribute('href')
                        text = elem.text[:100]
                        print(f'  {i}. {href}')
                        print(f'     Text: {text}')
                    except:
                        pass
                break
        except Exception as e:
            continue
    
    # Try to find any links on the page
    print('\n' + '='*60)
    print('All links on page:')
    print('='*60)
    
    links = driver.find_elements(By.TAG_NAME, 'a')
    product_links = []
    
    for link in links:
        href = link.get_attribute('href')
        if href and 'wasserpumpe.de' in href and href not in product_links:
            # Filter for potential products
            if not any(skip in href for skip in [
                '/rechtliches', '/datenschutz', '/impressum', '/uber-uns',
                'javascript:', '#', '/allgemeine-geschaftsbedingungen'
            ]):
                product_links.append(href)
    
    print(f'Found {len(product_links)} unique links')
    print('\nFirst 10 links:')
    for i, link in enumerate(product_links[:10], 1):
        print(f'{i}. {link}')
    
    # Test one product link
    if product_links:
        test_url = [l for l in product_links if l != url][0] if len(product_links) > 1 else product_links[0]
        
        print(f'\n{"="*60}')
        print(f'Testing product page: {test_url}')
        print('='*60)
        
        driver.get(test_url)
        time.sleep(5)
        
        print(f'Page title: {driver.title}')
        
        # Look for price
        price_selectors = [
            'span.price',
            'div.price',
            '[class*="price"]',
            '[data-testid="price"]'
        ]
        
        for selector in price_selectors:
            try:
                price_elem = driver.find_element(By.CSS_SELECTOR, selector)
                price_text = price_elem.text
                if price_text and ('€' in price_text or ',' in price_text):
                    print(f'\n✓ Found price with {selector}: {price_text}')
                    break
            except:
                continue
        else:
            print('\n✗ No price found')
            
            # Print page source snippet
            print('\nPage source snippet (first 2000 chars):')
            print(driver.page_source[:2000])

finally:
    driver.quit()
    print('\nDriver closed')
