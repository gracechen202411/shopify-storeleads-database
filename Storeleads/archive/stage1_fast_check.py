#!/usr/bin/env python3
"""
阶段一：快速筛选（Fast Judge）
目标：识别 never_advertised 和 suspected_new_advertiser

关键约束：
1. SQL 层筛选：杭州/浙江 + 访问量 >= 100k
2. 30天去重：ads_last_checked
3. 分离存储：ads_check_level = 'fast'
4. 断点续传：实时写入数据库
5. 稳定性：单条失败不中断
"""

import psycopg2
import os
from playwright.async_api import async_playwright
import asyncio
import time
import re
from datetime import datetime

# 数据库配置（从环境变量读取）
DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}


class FastJudge:
    """阶段一：快速判断器"""

    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()

    def get_target_stores(self, min_visits=100000):
        """
        SQL 层筛选目标店铺

        约束：
        - 国家：CN
        - 地区：杭州/浙江
        - 访问量：>= min_visits
        - 30天未检查
        """
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

        stores = self.cur.fetchall()
        print(f"✅ SQL 筛选完成：找到 {len(stores)} 个目标店铺")
        return stores

    async def check_single_store(self, browser, domain):
        """
        检查单个店铺（快速判断）

        返回：
        - never_advertised: 从未打广告
        - suspected_new_advertiser: 疑似新客户（<10个广告）
        - skip: 老客户（>=10个广告）
        """
        url = f'https://adstransparency.google.com/?region=anywhere&domain={domain}'

        try:
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            await asyncio.sleep(2)

            content = await page.content()
            await page.close()

            # 判断逻辑
            if '0 个广告' in content or '未找到任何广告' in content:
                return {
                    'customer_type': 'never_advertised',
                    'ads_count': 0,
                    'message': '✅ 从未投放广告'
                }

            # 提取广告数量
            match = re.search(r'(\d+|~\d+)\s*个广告', content)
            if match:
                ads_count_str = match.group(1).replace('~', '')
                ads_count = int(ads_count_str)

                if ads_count < 10:
                    return {
                        'customer_type': 'suspected_new_advertiser',
                        'ads_count': ads_count,
                        'message': f'⚠️  疑似新客户（{ads_count}个广告）'
                    }
                else:
                    return {
                        'customer_type': 'skip',
                        'ads_count': ads_count,
                        'message': f'❌ 老客户（{ads_count}个广告）'
                    }

            # 无法判断
            return {
                'customer_type': 'skip',
                'ads_count': None,
                'message': '⚠️  无法提取广告数量'
            }

        except Exception as e:
            print(f"  ❌ 检查失败: {e}")
            return None

    def save_result(self, domain, result):
        """
        保存检查结果到数据库

        关键：
        - ads_check_level = 'fast'
        - 实时写入
        - 单条失败不中断
        """
        if result is None:
            return False

        try:
            self.cur.execute("""
                UPDATE stores
                SET
                    customer_type = %s,
                    google_ads_count = %s,
                    has_google_ads = %s,
                    ads_check_level = 'fast',
                    ads_last_checked = NOW()
                WHERE domain = %s
            """, (
                result['customer_type'],
                result['ads_count'],
                result['ads_count'] > 0 if result['ads_count'] is not None else None,
                domain
            ))
            self.conn.commit()
            return True

        except Exception as e:
            print(f"  ❌ 保存失败: {e}")
            self.conn.rollback()
            return False

    async def run(self, min_visits=100000):
        """主流程"""
        print("=" * 80)
        print("🚀 阶段一：快速筛选（Fast Judge）")
        print("=" * 80)
        print()

        # 1. SQL 筛选
        stores = self.get_target_stores(min_visits)

        if not stores:
            print("✅ 没有需要检查的店铺！")
            return

        print()
        print(f"目标店铺列表：")
        for i, (domain, visits, city, state) in enumerate(stores, 1):
            print(f"  {i}. {domain} - {visits:,} 访问/月 - {city or state}")
        print()

        # 2. 启动浏览器（异步模式）
        print("启动浏览器...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            print("✅ 浏览器已启动")
            print()

            # 3. 逐个检查
            results = {
                'never_advertised': [],
                'suspected_new_advertiser': [],
                'skip': []
            }

            for i, (domain, visits, city, state) in enumerate(stores, 1):
                print(f"[{i}/{len(stores)}] 检查 {domain}...")

                result = await self.check_single_store(browser, domain)

                if result:
                    print(f"  {result['message']}")

                    # 保存到数据库
                    if self.save_result(domain, result):
                        print(f"  💾 已保存到数据库")
                        results[result['customer_type']].append({
                            'domain': domain,
                            'visits': visits,
                            'ads_count': result['ads_count']
                        })

                print()
                await asyncio.sleep(1)  # 避免请求过快

            await browser.close()

        # 4. 统计结果
        print("=" * 80)
        print("📊 阶段一完成 - 统计结果")
        print("=" * 80)
        print()
        print(f"✅ never_advertised (从未投放): {len(results['never_advertised'])} 个")
        for store in results['never_advertised']:
            print(f"   - {store['domain']} ({store['visits']:,} 访问/月)")

        print()
        print(f"⚠️  suspected_new_advertiser (疑似新客户): {len(results['suspected_new_advertiser'])} 个")
        print(f"   👉 这些店铺需要进入阶段二（精确判断）")
        for store in results['suspected_new_advertiser']:
            print(f"   - {store['domain']} ({store['ads_count']} 个广告, {store['visits']:,} 访问/月)")

        print()
        print(f"❌ skip (老客户): {len(results['skip'])} 个")
        for store in results['skip']:
            print(f"   - {store['domain']} ({store['ads_count']} 个广告)")

        print()
        print("=" * 80)
        print("✅ 阶段一执行完毕！")
        print()
        print("下一步：")
        if results['suspected_new_advertiser']:
            print(f"运行阶段二，精确判断 {len(results['suspected_new_advertiser'])} 个疑似新客户")
        else:
            print("没有疑似新客户，阶段二可跳过")
        print("=" * 80)

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()


async def main():
    """入口函数"""
    import sys

    # 访问量门槛（默认 100k）
    min_visits = int(sys.argv[1]) if len(sys.argv) > 1 else 100000

    print(f"参数：最小访问量 = {min_visits:,}/月")
    print()

    judge = FastJudge()

    try:
        await judge.run(min_visits)
    finally:
        judge.close()


if __name__ == '__main__':
    asyncio.run(main())
