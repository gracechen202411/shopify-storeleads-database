#!/usr/bin/env python3
"""
Stage 2: Precise date-based verification using URL parameters
Uses direct URL with date parameters to check if ads existed 30 days ago
Much faster and more reliable than clicking filters!
"""

import psycopg2
import time
import re
from datetime import datetime, timedelta
from selenium import webdriver
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


class Stage2DateChecker:
    """Stage 2: Check if store had ads 30 days ago using URL parameters"""

    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()
        self.driver = None

    def init_browser(self, headless=True):
        """Initialize Selenium browser"""
        print("Starting Chrome browser...")
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        self.driver = webdriver.Chrome(options=chrome_options)
        print("✅ Browser started successfully")
        if not headless:
            print("💡 Browser is visible - you can see what's happening!")

    def check_ads_on_date(self, domain, check_date):
        """
        Check if domain had ads BEFORE a specific cutoff date using URL parameters

        Args:
            domain: Domain to check (www. will be removed)
            check_date: Cutoff date to check (datetime object) - checks if had ads BEFORE this date

        Returns:
            dict with had_ads_before_date (bool) and ads_count (int)
        """
        # Remove www. prefix
        check_domain = domain.replace('www.', '') if domain.startswith('www.') else domain

        # Format cutoff date as YYYY-MM-DD
        # We check from a very old date (2018-05-31 when Google Ads Transparency started)
        # up to the day BEFORE the cutoff (to exclude the cutoff day itself)
        end_date = (check_date - timedelta(days=1)).strftime('%Y-%m-%d')  # One day before cutoff
        start_date = "2018-05-31"  # When Google Ads Transparency started

        # Build URL to check ads from start_date to end_date (30 days ago)
        url = f"https://adstransparency.google.com/?region=anywhere&domain={check_domain}&start-date={start_date}&end-date={end_date}"

        try:
            self.driver.get(url)

            # Wait for page to load and show results
            try:
                wait = WebDriverWait(self.driver, 20)
                wait.until(lambda driver: "个广告" in driver.find_element(By.TAG_NAME, 'body').text or "未找到任何广告" in driver.find_element(By.TAG_NAME, 'body').text)
                time.sleep(2)  # Additional stabilization
            except:
                pass

            # Get page text
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text

            # Check for ads count
            match = re.search(r'~?(\d+)\+?\s*个广告', page_text)
            if match:
                ads_count = int(match.group(1))
                return {
                    'had_ads_before_cutoff': ads_count > 0,
                    'ads_count': ads_count,
                    'check_url': url
                }

            # Check for "no ads" message
            if '未找到任何广告' in page_text:
                return {
                    'had_ads_before_cutoff': False,
                    'ads_count': 0,
                    'check_url': url
                }

            # If uncertain, be conservative
            return {
                'had_ads_before_cutoff': None,
                'ads_count': -1,
                'check_url': url
            }

        except Exception as e:
            print(f"❌ Error checking {domain} on {date_str}: {e}")
            return None

    def classify_store(self, domain, current_ads_count):
        """
        Classify store based on whether it had ads 30 days ago

        Args:
            domain: Domain to check
            current_ads_count: Number of ads currently (from Stage 1)

        Returns:
            dict with customer_type and supporting data
        """
        # Check 30 days ago
        cutoff_date = datetime.now() - timedelta(days=30)

        result = self.check_ads_on_date(domain, cutoff_date)

        if not result:
            return None

        had_ads_before_cutoff = result['had_ads_before_cutoff']
        ads_count_before_cutoff = result['ads_count']

        # Classification logic
        if had_ads_before_cutoff is False:
            # No ads before cutoff (30 days ago), has ads now → new advertiser
            customer_type = 'new_advertiser_30d'
        elif had_ads_before_cutoff is True:
            # Had ads before cutoff → old advertiser
            customer_type = 'old_advertiser'
        else:
            # Uncertain, mark for manual review
            customer_type = 'needs_manual_review'

        return {
            'customer_type': customer_type,
            'ads_count_before_cutoff': ads_count_before_cutoff,
            'check_url': result['check_url'],
            'check_date': cutoff_date.strftime('%Y-%m-%d')
        }

    def update_store(self, domain, result):
        """Update store in database with Stage 2 results"""
        if not result:
            return False

        try:
            self.cur.execute("""
                UPDATE stores
                SET customer_type = %s,
                    ads_check_level = 'precise',
                    has_google_ads = %s,
                    is_new_customer = %s
                WHERE domain = %s
            """, (
                result['customer_type'],
                True,  # has_google_ads (Stage 2 only runs on stores with ads)
                result['customer_type'] == 'new_advertiser_30d',  # is_new_customer
                domain
            ))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"❌ Database update error: {e}")
            self.conn.rollback()
            return False

    def get_has_ads_stores(self, min_visits=1000):
        """Get stores marked as 'has_ads' that need Stage 2 verification"""
        self.cur.execute("""
            SELECT domain, google_ads_count, estimated_monthly_visits, city
            FROM stores
            WHERE customer_type = 'has_ads'
            AND estimated_monthly_visits >= %s
            AND (city LIKE '%%杭州%%' OR city LIKE '%%Hangzhou%%'
                 OR city LIKE '%%浙江%%' OR city LIKE '%%Zhejiang%%'
                 OR city LIKE '%%宁波%%' OR city LIKE '%%Ningbo%%'
                 OR city LIKE '%%温州%%' OR city LIKE '%%Wenzhou%%'
                 OR city LIKE '%%嘉兴%%' OR city LIKE '%%Jiaxing%%'
                 OR city LIKE '%%金华%%' OR city LIKE '%%Jinhua%%'
                 OR city LIKE '%%绍兴%%' OR city LIKE '%%Shaoxing%%'
                 OR city LIKE '%%湖州%%' OR city LIKE '%%Huzhou%%'
                 OR city LIKE '%%衢州%%' OR city LIKE '%%Quzhou%%'
                 OR city LIKE '%%台州%%' OR city LIKE '%%Taizhou%%'
                 OR city LIKE '%%丽水%%' OR city LIKE '%%Lishui%%'
                 OR city LIKE '%%舟山%%' OR city LIKE '%%Zhoushan%%')
            ORDER BY estimated_monthly_visits DESC
        """, (min_visits,))

        return self.cur.fetchall()

    def close(self):
        """Close browser and database connections"""
        if self.driver:
            self.driver.quit()
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()


