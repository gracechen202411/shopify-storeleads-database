#!/usr/bin/env python3
"""
测试版：检查 20 个域名并同步到数据库
让用户去 Vercel 前端验证
"""

import psycopg2
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

TEST_LIMIT = 20


class QuickTestChecker:
    """快速测试检查器（20个域名）"""

    def __init__(self):
        self.conn = None
        self.driver = None
        self.results = []

    def connect_db(self):
        """连接数据库"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            print(f"✅ 数据库连接成功\n")
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False

    def init_browser(self):
        """初始化浏览器"""
        print("🌐 启动 Chrome 浏览器...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=chrome_options)
        self.driver = driver
        print("✅ 浏览器启动成功\n")

    def check_ads(self, domain):
        """检查广告"""
        check_domain = domain.replace('www.', '')
        url = f"https://adstransparency.google.com/?region=anywhere&domain={check_domain}"

        try:
            self.driver.get(url)

            try:
                wait = WebDriverWait(self.driver, 8)
                wait.until(lambda d: '个广告' in d.find_element(By.TAG_NAME, 'body').text)
                time.sleep(1)
            except:
                pass

            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            match = re.search(r'~?(\d+)\+?\s*个广告', page_text)

            if match:
                ads_count = int(match.group(1))
                customer_type = 'never_advertised' if ads_count == 0 else 'has_ads'
                return {
                    'domain': domain,
                    'has_ads': ads_count > 0,
                    'ad_count': ads_count,
                    'customer_type': customer_type,
                    'google_ads_url': url,
                    'error': None
                }
            elif '未找到任何广告' in page_text:
                return {
                    'domain': domain,
                    'has_ads': False,
                    'ad_count': 0,
                    'customer_type': 'never_advertised',
                    'google_ads_url': url,
                    'error': None
                }
            else:
                return {
                    'domain': domain,
                    'has_ads': True,
                    'ad_count': -1,
                    'customer_type': 'has_ads',
                    'google_ads_url': url,
                    'error': None
                }

        except Exception as e:
            return {
                'domain': domain,
                'has_ads': False,
                'ad_count': 0,
                'customer_type': 'error',
                'error': str(e)
            }

    def batch_update_database(self):
        """批量更新数据库"""
        try:
            cur = self.conn.cursor()
            updated = 0

            for result in self.results:
                if result['error']:
                    continue

                domain = result['domain']
                customer_type = result['customer_type']
                ad_count = result['ad_count']
                google_ads_url = result.get('google_ads_url')
                has_google_ads = result['has_ads']
                is_new_customer = None if customer_type == 'has_ads' else False

                cur.execute("""
                    UPDATE stores
                    SET customer_type = %s,
                        ads_check_level = 'quick_test_20',
                        ads_last_checked = NOW(),
                        has_google_ads = %s,
                        is_new_customer = %s,
                        google_ads_count = %s,
                        google_ads_url = %s
                    WHERE domain = %s
                """, (customer_type, has_google_ads, is_new_customer, ad_count, google_ads_url, domain))

                updated += 1

            self.conn.commit()
            cur.close()

            print(f"\n💾 批量更新 {updated} 个域名到数据库")
            return True

        except Exception as e:
            print(f"\n❌ 批量更新失败: {e}")
            self.conn.rollback()
            return False

    def run(self):
        """运行测试"""
        print("="*100)
        print("🧪 快速测试：检查 20 个域名并同步到数据库")
        print("="*100)
        print()

        if not self.connect_db():
            return

        self.init_browser()

        # 获取测试域名
        cur = self.conn.cursor()
        cur.execute("""
            SELECT domain, estimated_monthly_visits, country_code
            FROM stores
            WHERE country_code IN ('CN', 'HK')
              AND estimated_monthly_visits >= 10000
            ORDER BY estimated_monthly_visits DESC
            LIMIT %s
        """, (TEST_LIMIT,))

        test_domains = cur.fetchall()
        cur.close()

        print(f"📊 测试域名（访问量 Top 20）:")
        print("-"*100)
        for i, (domain, visits, country) in enumerate(test_domains, 1):
            flag = '🇨🇳' if country == 'CN' else '🇭🇰'
            print(f"  {i:2d}. {domain:40s} {visits:>10,} 访问/月 {flag}")
        print()

        print("="*100)
        print("🚀 开始检查...")
        print("="*100)
        print()

        start_time = time.time()

        for i, (domain, visits, country) in enumerate(test_domains, 1):
            flag = '🇨🇳' if country == 'CN' else '🇭🇰'
            print(f"[{i}/{TEST_LIMIT}] {domain} ({visits:,}/月 {flag})...", end=' ')

            result = self.check_ads(domain)
            self.results.append(result)

            status = '✅' if result['has_ads'] else '⭕'
            print(f"{status} {result['ad_count']} 个广告")

            time.sleep(0.5)

        elapsed = time.time() - start_time

        # 批量更新数据库
        print()
        print("="*100)
        print("💾 更新数据库...")
        print("="*100)
        self.batch_update_database()

        # 统计
        print()
        print("="*100)
        print("📊 测试完成！")
        print("="*100)
        print()
        print(f"⏱️  总耗时: {elapsed:.2f} 秒")
        print(f"📈 平均速度: {elapsed/TEST_LIMIT:.2f} 秒/域名")
        print()

        has_ads = sum(1 for r in self.results if r['has_ads'])
        no_ads = sum(1 for r in self.results if not r['has_ads'])

        print(f"统计结果:")
        print(f"  ✅ 有广告: {has_ads} 个")
        print(f"  ⭕ 无广告 (never_advertised): {no_ads} 个")
        print()

        # 显示 never_advertised 的域名
        print("="*100)
        print("🎯 从未投放广告的店铺（潜在客户）:")
        print("="*100)
        never_advertised = [r for r in self.results if r['customer_type'] == 'never_advertised']
        if never_advertised:
            for r in never_advertised:
                # 获取访问量
                visits = next((v for d, v, c in test_domains if d == r['domain']), 0)
                print(f"  🎯 {r['domain']} - {visits:,} 访问/月")
        else:
            print("  (无)")
        print()

        # 验证数据库
        print("="*100)
        print("🔍 验证数据库同步...")
        print("="*100)
        cur = self.conn.cursor()
        cur.execute("""
            SELECT domain, google_ads_count, customer_type, ads_last_checked
            FROM stores
            WHERE ads_check_level = 'quick_test_20'
            ORDER BY estimated_monthly_visits DESC
            LIMIT 5
        """)

        print("数据库中的前 5 条记录:")
        for domain, ads_count, customer_type, checked_at in cur.fetchall():
            status = '✅' if ads_count > 0 else '⭕'
            print(f"  {status} {domain}: {ads_count} 个广告, {customer_type}, {checked_at}")

        cur.close()

        print()
        print("="*100)
        print("✅ 数据已同步到 Neon 数据库！")
        print("="*100)
        print()
        print("💡 下一步：")
        print("  1. 去您的 Vercel 前端查看数据")
        print("  2. 搜索这些域名，应该能看到广告数据")
        print("  3. 确认数据正确后，可以运行完整版（6251个域名）")
        print()

        if self.driver:
            self.driver.quit()
        if self.conn:
            self.conn.close()


def main():
    checker = QuickTestChecker()
    checker.run()


if __name__ == '__main__':
    main()
