#!/usr/bin/env python3
"""
Automated verification of buydecided.com's Google Ads history - Version 2
自动验证 buydecided.com 在 2025-11-19 之前是否有 Google Ads (改进版)
"""

import time
import re
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Target domain
DOMAIN = 'buydecided.com'
TODAY = date(2025, 12, 19)
CUTOFF_DATE = date(2025, 11, 19)  # 30 days ago

def create_driver():
    """Create and configure Chrome driver"""
    chrome_options = Options()
    # Keep visible for now
    # chrome_options.add_argument('--headless')
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


def extract_ads_count(driver):
    """Extract ads count from the page"""
    try:
        page_text = driver.find_element(By.TAG_NAME, 'body').text

        patterns = [
            r'(\d+)\s+ads?',
            r'(\d+)\s*个广告',
            r'(\d+)\s*件の広告',
            r'~(\d+)\s+ads?',
            r'~(\d+)\s*个广告',
            r'~(\d+)\s*件の広告',
        ]

        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        if '0 ads' in page_text.lower() or '0 个广告' in page_text or '0 件の広告' in page_text:
            return 0

        return None

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def main():
    print("=" * 80)
    print("🎯 Automated Google Ads History Verification - V2")
    print("=" * 80)
    print(f"\n📅 Today: {TODAY}")
    print(f"📅 Cutoff: {CUTOFF_DATE} (30 days ago)")
    print(f"🌐 Domain: {DOMAIN}")

    screenshots_dir = "/Users/hangzhouweineng/Desktop/shopify-storeleads-database/Storeleads/screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    driver = create_driver()
    if not driver:
        return

    url = f"https://adstransparency.google.com/?region=anywhere&domain={DOMAIN}"

    result = {
        'domain': DOMAIN,
        'total_ads': None,
        'ads_before_cutoff': None,
        'classification': None,
        'screenshots': []
    }

    try:
        # Step 1: Load page
        print(f"\n{'=' * 80}")
        print("STEP 1: Loading page")
        print(f"{'=' * 80}")
        driver.get(url)
        time.sleep(5)

        ss1 = f"{screenshots_dir}/{DOMAIN}_v2_01_initial.png"
        driver.save_screenshot(ss1)
        result['screenshots'].append(ss1)
        print(f"📸 {ss1}")

        # Step 2: Get total ads count
        print(f"\n{'=' * 80}")
        print("STEP 2: Extract total ads count")
        print(f"{'=' * 80}")
        total_ads = extract_ads_count(driver)
        result['total_ads'] = total_ads
        print(f"✅ Total ads: {total_ads}")

        if total_ads == 0:
            result['classification'] = 'never_advertised'
            print("\n✅ RESULT: never_advertised")
            return result

        # Step 3: Click date filter
        print(f"\n{'=' * 80}")
        print("STEP 3: Click date filter")
        print(f"{'=' * 80}")

        # Wait for page to fully load
        print("⏳ Waiting for page elements to load...")
        time.sleep(3)

        date_filter = None
        selectors = [
            # Japanese
            "//span[contains(text(), '全期間')]",
            "//button[contains(text(), '全期間')]",
            "//*[contains(text(), '全期間')]",
            # Chinese
            "//span[contains(text(), '任意时间')]",
            "//button[contains(text(), '任意时间')]",
            "//*[contains(text(), '任意时间')]",
            # English
            "//span[contains(text(), 'All time')]",
            "//button[contains(text(), 'All time')]",
            "//*[contains(text(), 'All time')]",
        ]

        for selector in selectors:
            try:
                print(f"   Trying selector: {selector}")
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    date_filter = elements[0]
                    print(f"✅ Found: {selector}")
                    print(f"   Element text: '{elements[0].text}'")
                    print(f"   Element tag: {elements[0].tag_name}")
                    break
            except Exception as e:
                print(f"   Error: {str(e)}")

        # If still not found, let's search in page source
        if not date_filter:
            print("\n⚠️  Direct search failed, checking page source...")
            page_source = driver.page_source
            if '全期間' in page_source:
                print("✅ Found '全期間' in page source")
                # Try to find any clickable element containing this text
                try:
                    wait = WebDriverWait(driver, 10)
                    date_filter = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '全期間')]"))
                    )
                    print("✅ Found clickable element with WebDriverWait")
                except:
                    pass

        if not date_filter:
            print("❌ Date filter not found after all attempts")
            print("\n📄 Page text preview:")
            page_text = driver.find_element(By.TAG_NAME, 'body').text
            print(page_text[:500])
            return result

        date_filter.click()
        time.sleep(2)

        ss2 = f"{screenshots_dir}/{DOMAIN}_v2_02_filter_opened.png"
        driver.save_screenshot(ss2)
        result['screenshots'].append(ss2)
        print(f"📸 {ss2}")

        # Step 4: Find END DATE input and modify it
        print(f"\n{'=' * 80}")
        print("STEP 4: Set end date")
        print(f"{'=' * 80}")

        # Find all input fields with text values containing date patterns
        all_inputs = driver.find_elements(By.TAG_NAME, 'input')
        end_date_input = None

        for inp in all_inputs:
            try:
                value = inp.get_attribute('value')
                # Check for any date format
                if value and ('2025' in value or '12' in value or '19' in value):
                    # Check if it looks like an end date (has current date)
                    if '12' in value or 'Dec' in value or '12月' in value:
                        end_date_input = inp
                        print(f"✅ Found end date input with value: {value}")
                        break
            except:
                pass

        if not end_date_input:
            print("⚠️  Could not find end date input, trying alternative method...")
            # Try to find by position (usually the second input in the date picker)
            try:
                inputs_in_picker = driver.find_elements(By.XPATH, "//input[contains(@value, '年')]")
                if len(inputs_in_picker) >= 2:
                    end_date_input = inputs_in_picker[1]  # Second one is usually end date
                    print("✅ Found end date input by position")
            except:
                pass

        if end_date_input:
            # Clear and set new date
            print(f"📅 Setting end date to {CUTOFF_DATE}...")
            try:
                # Triple-click to select all text
                end_date_input.click()
                time.sleep(0.3)
                end_date_input.send_keys(Keys.COMMAND + "a")  # Select all
                time.sleep(0.3)

                # Type new date in Japanese format
                new_date_str = f"{CUTOFF_DATE.year}年{CUTOFF_DATE.month}月{CUTOFF_DATE.day}日"
                end_date_input.send_keys(new_date_str)
                time.sleep(1)

                print(f"✅ End date set to: {new_date_str}")

                ss3 = f"{screenshots_dir}/{DOMAIN}_v2_03_date_set.png"
                driver.save_screenshot(ss3)
                result['screenshots'].append(ss3)
                print(f"📸 {ss3}")

            except Exception as e:
                print(f"❌ Error setting date: {str(e)}")
                import traceback
                traceback.print_exc()
                return result

        else:
            print("❌ Could not find end date input")
            return result

        # Step 5: Click OK button
        print(f"\n{'=' * 80}")
        print("STEP 5: Click OK button")
        print(f"{'=' * 80}")

        ok_button = None
        ok_selectors = [
            # Chinese (Simplified)
            "//button[text()='确定']",
            "//button[contains(text(), '确定')]",
            "//*[text()='确定']",
            # Japanese
            "//button[contains(text(), '確定')]",
            # English
            "//button[text()='OK']",
            "//button[contains(text(), 'OK')]",
            "//button[contains(text(), 'Apply')]",
        ]

        for selector in ok_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    ok_button = elements[0]
                    print(f"✅ Found OK button: {selector}")
                    break
            except:
                pass

        if ok_button:
            # Try to scroll into view first
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", ok_button)
                time.sleep(0.5)
            except:
                pass

            # Try regular click first
            try:
                ok_button.click()
                print("✅ Clicked OK (regular click)")
            except:
                # If regular click fails, use JavaScript click
                print("⚠️  Regular click failed, trying JavaScript click...")
                driver.execute_script("arguments[0].click();", ok_button)
                print("✅ Clicked OK (JavaScript click)")

            time.sleep(4)  # Wait for page to reload with filtered results

            ss4 = f"{screenshots_dir}/{DOMAIN}_v2_04_filtered.png"
            driver.save_screenshot(ss4)
            result['screenshots'].append(ss4)
            print(f"📸 {ss4}")

        else:
            print("❌ Could not find OK button")
            return result

        # Step 6: Extract filtered ads count
        print(f"\n{'=' * 80}")
        print("STEP 6: Extract filtered ads count")
        print(f"{'=' * 80}")

        filtered_ads = extract_ads_count(driver)
        result['ads_before_cutoff'] = filtered_ads
        print(f"✅ Ads before {CUTOFF_DATE}: {filtered_ads}")

        # Classification
        if filtered_ads is not None:
            if filtered_ads == 0:
                result['classification'] = 'new_advertiser_30d'
            else:
                result['classification'] = 'old_advertiser'

        # Print final result
        print(f"\n{'=' * 80}")
        print("📊 FINAL RESULT")
        print(f"{'=' * 80}")
        print(f"\n🌐 Domain: {DOMAIN}")
        print(f"📅 Today: {TODAY}")
        print(f"📅 Cutoff: {CUTOFF_DATE}")
        print(f"\n📊 Total ads (all time): {result['total_ads']}")
        print(f"📊 Ads before cutoff: {result['ads_before_cutoff']}")
        print(f"\n🏷️  CLASSIFICATION: {result['classification']}")

        if result['classification'] == 'new_advertiser_30d':
            print(f"   🆕 NEW ADVERTISER - Started AFTER {CUTOFF_DATE}")
        elif result['classification'] == 'old_advertiser':
            print(f"   👴 OLD ADVERTISER - Had ads BEFORE {CUTOFF_DATE}")

        print(f"\n📸 Screenshots:")
        for ss in result['screenshots']:
            print(f"   {ss}")

        # Keep browser open for verification
        print("\n⏸️  Keeping browser open for 5 seconds...")
        time.sleep(5)

    finally:
        driver.quit()

    print("\n✅ Done!")
    return result


if __name__ == '__main__':
    result = main()