def main():
    print("=" * 100)
    print("🔍 阶段二：精确日期验证 (Stage 2: Precise Date Check)")
    print("=" * 100)
    print()
    print("功能：检查店铺 30 天前是否有广告")
    print("方法：使用 URL 日期参数直接查询")
    print()

    checker = Stage2DateChecker()

    # Get stores that need Stage 2 check
    stores = checker.get_has_ads_stores(min_visits=1000)

    print(f"找到 {len(stores)} 个需要 Stage 2 验证的店铺 (has_ads)")
    print()

    if not stores:
        print("没有需要验证的店铺")
        return

    # Show examples
    print("示例店铺：")
    for i, (domain, ads_count, visits, city) in enumerate(stores[:10], 1):
        print(f"  {i}. {domain} - {ads_count} 广告 - {visits:,} 访问/月 - {city}")
    if len(stores) > 10:
        print(f"  ... 还有 {len(stores) - 10} 个店铺")
    print()

    print(f"自动开始验证这 {len(stores)} 个店铺...")
    print()
    print("=" * 100)
    print("开始验证...")
    print("=" * 100)
    print()

    checker.init_browser(headless=True)

    results = {
        'new_advertiser_30d': [],
        'old_advertiser': [],
        'needs_manual_review': [],
        'failed': []
    }

    for i, (domain, current_ads_count, visits, city) in enumerate(stores, 1):
        print(f"[{i}/{len(stores)}] {domain} ({current_ads_count} 广告)...", end=' ')

        result = checker.classify_store(domain, current_ads_count)

        if result:
            customer_type = result['customer_type']

            if customer_type == 'new_advertiser_30d':
                results['new_advertiser_30d'].append((domain, current_ads_count, result['ads_count_before_cutoff']))
                print(f"✅ 30天新广告主 (30天前 {result['ads_count_before_cutoff']} 广告)")
            elif customer_type == 'old_advertiser':
                results['old_advertiser'].append((domain, current_ads_count, result['ads_count_before_cutoff']))
                print(f"📅 老广告主 (30天前 {result['ads_count_before_cutoff']} 广告)")
            else:
                results['needs_manual_review'].append((domain, current_ads_count))
                print(f"⚠️  需要人工审核")

            # Update database
            checker.update_store(domain, result)
        else:
            results['failed'].append(domain)
            print("❌ 检测失败")

        time.sleep(2)  # Rate limiting

    checker.close()

    # Summary
    print()
    print("=" * 100)
    print("📊 Stage 2 验证结果")
    print("=" * 100)
    print()

    print(f"✅ 30天新广告主: {len(results['new_advertiser_30d'])} 个店铺")
    if results['new_advertiser_30d']:
        print("   这些是你要找的目标客户！")
        for domain, current_ads, ads_before_cutoff in results['new_advertiser_30d']:
            print(f"   - {domain} (当前 {current_ads} 广告, 30天前 {ads_before_cutoff} 广告)")
    print()

    print(f"📅 老广告主: {len(results['old_advertiser'])} 个店铺")
    if results['old_advertiser'][:5]:
        print("   示例：")
        for domain, current_ads, ads_before_cutoff in results['old_advertiser'][:5]:
            print(f"   - {domain} (当前 {current_ads} 广告, 30天前 {ads_before_cutoff} 广告)")
    print()

    if results['needs_manual_review']:
        print(f"⚠️  需要人工审核: {len(results['needs_manual_review'])} 个店铺")
        for domain, current_ads in results['needs_manual_review']:
            print(f"   - {domain} ({current_ads} 广告)")
        print()

    if results['failed']:
        print(f"❌ 检测失败: {len(results['failed'])} 个店铺")
        for domain in results['failed']:
            print(f"   - {domain}")
        print()

    print("=" * 100)
    print(f"✅ Stage 2 完成")
    print("=" * 100)


if __name__ == '__main__':
    main()
