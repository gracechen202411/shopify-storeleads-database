#!/usr/bin/env python3
"""
PRECISE verification of buydecided.com's Google Ads history
检查 buydecided.com 在 2025-11-19 之前是否有 Google Ads

Task: Check if buydecided.com had Google Ads BEFORE 2025-11-19 (30 days ago)
Today: 2025-12-19
Cutoff date: 2025-11-19
"""

import time
import re
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os

# Target domain
DOMAIN = 'buydecided.com'
TODAY = date(2025, 12, 19)
CUTOFF_DATE = date(2025, 11, 19)  # 30 days ago

def create_driver():
    """Create and configure Chrome driver"""
    chrome_options = Options()
    # Keep browser visible for manual verification
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # Add language preference
    chrome_options.add_argument('--lang=en-US')
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US,en'})

    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"❌ Failed to create Chrome driver: {str(e)}")
        print("💡 Please make sure ChromeDriver is installed:")
        print("   brew install chromedriver")
        return None


def extract_total_ads_count(driver):
    """Extract total ads count from the page"""
    try:
        page_text = driver.find_element(By.TAG_NAME, 'body').text

        # Try multiple patterns to find ads count
        patterns = [
            r'(\d+)\s+ads?',  # English: "6 ads"
            r'(\d+)\s*个广告',  # Chinese: "6 个广告"
            r'(\d+)\s*件の広告',  # Japanese: "19 件の広告"
            r'~(\d+)\s+ads?',  # Approximate: "~6 ads"
            r'~(\d+)\s*个广告',  # Approximate Chinese
            r'~(\d+)\s*件の広告',  # Approximate Japanese
        ]

        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                count = int(match.group(1))
                print(f"✅ Found total ads count: {count}")
                return count

        # Check for "0 ads" or "no ads"
        if '0 ads' in page_text.lower() or 'no ads' in page_text.lower() or '0 个广告' in page_text or '0 件の広告' in page_text:
            print("✅ Found: 0 ads")
            return 0

        print("⚠️  Could not find ads count in page text")
        print(f"📄 Page text preview: {page_text[:500]}...")
        return None

    except Exception as e:
        print(f"❌ Error extracting ads count: {str(e)}")
        return None


def wait_for_date_filter_elements(driver, timeout=10):
    """Wait for and find date filter elements"""
    try:
        # Common date filter selectors
        selectors = [
            # Japanese text
            "//button[contains(text(), '全期間')]",  # "All time" in Japanese
            "//div[contains(text(), '全期間')]",
            "//span[contains(text(), '全期間')]",
            # English text
            "//button[contains(text(), 'Date')]",
            "//button[contains(text(), 'Custom')]",
            "//button[contains(text(), 'All time')]",
            # Chinese text
            "//button[contains(text(), '日期')]",
            "//button[contains(text(), '自定义')]",
            "//button[contains(text(), '全部时间')]",
            "//span[contains(text(), 'Date')]",
            "//span[contains(text(), 'Custom')]",
            # Input fields
            "//input[@type='date']",
            "//input[contains(@placeholder, 'date')]",
            "//input[contains(@aria-label, 'date')]",
            # Dropdowns
            "//select[contains(@aria-label, 'date')]",
            "//div[contains(@class, 'date-filter')]",
            "//div[contains(@class, 'date-picker')]",
            # Calendar icon
            "//button[contains(@aria-label, 'calendar')]",
            "//*[name()='svg' and contains(@class, 'calendar')]/..",
        ]

        for selector in selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"✅ Found date filter element with selector: {selector}")
                    print(f"   Element text: {elements[0].text}")
                    return elements[0]
            except:
                continue

        return None

    except Exception as e:
        print(f"❌ Error finding date filter: {str(e)}")
        return None


