#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Ads Checker - Production Version
Features:
- Skip already checked domains (deduplication)
- Batch commit every 20 domains
- Progress saving for fault tolerance
- Optimized speed: ~2.8 sec/domain
- Option to re-check specific domains
"""

import time
import json
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

# Configuration
BATCH_SIZE = 20  # Batch commit every 20 domains
MAX_RETRIES = 2
PROGRESS_FILE = 'production_progress.json'
CHECK_LEVEL = 'production_v1'

class ProductionAdsChecker:
    def __init__(self, recheck_mode=False, test_limit=None):
        """
        Args:
            recheck_mode: If True, re-check already checked domains
            test_limit: If set, only check this many domains (for testing)
        """
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.driver = None
        self.current_batch = []
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        self.start_time = time.time()
        self.recheck_mode = recheck_mode
        self.test_limit = test_limit

    def setup_driver(self):
        """Setup optimized Chrome driver"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

        # Speed optimizations
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.add_experimental_option('prefs', {
            'profile.managed_default_content_settings.images': 2
        })

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(10)

    def get_domains_to_check(self):
        """Get list of domains that need to be checked"""
        cur = self.conn.cursor()

        if self.recheck_mode:
            # Re-check mode: check domains that have customer_type (already checked before)
            query = """
                SELECT domain
                FROM stores
                WHERE customer_type IS NOT NULL
                  AND customer_type <> ''
                ORDER BY estimated_monthly_visits DESC NULLS LAST
            """
        else:
            # Normal mode: only check unchecked domains (no customer_type)
            query = """
                SELECT domain
                FROM stores
                WHERE (customer_type IS NULL OR customer_type = '')
                ORDER BY estimated_monthly_visits DESC NULLS LAST
            """

        if self.test_limit:
            query += f" LIMIT {self.test_limit}"

        cur.execute(query)
        domains = [row[0] for row in cur.fetchall()]
        cur.close()

        return domains

    def check_domain(self, domain):
        """Check if domain has Google Ads"""
        try:
            # Build search URL (use domain parameter, not search-input)
            check_domain = domain.replace('www.', '')
            url = f'https://adstransparency.google.com/?region=anywhere&domain={check_domain}'

            self.driver.get(url)

            # Wait for page to load results
            wait = WebDriverWait(self.driver, 5)
            try:
                # Wait for Chinese "个广告" or English text to appear
                wait.until(lambda d: '个广告' in d.find_element(By.TAG_NAME, 'body').text or
                                     'ads' in d.find_element(By.TAG_NAME, 'body').text.lower())
                time.sleep(0.5)
            except:
                # Timeout means likely no ads
                pass

            # Check for ads
            try:
                # Wait for either ads container or no results message
                wait.until(
                    lambda d: d.find_elements(By.CSS_SELECTOR,
                        'creative-preview, .no-creatives-message, [class*="no-result"], [class*="NoResult"]')
                )

                # Check if there are ads
                ads = self.driver.find_elements(By.TAG_NAME, 'creative-preview')

                if ads and len(ads) > 0:
                    # Has ads - try to get count
                    try:
                        count_element = self.driver.find_element(By.CSS_SELECTOR,
                            '[class*="creative-count"], [class*="result-count"]')
                        count_text = count_element.text

                        # Parse count (e.g., "1,234 ads" or "1234")
                        import re
                        numbers = re.findall(r'[\d,]+', count_text)
                        if numbers:
                            ads_count = int(numbers[0].replace(',', ''))
                        else:
                            ads_count = len(ads) if len(ads) < 300 else -1
                    except:
                        # Can't get exact count, use -1 to indicate "has ads but count unknown"
                        ads_count = -1 if len(ads) >= 3 else len(ads)

                    google_ads_url = f'https://adstransparency.google.com/?region=anywhere&search-input={check_domain}'

                    return {
                        'domain': domain,
                        'has_ads': True,
                        'google_ads_count': ads_count,
                        'google_ads_url': google_ads_url,
                        'customer_type': 'has_ads',
                        'status': 'success'
                    }
                else:
                    # No ads found
                    return {
                        'domain': domain,
                        'has_ads': False,
                        'google_ads_count': 0,
                        'google_ads_url': None,
                        'customer_type': 'never_advertised',
                        'status': 'success'
                    }

            except TimeoutException:
                # Timeout = likely no ads
                return {
                    'domain': domain,
                    'has_ads': False,
                    'google_ads_count': 0,
                    'google_ads_url': None,
                    'customer_type': 'never_advertised',
                    'status': 'success'
                }

        except Exception as e:
            print(f"  ❌ Error checking {domain}: {str(e)}")
            return {
                'domain': domain,
                'has_ads': False,
                'google_ads_count': 0,
                'google_ads_url': None,
                'customer_type': 'error',
                'status': 'error',
                'error': str(e)
            }

    def batch_update_database(self):
        """Update database with current batch"""
        if not self.current_batch:
            return

        cur = self.conn.cursor()

        for result in self.current_batch:
            cur.execute("""
                UPDATE stores SET
                    customer_type = %s,
                    ads_check_level = %s,
                    ads_last_checked = NOW(),
                    has_google_ads = %s,
                    google_ads_count = %s,
                    google_ads_url = %s
                WHERE domain = %s
            """, (
                result['customer_type'],
                CHECK_LEVEL,
                result['has_ads'],
                result['google_ads_count'],
                result['google_ads_url'],
                result['domain']
            ))

        self.conn.commit()
        cur.close()

        print(f"  💾 已提交 {len(self.current_batch)} 条记录到数据库")
        self.current_batch = []

    def save_progress(self):
        """Save progress to file"""
        progress = {
            'processed_count': self.processed_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'last_update': datetime.now().isoformat()
        }

        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, indent=2)

    def run(self):
        """Main execution"""
        try:
            print("="*100)
            print("🚀 Google Ads Production Checker")
            print("="*100)
            print(f"Mode: {'RE-CHECK' if self.recheck_mode else 'NORMAL (skip checked)'}")
            if self.test_limit:
                print(f"Test Limit: {self.test_limit} domains")
            print()

            # Get domains to check
            domains = self.get_domains_to_check()
            total_domains = len(domains)

            print(f"📋 待检查域名: {total_domains:,}")
            print()

            if total_domains == 0:
                print("✅ 没有需要检查的域名！")
                return

            # Setup driver
            print("🔧 初始化浏览器...")
            self.setup_driver()
            print("✅ 浏览器就绪")
            print()

            print("="*100)
            print("开始检查...")
            print("="*100)

            # Process each domain
            for i, domain in enumerate(domains, 1):
                domain_start = time.time()

                # Check domain
                result = self.check_domain(domain)

                domain_time = time.time() - domain_start

                # Update counters
                self.processed_count += 1
                if result['status'] == 'success':
                    self.success_count += 1
                else:
                    self.error_count += 1

                # Add to batch
                self.current_batch.append(result)

                # Print result
                status_icon = "✅" if result['status'] == 'success' else "❌"
                ads_info = f"{result['google_ads_count']:,} ads" if result['has_ads'] else "无广告"
                print(f"{status_icon} [{i}/{total_domains}] {domain:40s} | {ads_info:15s} | {domain_time:.2f}s")

                # Batch commit every BATCH_SIZE domains
                if len(self.current_batch) >= BATCH_SIZE:
                    self.batch_update_database()
                    self.save_progress()

                # Show progress every 50 domains
                if i % 50 == 0:
                    elapsed = time.time() - self.start_time
                    avg_time = elapsed / i
                    remaining = (total_domains - i) * avg_time
                    print()
                    print(f"📊 进度: {i}/{total_domains} ({i/total_domains*100:.1f}%)")
                    print(f"⏱️  平均速度: {avg_time:.2f}s/域名")
                    print(f"⏳ 预计剩余: {remaining/60:.1f} 分钟")
                    print()

            # Commit remaining batch
            if self.current_batch:
                self.batch_update_database()
                self.save_progress()

            # Final summary
            total_time = time.time() - self.start_time
            print()
            print("="*100)
            print("✅ 检查完成！")
            print("="*100)
            print(f"总计: {self.processed_count} 域名")
            print(f"成功: {self.success_count}")
            print(f"错误: {self.error_count}")
            print(f"总耗时: {total_time/60:.1f} 分钟")
            print(f"平均速度: {total_time/self.processed_count:.2f} 秒/域名")

            # Show customer type breakdown
            cur = self.conn.cursor()
            cur.execute("""
                SELECT customer_type, COUNT(*)
                FROM stores
                WHERE ads_check_level = %s
                GROUP BY customer_type
                ORDER BY COUNT(*) DESC
            """, (CHECK_LEVEL,))

            print()
            print("📈 客户类型分布:")
            for ctype, count in cur.fetchall():
                print(f"  {ctype}: {count:,}")
            cur.close()

        finally:
            if self.driver:
                self.driver.quit()
            if self.conn:
                self.conn.close()


if __name__ == '__main__':
    import sys

    # Parse command line arguments
    recheck_mode = '--recheck' in sys.argv
    test_limit = None

    # Check for --limit argument
    for arg in sys.argv:
        if arg.startswith('--limit='):
            test_limit = int(arg.split('=')[1])

    # Run checker
    checker = ProductionAdsChecker(recheck_mode=recheck_mode, test_limit=test_limit)
    checker.run()
