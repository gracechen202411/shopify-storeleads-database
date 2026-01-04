#!/usr/bin/env python3
"""
可靠的批量 Google Ads 检查工具
解决问题：
1. ✅ 实时更新数据库（不会丢失）
2. ✅ 批量 commit（速度快）
3. ✅ 自动重试（容错性强）
4. ✅ 保存进度（中断可恢复）
5. ✅ 异步并发（速度更快）
"""

import asyncio
import psycopg2
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright 未安装")
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

# 配置
CONCURRENT_BROWSERS = 8  # 增加并发数
TIMEOUT = 12000  # 减少超时时间
BATCH_SIZE = 20  # 每 20 个域名 commit 一次
MAX_RETRIES = 2  # 最多重试 2 次
PROGRESS_FILE = 'batch_progress.json'


class ReliableBatchChecker:
    """可靠的批量检查器"""

    def __init__(self):
        self.conn = None
        self.processed_domains = set()
        self.failed_domains = []
        self.load_progress()

    def load_progress(self):
        """加载之前的进度"""
        if Path(PROGRESS_FILE).exists():
            with open(PROGRESS_FILE, 'r') as f:
                progress = json.load(f)
                self.processed_domains = set(progress.get('processed', []))
                print(f"📦 加载进度: 已处理 {len(self.processed_domains)} 个域名")

    def save_progress(self):
        """保存当前进度"""
        with open(PROGRESS_FILE, 'w') as f:
            json.dump({
                'processed': list(self.processed_domains),
                'failed': self.failed_domains,
                'updated_at': datetime.now().isoformat()
            }, f, indent=2)

    def connect_db(self):
        """连接数据库（带重试）"""
        for i in range(3):
            try:
                self.conn = psycopg2.connect(**DB_CONFIG)
                print(f"✅ 数据库连接成功")
                return True
            except Exception as e:
                print(f"❌ 数据库连接失败 (尝试 {i+1}/3): {e}")
                time.sleep(2)
        return False

    async def check_single_domain(self, page, domain: str, retry_count: int = 0) -> Optional[Dict]:
        """检查单个域名（带重试）"""
        try:
            # 去掉 www. 前缀，确保查询准确
            check_domain = domain.replace('www.', '').strip()
            url = f'https://adstransparency.google.com/?region=anywhere&domain={check_domain}'

            # 导航到页面
            await page.goto(url, timeout=TIMEOUT, wait_until='domcontentloaded')

            # 快速等待
            try:
                await page.wait_for_selector('text=/个广告/', timeout=3000)
            except:
                # 没找到，可能没有广告
                return {
                    'domain': domain,
                    'has_ads': False,
                    'ad_count': 0,
                    'customer_type': 'never_advertised',
                    'error': None
                }

            # 提取广告数量
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

                # 判断客户类型
                if ad_count == 0:
                    customer_type = 'never_advertised'
                else:
                    customer_type = 'has_ads'  # 需要进一步检查日期

                return {
                    'domain': domain,
                    'has_ads': has_ads,
                    'ad_count': ad_count,
                    'customer_type': customer_type,
                    'google_ads_url': url,
                    'error': None
                }
            else:
                return {
                    'domain': domain,
                    'has_ads': False,
                    'ad_count': 0,
                    'customer_type': 'never_advertised',
                    'error': None
                }

        except Exception as e:
            # 重试机制
            if retry_count < MAX_RETRIES:
                print(f"  ⚠️  {domain} 失败，重试 {retry_count + 1}/{MAX_RETRIES}")
                await asyncio.sleep(2)
                return await self.check_single_domain(page, domain, retry_count + 1)
            else:
                return {
                    'domain': domain,
                    'has_ads': False,
                    'ad_count': 0,
                    'customer_type': 'error',
                    'error': str(e)
                }

    def batch_update_database(self, results: List[Dict]):
        """批量更新数据库（更快更可靠）"""
        if not results:
            return

        try:
            cur = self.conn.cursor()

            # 批量更新
            for result in results:
                if result['error']:
                    # 记录失败的域名
                    self.failed_domains.append(result['domain'])
                    continue

                domain = result['domain']
                customer_type = result['customer_type']
                ad_count = result['ad_count']
                google_ads_url = result.get('google_ads_url')

                # 映射到旧字段
                has_google_ads = result['has_ads']
                is_new_customer = None if customer_type == 'has_ads' else False

                cur.execute("""
                    UPDATE stores
                    SET customer_type = %s,
                        ads_check_level = 'reliable_batch',
                        ads_last_checked = NOW(),
                        has_google_ads = %s,
                        is_new_customer = %s,
                        google_ads_count = %s,
                        google_ads_url = %s
                    WHERE domain = %s
                """, (customer_type, has_google_ads, is_new_customer, ad_count, google_ads_url, domain))

                self.processed_domains.add(domain)

            # 批量 commit（更快）
            self.conn.commit()
            print(f"  💾 批量更新 {len(results)} 个域名到数据库")

            # 保存进度
            self.save_progress()

            cur.close()
            return True

        except Exception as e:
            print(f"❌ 批量更新失败: {e}")
            self.conn.rollback()
            return False

    async def check_domains_batch(self, domains: List[str]):
        """批量检查域名（异步并发）"""
        # 过滤已处理的域名
        to_check = [d for d in domains if d not in self.processed_domains]

        if not to_check:
            print(f"✅ 所有域名都已处理！")
            return

        print(f"\n🚀 需要检查: {len(to_check)} 个域名")
        print(f"⚡ 并发数: {CONCURRENT_BROWSERS}")
        print(f"📦 批量大小: {BATCH_SIZE} (每次 commit)\n")

        total = len(to_check)
        completed = 0
        batch_results = []

        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )

            # 创建多个上下文
            contexts = []
            for _ in range(CONCURRENT_BROWSERS):
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )
                contexts.append(context)

            # 分批处理
            for i in range(0, len(to_check), CONCURRENT_BROWSERS):
                batch = to_check[i:i + CONCURRENT_BROWSERS]
                tasks = []

                # 创建任务
                for idx, domain in enumerate(batch):
                    context = contexts[idx % len(contexts)]
                    page = await context.new_page()
                    task = asyncio.create_task(self.check_single_domain(page, domain))
                    tasks.append((task, page, domain))

                # 并发执行
                for task, page, domain in tasks:
                    try:
                        result = await task
                        batch_results.append(result)

                        completed += 1
                        status = '✅' if result['has_ads'] else '⭕'
                        error_msg = f" (❌ {result['error']})" if result['error'] else ''
                        print(f"[{completed}/{total}] {status} {result['domain']}: {result['ad_count']} 个广告{error_msg}")

                        # 每 BATCH_SIZE 个更新一次数据库
                        if len(batch_results) >= BATCH_SIZE:
                            self.batch_update_database(batch_results)
                            batch_results = []

                    except Exception as e:
                        print(f"❌ 任务执行失败 {domain}: {e}")
                    finally:
                        await page.close()

            # 更新剩余的结果
            if batch_results:
                self.batch_update_database(batch_results)

            # 关闭浏览器
            for context in contexts:
                await context.close()
            await browser.close()

    async def run(self):
        """运行批量检查"""
        print("="*100)
        print("🚀 可靠的批量 Google Ads 检查工具")
        print("="*100)
        print()

        # 连接数据库
        if not self.connect_db():
            print("❌ 无法连接数据库，退出")
            return

        # 获取需要检查的域名
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT domain
                FROM stores
                WHERE country_code IN ('CN', 'HK')
                  AND estimated_monthly_visits >= 1000
                ORDER BY estimated_monthly_visits DESC
            """)

            all_domains = [row[0] for row in cur.fetchall()]
            cur.close()

            print(f"📊 数据库中共有 {len(all_domains)} 个域名")
            print(f"✅ 已处理: {len(self.processed_domains)} 个")
            print(f"⏳ 待处理: {len(all_domains) - len(self.processed_domains)} 个\n")

        except Exception as e:
            print(f"❌ 查询数据库失败: {e}")
            return

        # 记录开始时间
        start_time = time.time()

        # 批量检查
        await self.check_domains_batch(all_domains)

        # 计算耗时
        elapsed = time.time() - start_time

        # 统计报告
        print(f"\n{'='*100}")
        print(f"📊 检查完成！")
        print(f"{'='*100}")
        print(f"⏱️  总耗时: {elapsed:.2f} 秒 ({elapsed/60:.1f} 分钟)")
        print(f"✅ 成功处理: {len(self.processed_domains)} 个域名")
        print(f"❌ 失败: {len(self.failed_domains)} 个域名")
        if len(self.processed_domains) > 0:
            print(f"📈 平均速度: {elapsed/len(self.processed_domains):.2f} 秒/域名")
        print()

        if self.failed_domains:
            print(f"❌ 失败的域名:")
            for domain in self.failed_domains[:10]:
                print(f"   - {domain}")
            if len(self.failed_domains) > 10:
                print(f"   ... 还有 {len(self.failed_domains) - 10} 个")

        print(f"\n✅ 进度已保存到: {PROGRESS_FILE}")
        print(f"💡 如果中断了，再次运行会从断点继续")
        print("="*100)

        # 关闭数据库连接
        if self.conn:
            self.conn.close()


async def main():
    """主函数"""
    checker = ReliableBatchChecker()
    await checker.run()


if __name__ == '__main__':
    asyncio.run(main())
