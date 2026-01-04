#!/usr/bin/env python3
"""
超快速版本 - 优化所有等待时间
目标：1-2 秒/域名
"""

import psycopg2
import time
import re
from datetime import datetime
from pathlib import Path
import json
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

# 超快速配置
BATCH_SIZE = 20  # 批量更新
MAX_RETRIES = 1  # 减少重试（只重试1次）
PROGRESS_FILE = 'ultrafast_progress.json'
PAGE_TIMEOUT = 5  # 页面等待只等5秒
ELEMENT_TIMEOUT = 2  # 元素等待只等2秒
SLEEP_TIME = 0  # 不等待！


class UltraFastChecker:
    """超快速检查器"""

    def __init__(self):
        self.conn = None
        self.driver = None
        self.processed_domains = set()
        self.failed_domains = []
        self.current_batch = []
        self.total_checked = 0
        self.load_progress()

    def load_progress(self):
        """加载进度"""
        if Path(PROGRESS_FILE).exists():
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                progress = json.load(f)
                self.processed_domains = set(progress.get('processed', []))
                self.failed_domains = progress.get('failed', [])
                if self.processed_domains:
                    print(f"📦 加载进度: 已处理 {len(self.processed_domains)} 个域名")

    def save_progress(self):
        """保存进度"""
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'processed': list(self.processed_domains),
                'failed': self.failed_domains,
                'total_checked': self.total_checked,
                'updated_at': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)

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
        """初始化浏览器 - 超快速配置"""
        print("🌐 启动浏览器（超快速模式）...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')

        # 超快速优化
        chrome_options.add_argument('--disable-images')  # 不加载图片
        chrome_options.add_argument('--disable-javascript')  # 不执行JS（Google Ads页面不需要）
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.page_load_strategy = 'eager'  # 不等待完全加载

        self.driver = webdriver.Chrome(options=chrome_options)
        # 设置全局超时
        self.driver.set_page_load_timeout(PAGE_TIMEOUT)
        print("✅ 浏览器启动成功（超快速模式）\n")

    def check_ads(self, domain, retry_count=0):
        """检查广告 - 超快速版本"""
        check_domain = domain.replace('www.', '')
        url = f"https://adstransparency.google.com/?region=anywhere&domain={check_domain}"

        try:
            # 快速导航（不等待完全加载）
            self.driver.get(url)

            # 快速等待（只等2秒）
            try:
                wait = WebDriverWait(self.driver, ELEMENT_TIMEOUT)
                wait.until(lambda d: '个广告' in d.find_element(By.TAG_NAME, 'body').text)
            except:
                pass  # 超时就算了

            # 快速提取文本
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text

            # 快速解析
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
            # 只重试1次
            if retry_count < MAX_RETRIES:
                return self.check_ads(domain, retry_count + 1)
            else:
                self.failed_domains.append(domain)
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
                        ads_check_level = 'ultrafast',
                        ads_last_checked = NOW(),
                        has_google_ads = %s,
                        is_new_customer = %s,
                        google_ads_count = %s,
                        google_ads_url = %s
                    WHERE domain = %s
                """, (customer_type, has_google_ads, is_new_customer, ad_count, google_ads_url, domain))

                self.processed_domains.add(domain)
                updated += 1

            self.conn.commit()
            cur.close()

            print(f"  💾 批量更新 {updated} 个")

            self.save_progress()
            self.current_batch = []

            return True

        except Exception as e:
            print(f"  ❌ 更新失败: {e}")
            self.conn.rollback()
            return False

    def run(self):
        """运行检查"""
        print("="*100)
        print("⚡ 超快速批量检查器")
        print("="*100)
        print()

        if not self.connect_db():
            return

        self.init_browser()

        # 获取域名
        cur = self.conn.cursor()
        cur.execute("""
            SELECT domain, estimated_monthly_visits, country_code
            FROM stores
            WHERE country_code IN ('CN', 'HK')
              AND estimated_monthly_visits >= 1000
            ORDER BY estimated_monthly_visits DESC
        """)

        all_domains_data = cur.fetchall()
        cur.close()

        print(f"📊 总域名: {len(all_domains_data)}")
        print(f"✅ 已处理: {len(self.processed_domains)}")
        print(f"⏳ 待处理: {len(all_domains_data) - len(self.processed_domains)}")
        print()

        # 过滤已处理的
        to_check = [(d, v, c) for d, v, c in all_domains_data
                    if d not in self.processed_domains]

        if not to_check:
            print("✅ 全部完成！")
            return

        print("="*100)
        print(f"⚡ 开始检查 {len(to_check)} 个域名（超快速模式）...")
        print("="*100)
        print()

        start_time = time.time()

        for i, (domain, visits, country) in enumerate(to_check, 1):
            print(f"[{i}/{len(to_check)}] {domain}...", end=' ')

            result = self.check_ads(domain)
            self.current_batch.append(result)
            self.total_checked += 1

            status = '✅' if result['has_ads'] else '⭕'
            print(f"{status} {result['ad_count']}")

            # 批量更新
            if len(self.current_batch) >= BATCH_SIZE:
                self.batch_update_database()

            # 不等待！
            if SLEEP_TIME > 0:
                time.sleep(SLEEP_TIME)

            # 每100个显示进度
            if i % 100 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                remaining = (len(to_check) - i) * avg_time
                print(f"\n📊 [{i}/{len(to_check)}] 平均: {avg_time:.2f}秒/个, 剩余: {remaining/3600:.1f}小时\n")

        # 更新剩余
        if self.current_batch:
            self.batch_update_database()

        elapsed = time.time() - start_time

        # 报告
        print()
        print("="*100)
        print("📊 完成！")
        print("="*100)
        print(f"⏱️  总耗时: {elapsed/3600:.2f} 小时")
        print(f"✅ 成功: {len(self.processed_domains)}")
        print(f"❌ 失败: {len(self.failed_domains)}")
        if self.total_checked > 0:
            print(f"📈 平均: {elapsed/self.total_checked:.2f} 秒/个")
        print("="*100)

        if self.driver:
            self.driver.quit()
        if self.conn:
            self.conn.close()


def main():
    print()
    print("⚡ 超快速模式优化:")
    print("   - 不加载图片")
    print("   - 不执行 JavaScript")
    print("   - 页面等待只等 5 秒")
    print("   - 元素等待只等 2 秒")
    print("   - 不 sleep")
    print("   - 目标: 1-2 秒/域名")
    print()
    input("按 Enter 开始...")
    print()

    checker = UltraFastChecker()

    try:
        checker.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  中断！")
        checker.save_progress()
        if checker.driver:
            checker.driver.quit()
        if checker.conn:
            checker.conn.close()


if __name__ == '__main__':
    main()
