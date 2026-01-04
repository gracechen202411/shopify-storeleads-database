#!/usr/bin/env python3
"""
测试版：使用 Selenium 检查 10 个域名
验证批量更新数据库功能
"""

import psycopg2
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# 数据库配置
DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

TEST_LIMIT = 10


class SeleniumBatchTester:
    """Selenium 批量测试器"""

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
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        self.driver = webdriver.Chrome(options=chrome_options)
        print("✅ 浏览器启动成功\n")

    def check_ads(self, domain):
        """检查单个域名的广告"""
        check_domain = domain.replace('www.', '') if domain.startswith('www.') else domain
        url = f"https://adstransparency.google.com/?region=anywhere&domain={check_domain}"

        try:
            self.driver.get(url)

            try:
                wait = WebDriverWait(self.driver, 20)
                wait.until(lambda driver: "个广告" in driver.find_element(By.TAG_NAME, 'body').text)
                time.sleep(2)
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

    def batch_update_database(self, results):
        """批量更新数据库"""
        try:
            cur = self.conn.cursor()
            updated = 0

            for result in results:
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
                        ads_check_level = 'test_selenium_batch',
                        ads_last_checked = NOW(),
                        has_google_ads = %s,
                        is_new_customer = %s,
                        google_ads_count = %s,
                        google_ads_url = %s
                    WHERE domain = %s
                """, (customer_type, has_google_ads, is_new_customer, ad_count, google_ads_url, domain))

                updated += 1

            # 批量 commit
            self.conn.commit()
            cur.close()

            print(f"  💾 批量更新 {updated} 个域名到数据库")
            return True

        except Exception as e:
            print(f"  ❌ 批量更新失败: {e}")
            self.conn.rollback()
            return False

    def run_test(self):
        """运行测试"""
        print("="*100)
        print("🧪 Selenium 批量测试（10 个域名）")
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

        print(f"📊 测试域名列表:")
        print("-"*100)
        for i, (domain, visits, country) in enumerate(test_domains, 1):
            flag = '🇨🇳' if country == 'CN' else '🇭🇰'
            print(f"  {i}. {domain} - {visits:,} 访问/月 {flag}")
        print()

        # 开始检查
        print("="*100)
        print("🚀 开始检查...")
        print("="*100)
        print()

        start_time = time.time()

        for i, (domain, visits, country) in enumerate(test_domains, 1):
            print(f"[{i}/{TEST_LIMIT}] 检查 {domain}...", end=' ')

            result = self.check_ads(domain)
            self.results.append(result)

            status = '✅' if result['has_ads'] else '⭕'
            error_msg = f" (错误: {result['error']})" if result['error'] else ''
            print(f"{status} {result['ad_count']} 个广告{error_msg}")

            time.sleep(1)  # 避免请求太快

        # 批量更新数据库
        print()
        print("="*100)
        print("💾 批量更新数据库...")
        print("="*100)
        self.batch_update_database(self.results)

        elapsed = time.time() - start_time

        # 统计报告
        print()
        print("="*100)
        print("📊 测试完成！")
        print("="*100)
        print()
        print(f"⏱️  总耗时: {elapsed:.2f} 秒")
        print(f"📈 平均速度: {elapsed/TEST_LIMIT:.2f} 秒/域名")
        print()

        has_ads_count = sum(1 for r in self.results if r['has_ads'])
        no_ads_count = sum(1 for r in self.results if not r['has_ads'])
        error_count = sum(1 for r in self.results if r['error'])

        print(f"统计结果:")
        print(f"  ✅ 有广告: {has_ads_count} 个")
        print(f"  ⭕ 无广告: {no_ads_count} 个")
        print(f"  ❌ 出错: {error_count} 个")
        print()

        # 显示详细结果
        print("="*100)
        print("📋 详细结果:")
        print("="*100)
        for r in self.results:
            status = '✅ 有广告' if r['has_ads'] else '⭕ 无广告'
            print(f"\n{r['domain']}:")
            print(f"  状态: {status}")
            print(f"  广告数: {r['ad_count']}")
            print(f"  客户类型: {r['customer_type']}")
            if r['error']:
                print(f"  错误: {r['error']}")

        print()
        print("="*100)
        print("✅ 数据库已更新（ads_check_level = 'test_selenium_batch'）")
        print("="*100)

        # 清理
        if self.driver:
            self.driver.quit()
        if self.conn:
            self.conn.close()


def main():
    tester = SeleniumBatchTester()
    tester.run_test()


if __name__ == '__main__':
    main()
