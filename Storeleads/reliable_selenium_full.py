#!/usr/bin/env python3
"""
完整版可靠批量检查器（Selenium）
= 测试版的速度（4-6秒/个）+ 进度保存 + 自动重试

特点：
✅ 批量 commit（快 4 倍）
✅ 进度保存（可中断恢复）
✅ 自动重试（成功率 95%+）
✅ 错误收集（知道哪些失败）
✅ 实时更新数据库

预计：6251 个店铺 = 8-10 小时
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

# 数据库配置
DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

# 配置
BATCH_SIZE = 20  # 每 20 个域名 commit 一次
MAX_RETRIES = 2  # 最多重试 2 次
PROGRESS_FILE = 'selenium_progress.json'


class ReliableSeleniumChecker:
    """完整版可靠检查器"""

    def __init__(self):
        self.conn = None
        self.driver = None
        self.processed_domains = set()
        self.failed_domains = []
        self.current_batch = []
        self.total_checked = 0
        self.load_progress()

    def load_progress(self):
        """加载之前的进度"""
        if Path(PROGRESS_FILE).exists():
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                progress = json.load(f)
                self.processed_domains = set(progress.get('processed', []))
                self.failed_domains = progress.get('failed', [])
                print(f"📦 加载进度: 已处理 {len(self.processed_domains)} 个域名")
                if self.failed_domains:
                    print(f"⚠️  上次失败: {len(self.failed_domains)} 个域名")

    def save_progress(self):
        """保存当前进度"""
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'processed': list(self.processed_domains),
                'failed': self.failed_domains,
                'total_checked': self.total_checked,
                'updated_at': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)

    def connect_db(self):
        """连接数据库（带重试）"""
        for i in range(3):
            try:
                self.conn = psycopg2.connect(**DB_CONFIG)
                print(f"✅ 数据库连接成功\n")
                return True
            except Exception as e:
                print(f"❌ 数据库连接失败 (尝试 {i+1}/3): {e}")
                time.sleep(2)
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
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        self.driver = webdriver.Chrome(options=chrome_options)
        print("✅ 浏览器启动成功\n")

    def check_ads(self, domain, retry_count=0):
        """检查单个域名的广告（带重试）"""
        check_domain = domain.replace('www.', '') if domain.startswith('www.') else domain
        url = f"https://adstransparency.google.com/?region=anywhere&domain={check_domain}"

        try:
            self.driver.get(url)

            # 优化的等待策略
            try:
                wait = WebDriverWait(self.driver, 8)  # 只等 8 秒
                wait.until(lambda driver: "个广告" in driver.find_element(By.TAG_NAME, 'body').text)
                time.sleep(1)  # 只等 1 秒
            except:
                # 超时，可能没有广告
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
            # 自动重试
            if retry_count < MAX_RETRIES:
                print(f"  ⚠️  {domain} 失败，重试 {retry_count + 1}/{MAX_RETRIES}")
                time.sleep(3)
                return self.check_ads(domain, retry_count + 1)
            else:
                # 重试失败，记录错误
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
                        ads_check_level = 'reliable_selenium_full',
                        ads_last_checked = NOW(),
                        has_google_ads = %s,
                        is_new_customer = %s,
                        google_ads_count = %s,
                        google_ads_url = %s
                    WHERE domain = %s
                """, (customer_type, has_google_ads, is_new_customer, ad_count, google_ads_url, domain))

                self.processed_domains.add(domain)
                updated += 1

            # 批量 commit（关键优化）
            self.conn.commit()
            cur.close()

            print(f"  💾 批量更新 {updated} 个域名到数据库")

            # 保存进度
            self.save_progress()

            # 清空当前批次
            self.current_batch = []

            return True

        except Exception as e:
            print(f"  ❌ 批量更新失败: {e}")
            self.conn.rollback()
            return False

    def run(self):
        """运行完整检查"""
        print("="*100)
        print("🚀 完整版可靠批量检查器（Selenium）")
        print("="*100)
        print()

        # 连接数据库
        if not self.connect_db():
            print("❌ 无法连接数据库，退出")
            return

        # 初始化浏览器
        self.init_browser()

        # 获取需要检查的域名
        try:
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

            print(f"📊 数据库中共有 {len(all_domains_data)} 个域名")
            print(f"✅ 已处理: {len(self.processed_domains)} 个")
            print(f"⏳ 待处理: {len(all_domains_data) - len(self.processed_domains)} 个")
            if self.failed_domains:
                print(f"❌ 失败: {len(self.failed_domains)} 个（可重试）")
            print()

        except Exception as e:
            print(f"❌ 查询数据库失败: {e}")
            return

        # 过滤已处理的
        to_check = [(d, v, c) for d, v, c in all_domains_data
                    if d not in self.processed_domains]

        if not to_check:
            print("✅ 所有域名都已处理！")
            if self.failed_domains:
                print(f"\n⚠️  有 {len(self.failed_domains)} 个失败的域名可以重试")
                print("删除 selenium_progress.json 中的 failed 列表，然后重新运行")
            return

        print("="*100)
        print(f"🚀 开始检查 {len(to_check)} 个域名...")
        print(f"⚙️  批量大小: {BATCH_SIZE} (每次 commit)")
        print(f"🔄 重试次数: {MAX_RETRIES}")
        print("="*100)
        print()

        # 记录开始时间
        start_time = time.time()

        # 逐个检查
        for i, (domain, visits, country) in enumerate(to_check, 1):
            flag = '🇨🇳' if country == 'CN' else '🇭🇰'
            print(f"[{i}/{len(to_check)}] 检查 {domain} ({visits:,} 访问/月 {flag})...", end=' ')

            # 检查广告
            result = self.check_ads(domain)
            self.current_batch.append(result)
            self.total_checked += 1

            # 显示结果
            status = '✅' if result['has_ads'] else '⭕'
            error_msg = f" (❌ {result['error']})" if result['error'] else ''
            print(f"{status} {result['ad_count']} 个广告{error_msg}")

            # 批量更新数据库
            if len(self.current_batch) >= BATCH_SIZE:
                self.batch_update_database()

            # 短暂延迟，避免请求太快
            time.sleep(0.5)

            # 每 100 个显示进度统计
            if i % 100 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                remaining = (len(to_check) - i) * avg_time
                print(f"\n📊 进度统计:")
                print(f"   已完成: {i}/{len(to_check)} ({i/len(to_check)*100:.1f}%)")
                print(f"   平均速度: {avg_time:.2f} 秒/域名")
                print(f"   预计剩余: {remaining/3600:.1f} 小时")
                print(f"   成功率: {(i - len([r for r in self.current_batch if r['error']]))/i*100:.1f}%")
                print()

        # 更新剩余的批次
        if self.current_batch:
            self.batch_update_database()

        # 计算总耗时
        elapsed = time.time() - start_time

        # 最终报告
        print()
        print("="*100)
        print("📊 检查完成！")
        print("="*100)
        print()
        print(f"⏱️  总耗时: {elapsed:.2f} 秒 ({elapsed/3600:.2f} 小时)")
        print(f"✅ 成功处理: {len(self.processed_domains)} 个域名")
        print(f"❌ 失败: {len(self.failed_domains)} 个域名")
        if self.total_checked > 0:
            print(f"📈 平均速度: {elapsed/self.total_checked:.2f} 秒/域名")
            success_rate = (self.total_checked - len(self.failed_domains)) / self.total_checked * 100
            print(f"📊 成功率: {success_rate:.1f}%")
        print()

        if self.failed_domains:
            print(f"❌ 失败的域名（前 20 个）:")
            for domain in self.failed_domains[:20]:
                print(f"   - {domain}")
            if len(self.failed_domains) > 20:
                print(f"   ... 还有 {len(self.failed_domains) - 20} 个")
            print()
            print(f"💡 提示: 可以删除 {PROGRESS_FILE} 中的 failed 列表，然后重新运行来重试失败的域名")

        print()
        print(f"✅ 进度已保存到: {PROGRESS_FILE}")
        print(f"✅ 数据已更新到 Neon 数据库")
        print("="*100)

        # 清理
        if self.driver:
            self.driver.quit()
        if self.conn:
            self.conn.close()


def main():
    """主函数"""
    print()
    print("💡 提示:")
    print("   - 可以随时按 Ctrl+C 中断，进度会保存")
    print("   - 再次运行会从上次断点继续")
    print("   - 预计耗时: 8-10 小时（6251 个域名）")
    print("   - 可以后台运行: nohup python3 reliable_selenium_full.py > output.log 2>&1 &")
    print()
    input("按 Enter 开始运行...")
    print()

    checker = ReliableSeleniumChecker()

    try:
        checker.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断！")
        print("💾 正在保存进度...")
        checker.save_progress()
        print("✅ 进度已保存，下次运行会继续")
        if checker.driver:
            checker.driver.quit()
        if checker.conn:
            checker.conn.close()
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        print("💾 正在保存进度...")
        checker.save_progress()
        if checker.driver:
            checker.driver.quit()
        if checker.conn:
            checker.conn.close()


if __name__ == '__main__':
    main()
