#!/usr/bin/env python3
"""
测试 100 个域名 - 平衡版
验证速度和准确性
"""

import psycopg2
import time
import re
import json
from datetime import datetime
from pathlib import Path
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

BATCH_SIZE = 20
TEST_LIMIT = 100


class Test100Checker:
    """测试100个域名"""

    def __init__(self):
        self.conn = None
        self.driver = None
        self.results = []
        self.current_batch = []

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
        """初始化浏览器 - 平衡配置"""
        print("🌐 启动浏览器（平衡配置：快速 + 准确）...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')

        prefs = {
            'profile.managed_default_content_settings.images': 2,
            'profile.default_content_setting_values': {'notifications': 2}
        }
        chrome_options.add_experimental_option('prefs', prefs)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(6)
        print("✅ 浏览器启动成功\n")

    def check_ads(self, domain):
        """检查广告"""
        check_domain = domain.replace('www.', '')
        url = f"https://adstransparency.google.com/?region=anywhere&domain={check_domain}"

        try:
            self.driver.get(url)

            try:
                wait = WebDriverWait(self.driver, 3)
                wait.until(lambda d: '个广告' in d.find_element(By.TAG_NAME, 'body').text)
                time.sleep(0.5)
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
        if not self.current_batch:
            return True

        try:
            cur = self.conn.cursor()
            updated = 0

            for result in self.current_batch:
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
                        ads_check_level = 'test_100_balanced',
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

            print(f"  💾 批量更新 {updated} 个域名")

            self.current_batch = []
            return True

        except Exception as e:
            print(f"  ❌ 批量更新失败: {e}")
            self.conn.rollback()
            return False

    def run(self):
        """运行测试"""
        print("="*100)
        print("🧪 测试 100 个域名 - 平衡版（快速 + 准确）")
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
              AND estimated_monthly_visits >= 5000
            ORDER BY estimated_monthly_visits DESC
            LIMIT %s
        """, (TEST_LIMIT,))

        test_domains = cur.fetchall()
        cur.close()

        print(f"📊 测试域名（访问量 Top 100）:")
        print(f"   选择标准：月访问量 >= 5000")
        print(f"   总数：{len(test_domains)} 个")
        print()

        print("="*100)
        print("⚡ 开始检查...")
        print("="*100)
        print()

        start_time = time.time()

        for i, (domain, visits, country) in enumerate(test_domains, 1):
            flag = '🇨🇳' if country == 'CN' else '🇭🇰'
            print(f"[{i}/{TEST_LIMIT}] {domain} ({visits:,}/月 {flag})...", end=' ')

            result = self.check_ads(domain)
            self.results.append(result)
            self.current_batch.append(result)

            status = '✅' if result['has_ads'] else '⭕'
            print(f"{status} {result['ad_count']}")

            # 批量更新
            if len(self.current_batch) >= BATCH_SIZE:
                self.batch_update_database()

        # 更新剩余
        if self.current_batch:
            self.batch_update_database()

        elapsed = time.time() - start_time

        # 统计
        print()
        print("="*100)
        print("📊 测试完成！")
        print("="*100)
        print()
        print(f"⏱️  总耗时: {elapsed:.2f} 秒 ({elapsed/60:.1f} 分钟)")
        print(f"📈 平均速度: {elapsed/TEST_LIMIT:.2f} 秒/域名")
        print()

        has_ads = sum(1 for r in self.results if r['has_ads'])
        no_ads = sum(1 for r in self.results if not r['has_ads'])
        errors = sum(1 for r in self.results if r['error'])

        print(f"统计结果:")
        print(f"  ✅ 有广告: {has_ads} 个")
        print(f"  ⭕ 无广告 (never_advertised): {no_ads} 个")
        print(f"  ❌ 错误: {errors} 个")
        print()

        # 按广告数量排序
        print("="*100)
        print("🏆 广告数量 Top 10:")
        print("="*100)
        sorted_results = sorted([r for r in self.results if r['ad_count'] > 0],
                               key=lambda x: x['ad_count'], reverse=True)[:10]
        for r in sorted_results:
            visits = next((v for d, v, c in test_domains if d == r['domain']), 0)
            print(f"  🎯 {r['domain']:40s} {r['ad_count']:>6,} 个广告  ({visits:,} 访问/月)")
        print()

        # never_advertised
        print("="*100)
        print("🎯 从未投放广告的店铺（潜在客户）:")
        print("="*100)
        never_advertised = [r for r in self.results if r['customer_type'] == 'never_advertised']
        if never_advertised:
            for r in never_advertised[:20]:
                visits = next((v for d, v, c in test_domains if d == r['domain']), 0)
                print(f"  💎 {r['domain']:40s} {visits:>10,} 访问/月")
            if len(never_advertised) > 20:
                print(f"  ... 还有 {len(never_advertised) - 20} 个")
        else:
            print("  (无)")
        print()

        # 验证数据库
        print("="*100)
        print("🔍 验证数据库同步...")
        print("="*100)
        cur = self.conn.cursor()
        cur.execute("""
            SELECT
                domain,
                google_ads_count,
                customer_type,
                ads_last_checked,
                estimated_monthly_visits
            FROM stores
            WHERE ads_check_level = 'test_100_balanced'
            ORDER BY google_ads_count DESC NULLS LAST
            LIMIT 5
        """)

        print("数据库中按广告数量排序（Top 5）:")
        for domain, ads_count, customer_type, checked_at, visits in cur.fetchall():
            status = '✅' if ads_count and ads_count > 0 else '⭕'
            ads_display = f'{ads_count:,}' if ads_count else '0'
            print(f"  {status} {domain:40s} {ads_display:>6s} 个广告, {customer_type:20s} ({visits:,} 访问/月)")
            print(f"     检查时间: {checked_at}")

        cur.close()

        # 预估完整运行
        print()
        print("="*100)
        print("📈 完整运行预估（6251 个店铺）:")
        print("="*100)
        total_time = (elapsed / TEST_LIMIT) * 6251
        print(f"  预计耗时: {total_time/3600:.1f} 小时")
        print(f"  平均速度: {elapsed/TEST_LIMIT:.2f} 秒/域名")
        print()

        print("="*100)
        print("✅ 测试完成！数据已同步到 Neon 数据库！")
        print("="*100)
        print()
        print("💡 下一步：")
        print("  1. 去 Vercel 前端搜索这些域名，验证数据")
        print("  2. 查看 ads_last_checked 字段（检测时间）")
        print("  3. 可以按 google_ads_count 排序筛选")
        print("  4. 确认无误后，运行完整版（6251个）")
        print()

        if self.driver:
            self.driver.quit()
        if self.conn:
            self.conn.close()


def main():
    checker = Test100Checker()
    checker.run()


if __name__ == '__main__':
    main()
