#!/usr/bin/env python3
"""
Check if stores had Google Ads BEFORE 2025-11-19 (30 days ago)
使用 Selenium 检查店铺在 2025-11-19 之前是否有 Google 广告
"""

import time
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Stores to check
STORES = [
    {
        'domain': 'ventiontech.com',
        'url': 'https://adstransparency.google.com/?region=anywhere&domain=ventiontech.com'
    },
    {
        'domain': 'uwowocosplay.com',
        'url': 'https://adstransparency.google.com/?region=anywhere&domain=uwowocosplay.com'
    }
]

CUTOFF_DATE = date(2025, 11, 19)  # 30 days ago from 2025-12-19


def create_driver():
    """Create and configure Chrome driver"""
    chrome_options = Options()
    # Remove headless for debugging - we need to see what's happening
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # Add language preference for Chinese
    chrome_options.add_argument('--lang=zh-CN')
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'zh-CN,zh'})

    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"❌ Failed to create Chrome driver: {str(e)}")
        print("💡 Please make sure ChromeDriver is installed:")
        print("   brew install chromedriver")
        return None


def check_historical_ads(driver, store_info):
    """
    Check if a store had Google Ads BEFORE 2025-11-19
    Returns: dict with results
    """
    domain = store_info['domain']
    url = store_info['url']

    print(f"\n{'=' * 80}")
    print(f"🔍 Checking: {domain}")
    print(f"{'=' * 80}")
    print(f"URL: {url}")
    print(f"Target date: BEFORE {CUTOFF_DATE}")

    result = {
        'domain': domain,
        'url': url,
        'date_range_checked': None,
        'result': None,
        'ads_count': None,
        'evidence': None,
        'error': None
    }

    try:
        # Navigate to URL
        print("\n📄 Loading page...")
        driver.get(url)

        # Wait for page to load
        print("⏳ Waiting for page to load...")
        time.sleep(5)

        # Take initial screenshot
        print("📸 Taking initial screenshot...")
        screenshot_path = f"/Users/hangzhouweineng/Desktop/shopify-storeleads-database/Storeleads/screenshots/{domain}_initial.png"
        driver.save_screenshot(screenshot_path)
        print(f"   Saved: {screenshot_path}")

        # Look for date filter button/dropdown
        print("\n🔍 Looking for date filter...")

        # Try to find date filter elements (common patterns)
        date_filter_selectors = [
            "//button[contains(text(), '自定义')]",
            "//button[contains(text(), '日期')]",
            "//div[contains(@class, 'date-filter')]",
            "//button[contains(@aria-label, 'date')]",
            "//button[contains(@class, 'date')]",
            "//div[contains(text(), '日期范围')]",
            "//button[contains(text(), 'Date')]",
            "//button[contains(text(), 'Custom')]"
        ]

        date_filter_found = False
        date_filter_element = None

        for selector in date_filter_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"✅ Found potential date filter with selector: {selector}")
                    print(f"   Found {len(elements)} element(s)")
                    date_filter_element = elements[0]
                    date_filter_found = True
                    break
            except Exception as e:
                continue

        if not date_filter_found:
            print("⚠️  Could not find date filter automatically")
            print("🔍 Searching page for date-related text...")
            page_source = driver.page_source

            # Check if there's any date filter on the page
            if '自定义' in page_source or 'Custom' in page_source or '日期' in page_source:
                print("✅ Found date filter keywords in page")
                result['evidence'] = "Date filter exists on page but could not be clicked automatically"
            else:
                print("❌ No date filter found on page")
                result['evidence'] = "No date filter found on page"

        # Get current page text to check for ads
        print("\n📊 Checking current ad count...")
        page_text = driver.find_element(By.TAG_NAME, 'body').text

        # Check for "0 个广告" or ad counts
        if '0 个广告' in page_text or '0 ads' in page_text.lower():
            print("   Current status: 0 ads displayed")
            result['ads_count'] = 0
            result['result'] = 'NO_ADS'
            result['evidence'] = "Page shows '0 个广告' without date filter applied"
        else:
            # Try to find ad count
            import re
            patterns = [
                r'(\d+)\s*个广告',
                r'(\d+)\s*ads'
            ]

            for pattern in patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    ads_count = int(match.group(1))
                    print(f"   Current status: {ads_count} ads displayed")
                    result['ads_count'] = ads_count

                    # If date filter was found, we should try to use it
                    if date_filter_found and date_filter_element:
                        print("\n⚠️  MANUAL VERIFICATION NEEDED:")
                        print("   The script found ads and a date filter.")
                        print("   Please manually:")
                        print(f"   1. Click the date filter button")
                        print(f"   2. Set END DATE to {CUTOFF_DATE} or earlier")
                        print(f"   3. Check if ads still appear")
                        result['result'] = 'MANUAL_CHECK_REQUIRED'
                        result['evidence'] = f"Found {ads_count} ads currently. Date filter found but needs manual verification."
                    else:
                        result['result'] = 'HAS_ADS'
                        result['evidence'] = f"Found {ads_count} ads currently. No date filter to check historical data."
                    break

        # Take final screenshot
        print("\n📸 Taking final screenshot...")
        screenshot_path = f"/Users/hangzhouweineng/Desktop/shopify-storeleads-database/Storeleads/screenshots/{domain}_final.png"
        driver.save_screenshot(screenshot_path)
        print(f"   Saved: {screenshot_path}")

        # Print page preview
        print("\n📄 Page text preview (first 500 chars):")
        print("-" * 80)
        print(page_text[:500])
        print("-" * 80)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        result['error'] = str(e)
        result['result'] = 'ERROR'

    return result


