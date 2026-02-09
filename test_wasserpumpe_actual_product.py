"""Test actual wasserpumpe product page"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(options=chrome_options)

try:
    # Test actual product page
    url = 'https://www.wasserpumpe.de/dab-nova-up-300-m-ae-flachsauger-tauchpumpe'
    print(f'Fetching: {url}')
    driver.get(url)
    
    # Wait for page to load
    time.sleep(5)
    
    print(f'Page title: {driver.title}')
    print('='*60)
    
    # Look for price with various selectors
    price_selectors = [
        'span.price',
        'div.price',
        '[class*="price"]',
        '[data-testid="price"]',
        'span[itemprop="price"]',
        'meta[itemprop="price"]'
    ]
    
    print('\nLooking for price elements:')
    for selector in price_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f'\nFound {len(elements)} elements with {selector}:')
                for i, elem in enumerate(elements[:5], 1):
                    try:
                        if elem.tag_name == 'meta':
                            content = elem.get_attribute('content')
                            print(f'  {i}. Meta content: {content}')
                        else:
                            text = elem.text
                            if text:
                                print(f'  {i}. Text: {text}')
                    except:
                        pass
        except Exception as e:
            pass
    
    # Look for product name
    print('\n' + '='*60)
    print('Product information:')
    print('='*60)
    
    try:
        h1 = driver.find_element(By.TAG_NAME, 'h1')
        print(f'Product name: {h1.text}')
    except:
        print('No H1 found')
    
    # Look for article number/SKU
    sku_selectors = [
        '[itemprop="sku"]',
        '[data-testid="sku"]',
        'span.sku',
        'div.sku'
    ]
    
    for selector in sku_selectors:
        try:
            elem = driver.find_element(By.CSS_SELECTOR, selector)
            print(f'SKU ({selector}): {elem.text}')
            break
        except:
            continue
    
    # Look for manufacturer
    brand_selectors = [
        '[itemprop="brand"]',
        'span.brand',
        'div.brand',
        'a.brand'
    ]
    
    for selector in brand_selectors:
        try:
            elem = driver.find_element(By.CSS_SELECTOR, selector)
            print(f'Brand ({selector}): {elem.text}')
            break
        except:
            continue
    
    # Save page source for inspection
    print('\n' + '='*60)
    print('Saving page source...')
    with open('wasserpumpe_product_page.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print('Saved to wasserpumpe_product_page.html')
    
    # Print a snippet with price-related content
    print('\n' + '='*60)
    print('Searching for price in page source...')
    print('='*60)
    
    page_source = driver.page_source
    
    # Look for price patterns in the HTML
    import re
    price_patterns = [
        r'€\s*\d+[,\.]\d{2}',
        r'\d+[,\.]\d{2}\s*€',
        r'"price":\s*"?\d+[,\.]?\d*"?',
        r'itemprop="price"\s+content="[\d\.,]+"'
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, page_source)
        if matches:
            print(f'\nPattern {pattern}:')
            for match in matches[:5]:
                print(f'  {match}')

finally:
    driver.quit()
