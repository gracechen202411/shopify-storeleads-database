#!/usr/bin/env python3
"""
Manual-assisted verification of buydecided.com's Google Ads history
手动辅助验证 buydecided.com 在 2025-11-19 之前是否有 Google Ads

This script will:
1. Open the browser (NOT headless)
2. Load the Google Ads Transparency page
3. Extract total ads count
4. Open the date filter
5. PAUSE for manual date selection
6. After manual selection, extract filtered ads count
"""

import time
import re
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os

# Target domain
DOMAIN = 'buydecided.com'
TODAY = date(2025, 12, 19)
CUTOFF_DATE = date(2025, 11, 19)  # 30 days ago

def create_driver():
    """Create and configure Chrome driver (visible browser)"""
    chrome_options = Options()
    # NO headless - we want to see the browser
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"❌ Failed to create Chrome driver: {str(e)}")
        return None


def extract_total_ads_count(driver):
    """Extract total ads count from the page"""
    try:
        page_text = driver.find_element(By.TAG_NAME, 'body').text

        # Try multiple patterns to find ads count
        patterns = [
            r'(\d+)\s+ads?',  # English
            r'(\d+)\s*个广告',  # Chinese
            r'(\d+)\s*件の広告',  # Japanese
            r'~(\d+)\s+ads?',
            r'~(\d+)\s*个广告',
            r'~(\d+)\s*件の広告',
        ]

        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                count = int(match.group(1))
                return count

        # Check for "0 ads"
        if '0 ads' in page_text.lower() or '0 个广告' in page_text or '0 件の広告' in page_text:
            return 0

        return None

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def main():
    print("=" * 80)
    print("🎯 MANUAL-ASSISTED Google Ads History Verification")
    print("=" * 80)
    print(f"\n📅 Today's date: {TODAY}")
    print(f"📅 Cutoff date: {CUTOFF_DATE} (30 days ago)")
    print(f"🌐 Domain: {DOMAIN}")
    print(f"\n🎯 Task: Verify if {DOMAIN} had Google Ads BEFORE {CUTOFF_DATE}")

    # Create screenshots directory
    screenshots_dir = "/Users/hangzhouweineng/Desktop/shopify-storeleads-database/Storeleads/screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    # Create driver
    print("\n🌐 Initializing Chrome driver (browser will be visible)...")
    driver = create_driver()

    if not driver:
        print("\n❌ Failed to create web driver.")
        return

    print("✅ Chrome driver initialized successfully")

    url = f"https://adstransparency.google.com/?region=anywhere&domain={DOMAIN}"

    try:
        # Step 1: Load page
        print(f"\n{'=' * 80}")
        print("STEP 1: Loading page")
        print(f"{'=' * 80}")
        print(f"URL: {url}")
        driver.get(url)
        print("⏳ Waiting 5 seconds for page to load...")
        time.sleep(5)

        screenshot1 = f"{screenshots_dir}/{DOMAIN}_manual_01_initial.png"
        driver.save_screenshot(screenshot1)
        print(f"📸 Screenshot: {screenshot1}")

        # Step 2: Extract total ads count
        print(f"\n{'=' * 80}")
        print("STEP 2: Extracting total ads count")
        print(f"{'=' * 80}")
        total_ads = extract_total_ads_count(driver)

        if total_ads is not None:
            print(f"✅ Total ads count (all time): {total_ads}")

            if total_ads == 0:
                print("\n📊 RESULT: 0 ads found - never_advertised")
                driver.quit()
                return
        else:
            print("⚠️  Could not extract total ads count")

        # Step 3: Find and click date filter
        print(f"\n{'=' * 80}")
        print("STEP 3: Opening date filter")
        print(f"{'=' * 80}")

        # Try to find and click the date filter
        selectors = [
            "//span[contains(text(), '全期間')]",
            "//button[contains(text(), '全期間')]",
            "//div[contains(text(), '全期間')]",
        ]

        date_filter_clicked = False
        for selector in selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"✅ Found date filter: {selector}")
                    elements[0].click()
                    date_filter_clicked = True
                    print("✅ Clicked date filter")
                    time.sleep(2)
                    break
            except:
                continue

        if date_filter_clicked:
            screenshot2 = f"{screenshots_dir}/{DOMAIN}_manual_02_date_filter_opened.png"
            driver.save_screenshot(screenshot2)
            print(f"📸 Screenshot: {screenshot2}")
        else:
            print("⚠️  Could not click date filter automatically")

        # Step 4: MANUAL DATE SELECTION
        print(f"\n{'=' * 80}")
        print("STEP 4: MANUAL DATE SELECTION")
        print(f"{'=' * 80}")
        print("\n⏸️  PLEASE MANUALLY:")
        print(f"   1. In the browser, set END DATE to: {CUTOFF_DATE} (2025年11月19日)")
        print("   2. Click OK/確定 to apply the filter")
        print("   3. Wait for the page to refresh and show filtered results")
        print("\n⏸️  When done, press ENTER in this terminal to continue...")

        input()

        # Step 5: Extract filtered ads count
        print(f"\n{'=' * 80}")
        print("STEP 5: Extracting ads count after date filter")
        print(f"{'=' * 80}")
        time.sleep(2)

        screenshot3 = f"{screenshots_dir}/{DOMAIN}_manual_03_after_filter.png"
        driver.save_screenshot(screenshot3)
        print(f"📸 Screenshot: {screenshot3}")

        filtered_ads = extract_total_ads_count(driver)

        print(f"\n{'=' * 80}")
        print("📊 FINAL RESULTS")
        print(f"{'=' * 80}")
        print(f"\n🌐 Domain: {DOMAIN}")
        print(f"📅 Today: {TODAY}")
        print(f"📅 Cutoff Date: {CUTOFF_DATE}")
        print(f"\n📊 Total ads (all time): {total_ads}")
        print(f"📊 Ads before {CUTOFF_DATE}: {filtered_ads}")

        if filtered_ads is not None:
            if filtered_ads == 0:
                classification = 'new_advertiser_30d'
                print(f"\n✅ CLASSIFICATION: {classification}")
                print(f"   🆕 NEW ADVERTISER (within 30 days)")
                print(f"   Started advertising AFTER {CUTOFF_DATE}")
            else:
                classification = 'old_advertiser'
                print(f"\n✅ CLASSIFICATION: {classification}")
                print(f"   👴 OLD ADVERTISER")
                print(f"   Had {filtered_ads} ads BEFORE {CUTOFF_DATE}")
        else:
            print("\n⚠️  CLASSIFICATION: unknown")
            print("   Could not extract filtered ads count")

        print(f"\n📸 Screenshots:")
        print(f"   {screenshot1}")
        if date_filter_clicked:
            print(f"   {screenshot2}")
        print(f"   {screenshot3}")

        print("\n⏸️  Press ENTER to close browser...")
        input()

    finally:
        print("\n🔒 Closing browser...")
        driver.quit()

    print("\n✅ Done!")


if __name__ == '__main__':
    main()
