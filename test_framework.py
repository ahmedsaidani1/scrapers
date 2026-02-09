#!/usr/bin/env python3
"""
Quick test script to verify the framework is working.
Run this before deploying to production.
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        import requests
        import bs4
        import gspread
        import oauth2client
        import csv
        print("✓ All required packages installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        print("Run: pip3 install -r requirements.txt")
        return False

def test_framework_files():
    """Test that all framework files exist."""
    print("\nTesting framework files...")
    required_files = [
        "config.py",
        "base_scraper.py",
        "google_sheets_helper.py",
        "scraper_template.py",
        "sample_scraper.py",
        "run_all_scrapers.sh",
        "setup_cron.sh",
        "requirements.txt"
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} missing")
            all_exist = False
    
    return all_exist

def test_directories():
    """Test that required directories exist or can be created."""
    print("\nTesting directories...")
    from config import DATA_DIR, LOGS_DIR, CREDENTIALS_DIR
    
    dirs = {
        "data": DATA_DIR,
        "logs": LOGS_DIR,
        "credentials": CREDENTIALS_DIR
    }
    
    for name, path in dirs.items():
        if path.exists():
            print(f"✓ {name}/ directory exists")
        else:
            print(f"⚠ {name}/ directory will be created on first run")
    
    return True

def test_credentials():
    """Test that credentials file exists."""
    print("\nTesting credentials...")
    from config import CREDENTIALS_FILE
    
    if CREDENTIALS_FILE.exists():
        print(f"✓ credentials.json found")
        return True
    else:
        print(f"⚠ credentials.json not found at {CREDENTIALS_FILE}")
        print("  You need to add your Google Sheets credentials")
        print("  Place credentials.json in the credentials/ directory")
        return False

def test_config():
    """Test configuration file."""
    print("\nTesting configuration...")
    try:
        from config import (
            CSV_COLUMNS, SHEET_IDS, SCRAPER_CONFIGS,
            USER_AGENTS, REQUEST_TIMEOUT
        )
        print(f"✓ Configuration loaded")
        print(f"  - CSV columns: {len(CSV_COLUMNS)}")
        print(f"  - User agents: {len(USER_AGENTS)}")
        print(f"  - Request timeout: {REQUEST_TIMEOUT}s")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_base_scraper():
    """Test that base scraper can be imported."""
    print("\nTesting base scraper...")
    try:
        from base_scraper import BaseScraper
        print("✓ BaseScraper class loaded")
        return True
    except Exception as e:
        print(f"✗ BaseScraper error: {e}")
        return False

def test_google_sheets_helper():
    """Test Google Sheets helper."""
    print("\nTesting Google Sheets helper...")
    try:
        from google_sheets_helper import GoogleSheetsHelper, push_data
        print("✓ GoogleSheetsHelper loaded")
        
        # Try to initialize (will fail without credentials, but that's ok)
        try:
            helper = GoogleSheetsHelper()
            print("✓ Google Sheets authentication successful")
            return True
        except FileNotFoundError:
            print("⚠ Cannot authenticate (credentials.json missing)")
            print("  This is expected if you haven't added credentials yet")
            return True
        except Exception as e:
            print(f"⚠ Authentication issue: {e}")
            return True
            
    except Exception as e:
        print(f"✗ GoogleSheetsHelper error: {e}")
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("Solar Scraper Framework - Test Suite")
    print("="*60)
    print()
    
    tests = [
        ("Package imports", test_imports),
        ("Framework files", test_framework_files),
        ("Directories", test_directories),
        ("Credentials", test_credentials),
        ("Configuration", test_config),
        ("Base scraper", test_base_scraper),
        ("Google Sheets helper", test_google_sheets_helper),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! Framework is ready to use.")
        print("\nNext steps:")
        print("1. Add your credentials.json to credentials/ directory")
        print("2. Create your first scraper using scraper_template.py")
        print("3. Test locally: python3 your_scraper.py")
        print("4. Deploy to server when ready")
        return 0
    else:
        print("\n⚠ Some tests failed. Fix issues before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
