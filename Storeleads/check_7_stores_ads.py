#!/usr/bin/env python3
"""
Check Google Ads for 7 specific stores and save to database
使用 Playwright 自动检查 7 个店铺的 Google Ads 信息并保存到数据库
"""

import psycopg2
import time
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

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


def check_google_ads(domain):
    """
    Check Google Ads for a domain using Playwright
    Returns: (customer_type, ads_count)
    """
    url = f"https://adstransparency.google.com/?region=anywhere&domain={domain}"

    print(f"\n🔍 Checking: {domain}")
    print(f"   URL: {url}")

    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate to URL
            page.goto(url, wait_until='networkidle', timeout=30000)

            # Wait for content to load
            time.sleep(2)

            # Get page content
            content = page.content()

            # Check for "0 个广告" or "未找到任何广告"
            if '0 个广告' in content or '未找到任何广告' in content or '0 ads' in content.lower():
                print(f"   ✅ Result: Never advertised (0 ads)")
                browser.close()
                return ('never_advertised', 0)

            # Try to extract ads count from patterns like "X 个广告" or "~X 个广告"
            patterns = [
                r'~?(\d+)\s*个广告',
                r'~?(\d+)\s*ads'
            ]

            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    ads_count = int(match.group(1))
                    if ads_count < 10:
                        customer_type = 'suspected_new_advertiser'
                        print(f"   ✅ Result: Suspected new advertiser ({ads_count} ads)")
                    else:
                        customer_type = 'skip'
                        print(f"   ✅ Result: Skip ({ads_count} ads >= 10)")

                    browser.close()
                    return (customer_type, ads_count)

            # If no match found, try to find any number
            print(f"   ⚠️  Could not parse ads count from page")
            browser.close()
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
    print("🚀 Google Ads Checker for 7 Stores")
    print("=" * 80)
    print(f"\n📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total stores to check: {len(STORES)}")

    results = {
        'never_advertised': [],
        'suspected_new_advertiser': [],
        'skip': [],
        'error': []
    }

    # Check each store
    for i, domain in enumerate(STORES, 1):
        print(f"\n{'=' * 80}")
        print(f"Progress: {i}/{len(STORES)}")
        print(f"{'=' * 80}")

        # Check Google Ads
        customer_type, ads_count = check_google_ads(domain)

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
