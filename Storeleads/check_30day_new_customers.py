#!/usr/bin/env python3
"""
检查30天内新客户 - 通过查看广告的时间范围
如果店铺30天前没有打广告，但现在有广告 → 30天内新客户
"""
import psycopg2
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import time

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

class NewCustomerChecker:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()
        self.playwright = None
        self.browser = None
        self.page = None

        # 计算30天前的日期
        self.today = datetime.now()
        self.date_30_days_ago = self.today - timedelta(days=30)
        self.date_180_days_ago = self.today - timedelta(days=180)

        print(f"今天: {self.today.strftime('%Y-%m-%d')}")
        print(f"30天前: {self.date_30_days_ago.strftime('%Y-%m-%d')}")
        print(f"180天前: {self.date_180_days_ago.strftime('%Y-%m-%d')}")
        print()

    def start_browser(self):
        """启动浏览器"""
        print("启动浏览器...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        print("✅ 浏览器已启动")
        print()

    def check_ad_date_range(self, domain):
        """
        检查广告的时间范围
        返回: {
            'has_current_ads': bool,  # 现在是否有广告
            'has_ads_before_30_days': bool,  # 30天前是否有广告
            'has_ads_before_180_days': bool,  # 180天前是否有广告
            'first_ad_date': str or None,  # 第一个广告的最后展示时间
            'total_ads': int
        }
        """
        print(f"检查 {domain}...")

        try:
            # 先检查是否有广告
            url = f'https://adstransparency.google.com/?region=anywhere&domain={domain}'
            self.page.goto(url, timeout=30000)
            time.sleep(2)

            content = self.page.content()

            # 检查是否有广告
            if '0 个广告' in content or '未找到任何广告' in content:
                print(f"  ❌ {domain}: 从来没打过广告")
                return {
                    'has_current_ads': False,
                    'has_ads_before_30_days': False,
                    'has_ads_before_180_days': False,
                    'first_ad_date': None,
                    'total_ads': 0,
                    'is_30_day_new_customer': True  # 从来没打过 = 新客户
                }

            # 有广告，获取广告数量
            import re
            ads_match = re.search(r'(\d+)\s*个广告', content)
            total_ads = int(ads_match.group(1)) if ads_match else 0

            print(f"  📊 {domain}: 有 {total_ads} 个广告")

            # 点击第一个广告查看详情
            try:
                # 等待广告列表加载
                time.sleep(2)

                # 查找第一个广告链接
                first_ad = self.page.query_selector('a[href*="/advertiser/"][href*="/creative/"]')
                if first_ad:
                    first_ad.click()
                    time.sleep(2)

                    # 获取广告详情页面内容
                    detail_content = self.page.content()

                    # 提取"最后展示时间"
                    date_match = re.search(r'最后展示时间：(\d{4})年(\d{1,2})月(\d{1,2})日', detail_content)
                    if date_match:
                        year = int(date_match.group(1))
                        month = int(date_match.group(2))
                        day = int(date_match.group(3))
                        first_ad_date = datetime(year, month, day)

                        print(f"  📅 最后展示时间: {first_ad_date.strftime('%Y-%m-%d')}")

                        # 判断是否是30天内新客户
                        has_ads_before_30_days = first_ad_date < self.date_30_days_ago
                        has_ads_before_180_days = first_ad_date < self.date_180_days_ago

                        # 新客户判断逻辑
                        # 1. 30天前没有广告，现在有广告 = 30天内新客户
                        # 2. 180天前有广告，但30-180天之间没有 = 也可能是重新启动的客户
                        is_30_day_new = not has_ads_before_30_days

                        if is_30_day_new:
                            print(f"  🔥 30天内新客户！")
                        elif has_ads_before_180_days:
                            print(f"  ⚠️  老客户（180天前就开始投放）")
                        else:
                            print(f"  ⚠️  30-180天内开始投放（不算新客户）")

                        return {
                            'has_current_ads': True,
                            'has_ads_before_30_days': has_ads_before_30_days,
                            'has_ads_before_180_days': has_ads_before_180_days,
                            'first_ad_date': first_ad_date.strftime('%Y-%m-%d'),
                            'total_ads': total_ads,
                            'is_30_day_new_customer': is_30_day_new
                        }
                    else:
                        print(f"  ⚠️  无法提取日期信息")
                else:
                    print(f"  ⚠️  找不到第一个广告链接")

            except Exception as e:
                print(f"  ❌ 获取广告详情失败: {e}")

            # 如果无法获取详细日期，保守处理
            return {
                'has_current_ads': True,
                'has_ads_before_30_days': None,  # 未知
                'has_ads_before_180_days': None,
                'first_ad_date': None,
                'total_ads': total_ads,
                'is_30_day_new_customer': None  # 未知
            }

        except Exception as e:
            print(f"  ❌ 检查失败: {e}")
            return None

    def check_stores(self, limit=10, country_code='CN'):
        """批量检查店铺"""
        print("="*80)
        print(f"🔍 检查30天内新客户")
        print("="*80)
        print()

        # 从数据库获取有广告的店铺
        self.cur.execute(f"""
            SELECT domain
            FROM stores
            WHERE country_code = %s
            AND estimated_monthly_visits > 10000
            ORDER BY estimated_monthly_visits DESC
            LIMIT %s
        """, (country_code, limit))

        stores = [row[0] for row in self.cur.fetchall()]
        print(f"找到 {len(stores)} 个店铺需要检查")
        print()

        self.start_browser()

        results = []
        for i, domain in enumerate(stores, 1):
            print(f"[{i}/{len(stores)}] 检查 {domain}")
            result = self.check_ad_date_range(domain)
            if result:
                results.append({
                    'domain': domain,
                    **result
                })
            print()
            time.sleep(2)  # 避免被封IP

        self.browser.close()
        self.playwright.stop()

        return results

    def save_results(self, results):
        """保存结果到数据库"""
        print("="*80)
        print("💾 保存结果到数据库")
        print("="*80)
        print()

        for result in results:
            domain = result['domain']

            try:
                self.cur.execute("""
                    UPDATE stores
                    SET
                        has_google_ads = %s,
                        google_ads_count = %s,
                        is_new_customer = %s,
                        ads_last_checked = NOW()
                    WHERE domain = %s
                """, (
                    result['has_current_ads'],
                    result['total_ads'],
                    result['is_30_day_new_customer'],
                    domain
                ))
                self.conn.commit()

                status = "🔥 30天内新客户" if result['is_30_day_new_customer'] else "老客户"
                print(f"✅ {domain}: {status} ({result['total_ads']}个广告)")

            except Exception as e:
                print(f"❌ {domain}: 保存失败 - {e}")
                self.conn.rollback()

        print()
        print("✅ 所有结果已保存")

    def close(self):
        """关闭连接"""
        self.cur.close()
        self.conn.close()

def main():
    import sys

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    country_code = sys.argv[2] if len(sys.argv) > 2 else 'CN'

    print(f"参数：检查 {limit} 个店铺，国家：{country_code}")
    print()

    checker = NewCustomerChecker()

    try:
        results = checker.check_stores(limit=limit, country_code=country_code)
        checker.save_results(results)

        # 打印统计
        print()
        print("="*80)
        print("📊 统计结果")
        print("="*80)
        new_customers = [r for r in results if r.get('is_30_day_new_customer')]
        print(f"总检查: {len(results)} 个店铺")
        print(f"🔥 30天内新客户: {len(new_customers)} 个")
        print()

        if new_customers:
            print("30天内新客户列表:")
            for r in new_customers:
                print(f"  - {r['domain']}: {r['total_ads']} 个广告")

    finally:
        checker.close()

if __name__ == '__main__':
    main()