def check_ads_before_date(driver, domain, cutoff_date):
    """
    Check if domain had Google Ads BEFORE cutoff_date
    Returns: dict with detailed results
    """
    url = f"https://adstransparency.google.com/?region=anywhere&domain={domain}"

    print(f"\n{'=' * 80}")
    print(f"🔍 CHECKING: {domain}")
    print(f"{'=' * 80}")
    print(f"URL: {url}")
    print(f"Today: {TODAY}")
    print(f"Cutoff Date: {cutoff_date}")
    print(f"Task: Check if ads existed BEFORE {cutoff_date}")

    result = {
        'domain': domain,
        'url': url,
        'check_date': TODAY,
        'cutoff_date': cutoff_date,
        'total_ads_count': None,
        'ads_before_cutoff': None,
        'classification': None,
        'evidence': [],
        'screenshots': [],
        'notes': []
    }

    try:
        # Step 1: Navigate to URL
        print("\n📄 Step 1: Loading page...")
        driver.get(url)
        print("⏳ Waiting for page to load (5 seconds)...")
        time.sleep(5)

        # Take screenshot 1: Initial page
        screenshots_dir = "/Users/hangzhouweineng/Desktop/shopify-storeleads-database/Storeleads/screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)

        screenshot1 = f"{screenshots_dir}/{domain}_01_initial.png"
        driver.save_screenshot(screenshot1)
        result['screenshots'].append(screenshot1)
        print(f"📸 Screenshot saved: {screenshot1}")

        # Step 2: Extract total ads count
        print("\n📊 Step 2: Extracting total ads count...")
        total_ads = extract_total_ads_count(driver)
        result['total_ads_count'] = total_ads

        if total_ads is not None:
            result['evidence'].append(f"Total ads displayed on page: {total_ads}")

            if total_ads == 0:
                print("✅ Result: 0 ads total - never_advertised")
                result['classification'] = 'never_advertised'
                result['notes'].append("No ads found on Google Ads Transparency")
                return result
        else:
            result['notes'].append("Could not extract total ads count from page")

        # Step 3: Look for date filter
        print("\n🔍 Step 3: Looking for date filter...")
        date_filter = wait_for_date_filter_elements(driver)

        if date_filter:
            print("✅ Found date filter element")
            result['evidence'].append("Date filter element found on page")

            # Take screenshot 2: Before clicking date filter
            screenshot2 = f"{screenshots_dir}/{domain}_02_before_date_filter.png"
            driver.save_screenshot(screenshot2)
            result['screenshots'].append(screenshot2)
            print(f"📸 Screenshot saved: {screenshot2}")

            # Try to click date filter
            print("\n🖱️  Step 4: Attempting to click date filter...")
            try:
                date_filter.click()
                time.sleep(2)

                # Take screenshot 3: After clicking date filter
                screenshot3 = f"{screenshots_dir}/{domain}_03_date_filter_opened.png"
                driver.save_screenshot(screenshot3)
                result['screenshots'].append(screenshot3)
                print(f"📸 Screenshot saved: {screenshot3}")

                result['evidence'].append("Successfully clicked date filter")
                result['notes'].append("Date filter opened - MANUAL VERIFICATION NEEDED")

                # Look for date input fields
                print("\n🔍 Looking for date input fields...")
                date_inputs = driver.find_elements(By.XPATH, "//input[@type='date']")

                if date_inputs:
                    print(f"✅ Found {len(date_inputs)} date input field(s)")
                    result['evidence'].append(f"Found {len(date_inputs)} date input field(s)")

                    # Try to set end date to cutoff_date
                    if len(date_inputs) >= 2:
                        print(f"\n📅 Attempting to set END DATE to {cutoff_date}...")
                        try:
                            # Usually the second input is the end date
                            end_date_input = date_inputs[1]
                            end_date_input.clear()
                            end_date_input.send_keys(cutoff_date.strftime('%Y-%m-%d'))
                            time.sleep(2)

                            # Look for apply button
                            apply_buttons = driver.find_elements(By.XPATH,
                                "//button[contains(text(), 'Apply') or contains(text(), '应用') or contains(text(), 'OK') or contains(text(), '确定')]")

                            if apply_buttons:
                                print("🖱️  Clicking Apply button...")
                                apply_buttons[0].click()
                                time.sleep(3)

                                # Take screenshot 4: After applying date filter
                                screenshot4 = f"{screenshots_dir}/{domain}_04_date_filter_applied.png"
                                driver.save_screenshot(screenshot4)
                                result['screenshots'].append(screenshot4)
                                print(f"📸 Screenshot saved: {screenshot4}")

                                # Extract ads count after filter
                                print("\n📊 Extracting ads count after date filter...")
                                filtered_ads = extract_total_ads_count(driver)
                                result['ads_before_cutoff'] = filtered_ads

                                if filtered_ads is not None:
                                    result['evidence'].append(f"Ads count after date filter (before {cutoff_date}): {filtered_ads}")

                                    if filtered_ads == 0:
                                        result['classification'] = 'new_advertiser_30d'
                                        result['notes'].append(f"0 ads found before {cutoff_date} - Started advertising after cutoff date")
                                    else:
                                        result['classification'] = 'old_advertiser'
                                        result['notes'].append(f"{filtered_ads} ads found before {cutoff_date} - Was advertising before cutoff date")
                                else:
                                    result['notes'].append("Could not extract ads count after date filter - MANUAL VERIFICATION NEEDED")
                            else:
                                result['notes'].append("Could not find Apply button - MANUAL VERIFICATION NEEDED")

                        except Exception as e:
                            print(f"⚠️  Error setting date: {str(e)}")
                            result['notes'].append(f"Error setting date filter: {str(e)}")
                    else:
                        result['notes'].append("Not enough date input fields - MANUAL VERIFICATION NEEDED")
                else:
                    result['notes'].append("No date input fields found - MANUAL VERIFICATION NEEDED")

            except Exception as e:
                print(f"⚠️  Error clicking date filter: {str(e)}")
                result['notes'].append(f"Error clicking date filter: {str(e)}")
        else:
            print("⚠️  Date filter not found")
            result['notes'].append("Date filter not found on page")

            if total_ads and total_ads > 0:
                result['classification'] = 'has_ads_but_cannot_verify_date'
                result['notes'].append(f"Found {total_ads} ads but cannot apply date filter - MANUAL VERIFICATION NEEDED")

        # Final screenshot
        screenshot_final = f"{screenshots_dir}/{domain}_05_final.png"
        driver.save_screenshot(screenshot_final)
        result['screenshots'].append(screenshot_final)
        print(f"📸 Screenshot saved: {screenshot_final}")

        # Print page text preview
        print("\n📄 Page text preview (first 800 characters):")
        print("-" * 80)
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        print(page_text[:800])
        print("-" * 80)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        result['notes'].append(f"Error during check: {str(e)}")

        # Emergency screenshot
        try:
            screenshot_error = f"{screenshots_dir}/{domain}_error.png"
            driver.save_screenshot(screenshot_error)
            result['screenshots'].append(screenshot_error)
            print(f"📸 Error screenshot saved: {screenshot_error}")
        except:
            pass

    return result


