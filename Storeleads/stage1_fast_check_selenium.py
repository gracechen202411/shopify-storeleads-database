#!/usr/bin/env python3
"""
Stage 1: Fast Check with Selenium (Fixed for macOS)
Replace Playwright with Selenium + Chrome
"""

import psycopg2
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}


class FastJudgeSelenium:
    """Stage 1: Fast Judge using Selenium"""

    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()
        self.driver = None

    def init_browser(self, headless=False):
        """Initialize Chrome browser with Selenium"""
        print("Starting Chrome browser...")

        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        self.driver = webdriver.Chrome(options=chrome_options)
        print("✅ Browser started successfully")
        if not headless:
            print("💡 Browser is visible - you can see what's happening!")

    def get_target_stores(self, min_visits=100000):
        """Get target stores from database"""
        query = """
            SELECT domain, estimated_monthly_visits, city, state
            FROM stores
            WHERE country_code = 'CN'
              AND (
                city ILIKE %s OR city ILIKE %s
                OR region ILIKE %s OR state ILIKE %s
              )
              AND estimated_monthly_visits >= %s
              AND (
                ads_last_checked IS NULL
                OR ads_last_checked < NOW() - INTERVAL '30 days'
              )
            ORDER BY estimated_monthly_visits DESC
        """

        self.cur.execute(query, (
            '%Hangzhou%', '%杭州%',
            '%Zhejiang%', '%Zhejiang%',
            min_visits
        ))

        return self.cur.fetchall()

    def check_ads(self, domain):
        """
        Check Google Ads for a domain
        Returns: dict with customer_type, ads_count, and google_ads_url
        """
        # Remove www. prefix for Google Ads Transparency check
        # Google shows different results for www vs non-www domains
        check_domain = domain.replace('www.', '') if domain.startswith('www.') else domain
        url = f"https://adstransparency.google.com/?region=anywhere&domain={check_domain}"

        try:
            self.driver.get(url)

            # Wait for ads count element to be present (up to 20 seconds)
            # Looking for element with class "ads-count" that contains "个广告"
            try:
                wait = WebDriverWait(self.driver, 20)
                # Wait for any element containing "个广告" text
                wait.until(lambda driver: "个广告" in driver.find_element(By.TAG_NAME, 'body').text)
                time.sleep(3)  # Additional wait for content to stabilize
            except:
                # If timeout, proceed anyway (page might have no ads)
                pass

            # Get page text
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text

            # First try to extract ads count (supports formats: "6 个广告", "~300 个广告", "300+ 个广告")
            match = re.search(r'~?(\d+)\+?\s*个广告', page_text)
            if match:
                ads_count = int(match.group(1))

                # 0 means no ads
                if ads_count == 0:
                    return {'customer_type': 'never_advertised', 'ads_count': 0, 'google_ads_url': url}
                # Any ads > 0 needs Stage 2 verification
                else:
                    return {'customer_type': 'has_ads', 'ads_count': ads_count, 'google_ads_url': url}

            # If no number found, check for "未找到任何广告" message
            if '未找到任何广告' in page_text:
                return {'customer_type': 'never_advertised', 'ads_count': 0, 'google_ads_url': url}

            # If can't determine, mark as has_ads (conservative, needs Stage 2)
            return {'customer_type': 'has_ads', 'ads_count': -1, 'google_ads_url': url}

        except Exception as e:
            print(f"❌ Error checking {domain}: {e}")
            return None

    def update_store(self, domain, result):
        """Update store in database with both old and new fields"""
        if not result:
            return False

        try:
            customer_type = result['customer_type']
            ads_count = result['ads_count']

            # Map new fields to old fields for backward compatibility
            if customer_type == 'never_advertised':
                has_google_ads = False
                is_new_customer = False
            elif customer_type == 'has_ads':
                has_google_ads = True
                is_new_customer = None  # Unknown until Stage 2
            elif customer_type == 'new_advertiser_30d':
                has_google_ads = True
                is_new_customer = True
            elif customer_type == 'old_advertiser':
                has_google_ads = True
                is_new_customer = False
            else:  # unknown/error cases
                has_google_ads = True
                is_new_customer = None

            # Update both old and new fields, including Google Ads URL
            google_ads_url = result.get('google_ads_url')

            self.cur.execute("""
                UPDATE stores
                SET customer_type = %s,
                    ads_check_level = 'fast',
                    ads_last_checked = NOW(),
                    has_google_ads = %s,
                    is_new_customer = %s,
                    google_ads_count = %s,
                    google_ads_url = %s
                WHERE domain = %s
            """, (customer_type, has_google_ads, is_new_customer, ads_count, google_ads_url, domain))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Failed to update {domain}: {e}")
            self.conn.rollback()
            return False

    def run(self, min_visits=100000, headless=False):
        """Run Stage 1 check"""
        print("=" * 100)
        print("🚀 Stage 1: Fast Check (Selenium)")
        print("=" * 100)
        print()

        # Get target stores
        stores = self.get_target_stores(min_visits)
        print(f"✅ Found {len(stores)} target stores\n")

        if len(stores) == 0:
            print("No stores to check.")
            return

        # List stores
        print("Target stores:")
        for i, (domain, visits, city, state) in enumerate(stores, 1):
            print(f"  {i}. {domain} - {visits:,} visits/month - {city}")
        print()

        # Initialize browser
        self.init_browser(headless=headless)

        # Check each store
        results = {
            'never_advertised': [],
            'has_ads': [],
            'failed': []
        }

        print("=" * 100)
        print("Checking stores...")
        print("=" * 100)
        print()

        for i, (domain, visits, city, state) in enumerate(stores, 1):
            print(f"[{i}/{len(stores)}] Checking {domain}...", end=' ')

            result = self.check_ads(domain)

            if result:
                customer_type = result['customer_type']
                ads_count = result['ads_count']
                results[customer_type].append(domain)

                # Update database
                if self.update_store(domain, result):
                    icon = {
                        'never_advertised': '✅',
                        'has_ads': '📊'
                    }.get(customer_type, '❓')

                    print(f"{icon} {customer_type} ({ads_count} ads)")
                else:
                    print(f"❌ Failed to update database")
            else:
                results['failed'].append(domain)
                print("❌ Failed")

            time.sleep(2)  # Rate limiting

        # Summary
        print()
        print("=" * 100)
        print("📊 Summary")
        print("=" * 100)
        print()
        print(f"✅ Never advertised: {len(results['never_advertised'])} stores")
        for domain in results['never_advertised']:
            print(f"   - {domain}")
        print()

        print(f"📊 Has ads (needs Stage 2 verification): {len(results['has_ads'])} stores")
        for domain in results['has_ads']:
            print(f"   - {domain}")
        print()

        if results['failed']:
            print(f"❌ Failed: {len(results['failed'])} stores")
            for domain in results['failed']:
                print(f"   - {domain}")
            print()

        print("=" * 100)

    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        self.cur.close()
        self.conn.close()


def main():
    import sys

    min_visits = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    headless = '--headless' in sys.argv

    print(f"Minimum monthly visits: {min_visits:,}")
    print(f"Headless mode: {headless}")
    print()

    judge = FastJudgeSelenium()

    try:
        judge.run(min_visits, headless=headless)
    finally:
        judge.close()


if __name__ == '__main__':
    main()
