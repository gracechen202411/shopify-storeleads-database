#!/usr/bin/env python3
"""
测试版：只检查 10 个域名
用于验证新版本是否正常工作
"""

import asyncio
import psycopg2
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright 未安装，正在安装...")
    import subprocess
    subprocess.run(["pip3", "install", "playwright"], check=True)
    subprocess.run(["playwright", "install", "chromium"], check=True)
    from playwright.async_api import async_playwright

# 数据库配置
DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

# 测试配置
CONCURRENT_BROWSERS = 3  # 测试用少一点
TIMEOUT = 12000
TEST_LIMIT = 10  # 只测试 10 个


class TestChecker:
    """测试检查器"""

    def __init__(self):
        self.conn = None
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

    async def check_single_domain(self, page, domain: str) -> Optional[Dict]:
        """检查单个域名"""
        try:
            url = f'https://adstransparency.google.com/?region=anywhere&domain={domain}'
            await page.goto(url, timeout=TIMEOUT, wait_until='domcontentloaded')

            try:
                await page.wait_for_selector('text=/个广告/', timeout=3000)
            except:
                return {
                    'domain': domain,
                    'has_ads': False,
                    'ad_count': 0,
                    'customer_type': 'never_advertised',
                    'error': None
                }

            ad_count_element = await page.query_selector('generic:has-text("个广告")')
            if ad_count_element:
                ad_count_text = await ad_count_element.inner_text()
                has_ads = '0 个广告' not in ad_count_text and '未找到任何广告' not in ad_count_text

                ad_count = 0
                if has_ads:
                    if '~' in ad_count_text:
                        ad_count = int(ad_count_text.split('~')[1].split(' ')[0])
                    elif ad_count_text[0].isdigit():
                        ad_count = int(ad_count_text.split(' ')[0])

                customer_type = 'never_advertised' if ad_count == 0 else 'has_ads'

                return {
                    'domain': domain,
                    'has_ads': has_ads,
                    'ad_count': ad_count,
                    'customer_type': customer_type,
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

    def update_database(self, result: Dict):
        """更新单个域名到数据库"""
        if not result or result['error']:
            return False

        try:
            cur = self.conn.cursor()

            domain = result['domain']
            customer_type = result['customer_type']
            ad_count = result['ad_count']
            google_ads_url = result.get('google_ads_url')
            has_google_ads = result['has_ads']
            is_new_customer = None if customer_type == 'has_ads' else False

            cur.execute("""
                UPDATE stores
                SET customer_type = %s,
                    ads_check_level = 'test_reliable',
                    ads_last_checked = NOW(),
                    has_google_ads = %s,
                    is_new_customer = %s,
                    google_ads_count = %s,
                    google_ads_url = %s
                WHERE domain = %s
            """, (customer_type, has_google_ads, is_new_customer, ad_count, google_ads_url, domain))

            self.conn.commit()
            cur.close()
            return True

        except Exception as e:
            print(f"  ❌ 数据库更新失败: {e}")
            self.conn.rollback()
            return False

    async def run_test(self):
        """运行测试"""
        print("="*100)
        print("🧪 测试版：检查 10 个域名")
        print("="*100)
        print()

        if not self.connect_db():
            return

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

        domains = [d[0] for d in test_domains]

        # 开始测试
        print("="*100)
        print("🚀 开始检查...")
        print("="*100)
        print()

        start_time = time.time()

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )

            contexts = []
            for _ in range(min(CONCURRENT_BROWSERS, len(domains))):
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )
                contexts.append(context)

            # 分批处理
            for i in range(0, len(domains), CONCURRENT_BROWSERS):
                batch = domains[i:i + CONCURRENT_BROWSERS]
                tasks = []

                for idx, domain in enumerate(batch):
                    context = contexts[idx % len(contexts)]
                    page = await context.new_page()
                    task = asyncio.create_task(self.check_single_domain(page, domain))
                    tasks.append((task, page, domain))

                for task, page, domain in tasks:
                    try:
                        result = await task
                        self.results.append(result)

                        status = '✅' if result['has_ads'] else '⭕'
                        error_msg = f" (错误: {result['error']})" if result['error'] else ''

                        print(f"[{len(self.results)}/{len(domains)}] {status} {result['domain']}: {result['ad_count']} 个广告{error_msg}")

                        # 立即更新数据库
                        if self.update_database(result):
                            print(f"  💾 已更新到数据库")
                        else:
                            print(f"  ⚠️  数据库更新失败")

                    except Exception as e:
                        print(f"❌ 任务执行失败 {domain}: {e}")
                    finally:
                        await page.close()

            for context in contexts:
                await context.close()
            await browser.close()

        elapsed = time.time() - start_time

        # 统计报告
        print()
        print("="*100)
        print("📊 测试完成！")
        print("="*100)
        print()
        print(f"⏱️  总耗时: {elapsed:.2f} 秒")
        print(f"📈 平均速度: {elapsed/len(domains):.2f} 秒/域名")
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

        # 保存结果
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print()
        print("="*100)
        print(f"✅ 测试结果已保存到: test_results.json")
        print(f"✅ 数据库已更新（check_level = 'test_reliable'）")
        print("="*100)

        if self.conn:
            self.conn.close()


async def main():
    checker = TestChecker()
    await checker.run_test()


if __name__ == '__main__':
    asyncio.run(main())