def print_result(result):
    """Print formatted result"""
    print(f"\n{'=' * 80}")
    print(f"📊 RESULT FOR: {result['domain']}")
    print(f"{'=' * 80}")
    print(f"Domain: {result['domain']}")
    print(f"Date range checked: {result['date_range_checked'] or 'N/A - Manual check needed'}")
    print(f"Result: {result['result']}")
    print(f"Ads count (if found): {result['ads_count']}")
    print(f"Evidence: {result['evidence']}")
    if result['error']:
        print(f"Error: {result['error']}")
    print(f"{'=' * 80}")


def main():
    print("=" * 80)
    print("🚀 Historical Google Ads Checker")
    print("=" * 80)
    print(f"\n📅 Today's date: {date.today()}")
    print(f"📅 Checking for ads BEFORE: {CUTOFF_DATE}")
    print(f"📊 Total stores to check: {len(STORES)}")
    print()

    # Create screenshots directory
    import os
    screenshots_dir = "/Users/hangzhouweineng/Desktop/shopify-storeleads-database/Storeleads/screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    # Create driver
    print("🌐 Initializing Chrome driver...")
    driver = create_driver()

    if not driver:
        print("\n❌ Failed to create web driver. Exiting.")
        return

    print("✅ Web driver initialized successfully")

    results = []

    try:
        # Check each store
        for i, store_info in enumerate(STORES, 1):
            print(f"\n{'=' * 80}")
            print(f"Progress: {i}/{len(STORES)}")
            print(f"{'=' * 80}")

            result = check_historical_ads(driver, store_info)
            results.append(result)

            print_result(result)

            # Wait between requests
            if i < len(STORES):
                print("\n⏳ Waiting 5 seconds before next request...")
                time.sleep(5)

    finally:
        print("\n🔒 Closing web driver...")
        # Keep browser open for manual verification
        input("\n⏸️  Press ENTER to close browser and exit...")
        driver.quit()

    # Print final summary
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY")
    print("=" * 80)

    for result in results:
        print(f"\n{result['domain']}:")
        print(f"  Result: {result['result']}")
        print(f"  Ads count: {result['ads_count']}")
        print(f"  Evidence: {result['evidence']}")

    print("\n" + "=" * 80)
    print("✅ Done!")
    print("=" * 80)
    print("\n💡 IMPORTANT:")
    print("   Google Ads Transparency page may require MANUAL DATE FILTERING")
    print("   Please review the screenshots and browser state to complete verification")
    print(f"   Screenshots saved in: {screenshots_dir}")


if __name__ == '__main__':
    main()
