"""
Automated Shopify CSV upload using Selenium.
NO API NEEDED - just your Shopify login.
"""
import time
import glob
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def upload_to_shopify(email, password):
    """Upload all CSV files to Shopify automatically."""
    
    print("=" * 70)
    print("AUTOMATED SHOPIFY UPLOAD")
    print("=" * 70)
    
    # Setup Chrome
    print("\nSetting up browser...")
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    try:
        # Login to Shopify
        print("\nLogging into Shopify...")
        driver.get("https://admin.shopify.com/store/tbtgermany")
        time.sleep(5)
        
        # Check if login needed
        if "login" in driver.current_url or "account" in driver.current_url:
            print("Entering credentials...")
            
            # Email
            email_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "account_email"))
            )
            email_field.clear()
            email_field.send_keys(email)
            time.sleep(1)
            
            # Continue button
            continue_btn = driver.find_element(By.NAME, "commit")
            continue_btn.click()
            time.sleep(3)
            
            # Password
            password_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "account_password"))
            )
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # Login button
            login_btn = driver.find_element(By.NAME, "commit")
            login_btn.click()
            time.sleep(8)
        
        print("✓ Logged in successfully")
        
        # Get CSV files
        csv_files = sorted(glob.glob('shopify_imports/*_shopify.csv'))
        csv_files = [f for f in csv_files if os.path.getsize(f) > 100]
        
        if not csv_files:
            print("\n❌ No CSV files found in shopify_imports/")
            return False
        
        print(f"\nFound {len(csv_files)} files to upload")
        
        success_count = 0
        
        for i, csv_file in enumerate(csv_files, 1):
            filename = os.path.basename(csv_file)
            print(f"\n[{i}/{len(csv_files)}] Uploading {filename}...")
            
            try:
                # Go to products page
                driver.get("https://admin.shopify.com/store/tbtgermany/products")
                time.sleep(3)
                
                # Click Import button
                import_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Import')]"))
                )
                import_btn.click()
                time.sleep(2)
                
                # Upload file
                file_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
                file_input.send_keys(os.path.abspath(csv_file))
                time.sleep(3)
                
                # Click Upload and continue
                upload_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload and continue')]"))
                )
                upload_btn.click()
                time.sleep(5)
                
                # Click Import products
                import_products_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Import products')]"))
                )
                import_products_btn.click()
                time.sleep(3)
                
                print(f"  ✓ Upload initiated")
                success_count += 1
                
                # Wait before next upload
                if i < len(csv_files):
                    print("  Waiting 30 seconds...")
                    time.sleep(30)
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
        
        print("\n" + "=" * 70)
        print(f"UPLOAD COMPLETE: {success_count}/{len(csv_files)} files uploaded")
        print("=" * 70)
        print("\nCheck Shopify Admin → Products → Filter: Draft")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
        
    finally:
        time.sleep(5)
        driver.quit()
        print("\n✓ Browser closed")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python auto_shopify_upload.py <email> <password>")
        print("\nExample:")
        print("  python auto_shopify_upload.py admin@tbbt.de mypassword")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    upload_to_shopify(email, password)
