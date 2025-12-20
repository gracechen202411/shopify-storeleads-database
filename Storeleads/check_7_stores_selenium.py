#!/usr/bin/env python3
"""
Check Google Ads for 7 specific stores using Selenium and save to database
使用 Selenium 自动检查 7 个店铺的 Google Ads 信息并保存到数据库
"""

import psycopg2
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Database configuration
DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

# Stores to check
STORES = [
    'dokidokicos.com',
    'ventiontech.com',
    'uwowocosplay.com',
    'vograce.com',
    'cabletimetech.com',
    'joetoyss.com',
    'dolcewe.com'
]


def create_driver():
    """Create and configure Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"   ❌ Failed to create Chrome driver: {str(e)}")
        print("   💡 Trying Safari WebDriver instead...")
        # Try Safari as fallback
        try:
            driver = webdriver.Safari()
            return driver
        except:
            return None


def check_google_ads(driver, domain):
    """
    Check Google Ads for a domain using Selenium
    Returns: (customer_type, ads_count)
    """
    url = f"https://adstransparency.google.com/?region=anywhere&domain={domain}"

    print(f"\n🔍 Checking: {domain}")
    print(f"   URL: {url}")

    try:
        # Navigate to URL
        driver.get(url)

        # Wait for page to load
        time.sleep(3)

        # Get page source
        page_source = driver.page_source

        # Check for "0 个广告" or "未找到任何广告"
        if '0 个广告' in page_source or '未找到任何广告' in page_source or '0 ads' in page_source.lower():
            print(f"   ✅ Result: Never advertised (0 ads)")
            return ('never_advertised', 0)

        # Try to extract ads count from patterns like "X 个广告" or "~X 个广告"
        patterns = [
            r'~?(\d+)\s*个广告',
            r'~?(\d+)\s*ads'
        ]

        for pattern in patterns:
            match = re.search(pattern, page_source, re.IGNORECASE)
            if match:
                ads_count = int(match.group(1))
                if ads_count < 10:
                    customer_type = 'suspected_new_advertiser'
                    print(f"   ✅ Result: Suspected new advertiser ({ads_count} ads)")
                else:
                    customer_type = 'skip'
                    print(f"   ✅ Result: Skip ({ads_count} ads >= 10)")

                return (customer_type, ads_count)

        # If no match found, try to get text from specific elements
        try:
            # Look for elements that might contain ad count
            body_text = driver.find_element(By.TAG_NAME, 'body').text
            print(f"   ⚠️  Could not parse ads count. Page text preview:")
            print(f"   {body_text[:200]}...")
        except:
            pass

        print(f"   ⚠️  Could not parse ads count from page")
        return (None, None)

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return (None, None)


def save_to_database(domain, customer_type, ads_count):
    """Save results to database"""
    if customer_type is None:
        print(f"   ⏭️  Skipping database save (no valid data)")
        return False

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("""
            UPDATE stores
            SET customer_type = %s,
                google_ads_count = %s,
                has_google_ads = %s,
                ads_check_level = 'fast',
                ads_last_checked = NOW()
            WHERE domain = %s
        """, (customer_type, ads_count, ads_count > 0, domain))

        conn.commit()
        print(f"   💾 Saved to database: {domain} -> {customer_type}")

        cur.close()
        conn.close()
        return True

    except Exception as e:
        print(f"   ❌ Database error: {str(e)}")
        return False


def main():
    print("=" * 80)
    print("🚀 Google Ads Checker for 7 Stores (Selenium)")
    print("=" * 80)
    print(f"\n📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total stores to check: {len(STORES)}")

    # Create driver
    print("\n🌐 Initializing web driver...")
    driver = create_driver()

    if not driver:
        print("\n❌ Failed to create web driver. Please check your browser setup.")
        return

    print("✅ Web driver initialized successfully")

    results = {
        'never_advertised': [],
        'suspected_new_advertiser': [],
        'skip': [],
        'error': []
    }

    try:
        # Check each store
        for i, domain in enumerate(STORES, 1):
            print(f"\n{'=' * 80}")
            print(f"Progress: {i}/{len(STORES)}")
            print(f"{'=' * 80}")

            # Check Google Ads
            customer_type, ads_count = check_google_ads(driver, domain)

            # Save to database
            if customer_type:
                save_to_database(domain, customer_type, ads_count)
                results[customer_type].append({
                    'domain': domain,
                    'ads_count': ads_count
                })
            else:
                results['error'].append(domain)

            # Wait between requests
            if i < len(STORES):
                print("\n   ⏳ Waiting 3 seconds before next request...")
                time.sleep(3)

    finally:
        # Close driver
        print("\n🔒 Closing web driver...")
        driver.quit()

    # Print summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)

    print(f"\n✅ Never Advertised ({len(results['never_advertised'])}):")
    if results['never_advertised']:
        for item in results['never_advertised']:
            print(f"   - {item['domain']} (0 ads)")
    else:
        print("   (none)")

    print(f"\n⚠️  Suspected New Advertiser ({len(results['suspected_new_advertiser'])}):")
    if results['suspected_new_advertiser']:
        for item in results['suspected_new_advertiser']:
            print(f"   - {item['domain']} ({item['ads_count']} ads)")
    else:
        print("   (none)")

    print(f"\n⏭️  Skip ({len(results['skip'])}):")
    if results['skip']:
        for item in results['skip']:
            print(f"   - {item['domain']} ({item['ads_count']} ads)")
    else:
        print("   (none)")

    print(f"\n❌ Errors ({len(results['error'])}):")
    if results['error']:
        for domain in results['error']:
            print(f"   - {domain}")
    else:
        print("   (none)")

    print("\n" + "=" * 80)
    print("✅ Done!")
    print("=" * 80)


if __name__ == '__main__':
    main()
