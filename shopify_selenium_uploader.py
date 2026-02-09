"""
Automated Shopify CSV upload using Selenium.
No API tokens needed - just your Shopify login credentials.
"""
import time
import glob
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class ShopifySeleniumUploader:
    """
    Automate Shopify CSV uploads using Selenium.
    Logs into Shopify admin and uploads CSV files automatically.
    """
    
    def __init__(self, email: str, password: str, store_url: str = "tbbt.de"):
        """
        Initialize uploader.
        
        Args:
            email: Your Shopify admin email
            password: Your Shopify admin password
            store_url: Your store URL (tbbt.de)
        """
        self.email = email
        self.password = password
        self.store_url = store_url
        self.driver = None
    
    def setup_driver(self, headless: bool = False):
        """Setup Chrome driver."""
        options = Options()
        
        if headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Set download directory
        prefs = {
            "download.default_directory": os.path.abspath("shopify_imports"),
            "download.prompt_for_download": False,
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        
        print("✓ Chrome driver initialized")
    
    def login(self):
        """Login to Shopify admin."""
        try:
            print(f"\nLogging into Shopify admin...")
            
            # Go directly to admin URL
            self.driver.get("https://admin.shopify.com/store/tbtgermany")
            time.sleep(5)
            
            # Check if already logged in or need to login
            current_url = self.driver.current_url
            
            if "login" in current_url or "account" in current_url:
                # Need to login
                print("Login page detected, entering credentials...")
                
                # Wait for page to fully load
                time.sleep(3)
                
                # Enter email
                try:
                    email_field = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "account_email"))
                    )
                    email_field.clear()
                    email_field.send_keys(self.email)
                    time.sleep(1)
                    
                    # Click continue
                    continue_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.NAME, "commit"))
                    )
                    continue_btn.click()
                    time.sleep(3)
                    
                    # Enter password
                    password_field = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "account_password"))
                    )
                    password_field.clear()
                    password_field.send_keys(self.password)
                    time.sleep(1)
                    
                    # Click login
                    login_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.NAME, "commit"))
                    )
                    login_btn.click()
                    time.sleep(8)
                except Exception as e:
                    print(f"Login form error: {e}")
                    print("You may need to login manually in the browser window")
                    time.sleep(15)  # Give time for manual login
            
            # Check if logged in
            current_url = self.driver.current_url
            if "admin.shopify.com/store" in current_url or "/admin" in current_url:
                print("✓ Successfully logged in")
                return True
            else:
                print(f"❌ Login failed. Current URL: {current_url}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            print("Current URL:", self.driver.current_url)
            return False
    
    def upload_csv(self, csv_file: str) -> bool:
        """
        Upload a CSV file to Shopify.
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            True if successful
        """
        try:
            print(f"\nUploading {os.path.basename(csv_file)}...")
            
            # Go to products page
            self.driver.get(f"https://admin.shopify.com/store/tbtgermany/products")
            time.sleep(3)
            
            # Click Import button
            import_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Import')]"))
            )
            import_btn.click()
            time.sleep(2)
            
            # Upload file
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            file_input.send_keys(os.path.abspath(csv_file))
            time.sleep(3)
            
            # Click Upload and continue
            upload_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Upload and continue')]"))
            )
            upload_btn.click()
            time.sleep(5)
            
            # Click Import products
            import_products_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Import products')]"))
            )
            import_products_btn.click()
            time.sleep(3)
            
            print(f"✓ Upload initiated for {os.path.basename(csv_file)}")
            
            # Wait for import to complete (check for success message)
            time.sleep(10)
            
            return True
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    def upload_all_csvs(self, csv_dir: str = "shopify_imports", max_files: int = None):
        """
        Upload all CSV files from directory.
        
        Args:
            csv_dir: Directory containing CSV files
            max_files: Maximum number of files to upload (None = all)
        """
        csv_files = sorted(glob.glob(f"{csv_dir}/*_shopify.csv"))
        
        if not csv_files:
            print(f"❌ No CSV files found in {csv_dir}/")
            return
        
        # Filter out empty files
        csv_files = [f for f in csv_files if os.path.getsize(f) > 100]
        
        if max_files:
            csv_files = csv_files[:max_files]
        
        print(f"\nFound {len(csv_files)} CSV files to upload")
        
        stats = {'success': 0, 'failed': 0}
        
        for i, csv_file in enumerate(csv_files, 1):
            print(f"\n[{i}/{len(csv_files)}] Processing {os.path.basename(csv_file)}")
            
            if self.upload_csv(csv_file):
                stats['success'] += 1
            else:
                stats['failed'] += 1
            
            # Wait between uploads
            if i < len(csv_files):
                print("Waiting 30 seconds before next upload...")
                time.sleep(30)
        
        print(f"\n{'='*70}")
        print("Upload Summary:")
        print(f"  Successful: {stats['success']}")
        print(f"  Failed: {stats['failed']}")
        print(f"{'='*70}")
    
    def close(self):
        """Close browser."""
        if self.driver:
            self.driver.quit()
            print("\n✓ Browser closed")


def main():
    """Main execution."""
    import sys
    
    print("=" * 70)
    print("SHOPIFY SELENIUM UPLOADER - Automated CSV Upload")
    print("=" * 70)
    
    # Get credentials
    if len(sys.argv) < 3:
        print("\nUsage:")
        print("  python shopify_selenium_uploader.py <email> <password> [max_files]")
        print("\nExample:")
        print("  python shopify_selenium_uploader.py admin@tbbt.de mypassword 5")
        print("\nThis will:")
        print("  1. Login to Shopify admin")
        print("  2. Upload CSV files from shopify_imports/ folder")
        print("  3. Import products automatically")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    max_files = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    # Initialize uploader
    uploader = ShopifySeleniumUploader(email, password)
    
    try:
        # Setup browser
        uploader.setup_driver(headless=False)  # Set to True for headless mode
        
        # Login
        if not uploader.login():
            print("\n❌ Login failed. Check your credentials.")
            sys.exit(1)
        
        # Upload CSVs
        uploader.upload_all_csvs(max_files=max_files)
        
        print("\n✓ All uploads complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Close browser
        time.sleep(5)
        uploader.close()


if __name__ == "__main__":
    main()