def print_result(result):
    """Print formatted result"""
    print(f"\n{'=' * 80}")
    print(f"📊 FINAL RESULT FOR: {result['domain']}")
    print(f"{'=' * 80}")
    print(f"\n🌐 Domain: {result['domain']}")
    print(f"📅 Check Date: {result['check_date']}")
    print(f"📅 Cutoff Date: {result['cutoff_date']}")
    print(f"\n📊 RESULTS:")
    print(f"   Total ads count (all time): {result['total_ads_count']}")
    print(f"   Ads count before {result['cutoff_date']}: {result['ads_before_cutoff']}")
    print(f"\n🏷️  CLASSIFICATION: {result['classification']}")

    if result['classification']:
        classification_map = {
            'never_advertised': '❌ Never advertised - No Google Ads found',
            'new_advertiser_30d': '🆕 New advertiser (within 30 days) - Started advertising after 2025-11-19',
            'old_advertiser': '👴 Old advertiser - Had ads before 2025-11-19',
            'has_ads_but_cannot_verify_date': '⚠️  Has ads but date verification incomplete'
        }
        print(f"   {classification_map.get(result['classification'], result['classification'])}")

    print(f"\n📝 EVIDENCE:")
    for evidence in result['evidence']:
        print(f"   • {evidence}")

    print(f"\n📸 SCREENSHOTS:")
    for screenshot in result['screenshots']:
        print(f"   • {screenshot}")

    print(f"\n💡 NOTES:")
    for note in result['notes']:
        print(f"   • {note}")

    print(f"\n{'=' * 80}")


def main():
    print("=" * 80)
    print("🎯 PRECISE Google Ads History Verification")
    print("=" * 80)
    print(f"\n📅 Today's date: {TODAY}")
    print(f"📅 Cutoff date: {CUTOFF_DATE} (30 days ago)")
    print(f"🌐 Domain to check: {DOMAIN}")
    print(f"\n🎯 Task: Verify if {DOMAIN} had Google Ads BEFORE {CUTOFF_DATE}")

    # Create driver
    print("\n🌐 Initializing Chrome driver...")
    driver = create_driver()

    if not driver:
        print("\n❌ Failed to create web driver. Exiting.")
        return

    print("✅ Chrome driver initialized successfully")
    print("💡 Browser will stay open for manual verification if needed")

    try:
        # Check the domain
        result = check_ads_before_date(driver, DOMAIN, CUTOFF_DATE)

        # Print result
        print_result(result)

        # Keep browser open for a bit to ensure screenshots are saved
        print("\n⏸️  Keeping browser open for 3 seconds to ensure all data is captured...")
        time.sleep(3)

    finally:
        print("\n🔒 Closing web driver...")
        driver.quit()

    print("\n✅ Done!")
    print(f"\n📁 Screenshots saved in:")
    print(f"   /Users/hangzhouweineng/Desktop/shopify-storeleads-database/Storeleads/screenshots/")


if __name__ == '__main__':
    main()
