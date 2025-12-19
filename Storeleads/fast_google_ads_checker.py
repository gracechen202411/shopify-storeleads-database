#!/usr/bin/env python3
"""
高速并发Google广告查询工具
使用Playwright异步并发 + 多浏览器上下文 + 缓存机制
预计速度：100域名约1-2分钟
"""

import asyncio
import pandas as pd
import json
import time
from datetime import datetime
from pathlib import Path
import hashlib

# 尝试导入playwright
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright未安装，正在安装...")
    import subprocess
    subprocess.run(["pip3", "install", "playwright"], check=True)
    subprocess.run(["playwright", "install", "chromium"], check=True)
    from playwright.async_api import async_playwright

# 配置
CONCURRENT_BROWSERS = 5  # 并发浏览器数量（5个比较稳定）
TIMEOUT = 15000  # 页面超时15秒
CACHE_FILE = 'ads_cache.json'

# 缓存管理
class AdsCache:
    def __init__(self, cache_file=CACHE_FILE):
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self):
        """加载缓存"""
        if Path(self.cache_file).exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        """保存缓存"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def get(self, domain):
        """获取缓存"""
        return self.cache.get(domain)

    def set(self, domain, data):
        """设置缓存"""
        self.cache[domain] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()

    def is_fresh(self, domain, max_age_days=7):
        """检查缓存是否新鲜（默认7天）"""
        if domain not in self.cache:
            return False
        cached_time = datetime.fromisoformat(self.cache[domain]['timestamp'])
        age = (datetime.now() - cached_time).days
        return age < max_age_days


async def check_single_domain(page, domain):
    """检查单个域名的广告（异步）"""
    try:
        # 导航到页面
        await page.goto(
            f'https://adstransparency.google.com/?region=anywhere&domain={domain}',
            timeout=TIMEOUT,
            wait_until='domcontentloaded'  # 不等待完全加载，只等DOM加载
        )

        # 快速等待关键元素
        try:
            await page.wait_for_selector('text=/个广告/', timeout=3000)
        except:
            # 如果3秒内没找到，认为没有广告
            return {
                'domain': domain,
                'has_ads': False,
                'ad_count': 0,
                'ad_count_text': '0 个广告',
                'error': None
            }

        # 提取广告数量
        ad_count_element = await page.query_selector('generic:has-text("个广告")')
        if ad_count_element:
            ad_count_text = await ad_count_element.inner_text()

            # 判断是否有广告
            has_ads = '0 个广告' not in ad_count_text and '未找到任何广告' not in ad_count_text

            # 提取数字
            ad_count = 0
            if has_ads:
                if '~' in ad_count_text:
                    # ~200 个广告
                    ad_count = int(ad_count_text.split('~')[1].split(' ')[0])
                elif ad_count_text[0].isdigit():
                    # 42 个广告
                    ad_count = int(ad_count_text.split(' ')[0])

            return {
                'domain': domain,
                'has_ads': has_ads,
                'ad_count': ad_count,
                'ad_count_text': ad_count_text,
                'error': None
            }
        else:
            return {
                'domain': domain,
                'has_ads': False,
                'ad_count': 0,
                'ad_count_text': '未找到',
                'error': None
            }

    except Exception as e:
        return {
            'domain': domain,
            'has_ads': False,
            'ad_count': 0,
            'ad_count_text': 'Error',
            'error': str(e)
        }


async def check_domains_batch(domains, progress_callback=None):
    """批量检查域名（异步并发）"""
    cache = AdsCache()
    results = []
    to_check = []

    # 检查缓存
    print(f"📦 检查缓存...")
    for domain in domains:
        if cache.is_fresh(domain):
            cached = cache.get(domain)
            results.append(cached['data'])
            print(f"  ✅ 缓存命中: {domain}")
        else:
            to_check.append(domain)

    if not to_check:
        print(f"✅ 全部来自缓存！")
        return results

    print(f"\n🚀 需要查询: {len(to_check)} 个域名")
    print(f"⚡ 并发数: {CONCURRENT_BROWSERS} 个浏览器")

    # 启动Playwright
    async with async_playwright() as p:
        # 启动浏览器（无头模式，更快）
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )

        # 创建多个浏览器上下文（模拟多个独立浏览器）
        contexts = []
        for _ in range(CONCURRENT_BROWSERS):
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            contexts.append(context)

        # 创建任务队列
        tasks = []
        context_idx = 0

        for domain in to_check:
            # 轮流分配到不同的context
            context = contexts[context_idx % CONCURRENT_BROWSERS]
            page = await context.new_page()

            # 创建任务
            task = asyncio.create_task(check_single_domain(page, domain))
            tasks.append((task, page))

            context_idx += 1

        # 并发执行所有任务
        print(f"\n⏳ 查询中...\n")
        completed = 0
        total = len(tasks)

        for task, page in tasks:
            try:
                result = await task
                results.append(result)

                # 保存到缓存
                cache.set(result['domain'], result)

                completed += 1
                status = '✅' if result['has_ads'] else '⭕'
                print(f"[{completed}/{total}] {status} {result['domain']}: {result['ad_count_text']}")

                if progress_callback:
                    progress_callback(completed, total)

            except Exception as e:
                print(f"❌ {page.url}: {str(e)}")
            finally:
                await page.close()

        # 关闭浏览器
        for context in contexts:
            await context.close()
        await browser.close()

    return results


async def main():
    """主函数"""
    print("="*100)
    print("🚀 高速Google广告批量查询工具")
    print("="*100)

    # 读取数据
    df = pd.read_csv('hangzhou_stores_20k_200k.csv')
    domains = [row['domain'].replace('www.', '') for _, row in df.iterrows()]

    print(f"\n📊 总共 {len(domains)} 个域名")

    # 记录开始时间
    start_time = time.time()

    # 批量查询
    results = await check_domains_batch(domains)

    # 计算耗时
    elapsed = time.time() - start_time

    print(f"\n{'='*100}")
    print(f"⏱️  查询完成！总耗时: {elapsed:.2f}秒")
    print(f"📈 平均速度: {elapsed/len(domains):.2f}秒/域名")
    print(f"{'='*100}")

    # 生成报告
    print(f"\n📊 统计结果:")
    has_ads = sum(1 for r in results if r['has_ads'])
    no_ads = len(results) - has_ads
    total_ads = sum(r['ad_count'] for r in results)

    print(f"  ✅ 有广告: {has_ads} 个")
    print(f"  ⭕ 无广告: {no_ads} 个")
    print(f"  📊 广告总数: {total_ads} 个")

    # 保存结果
    df_results = pd.DataFrame(results)

    # 合并原始数据
    df_merged = df.copy()
    df_merged['domain_clean'] = df_merged['domain'].str.replace('www.', '')

    for idx, row in df_merged.iterrows():
        domain_clean = row['domain_clean']
        result = next((r for r in results if r['domain'] == domain_clean), None)
        if result:
            df_merged.at[idx, 'has_ads'] = '✅' if result['has_ads'] else '❌'
            df_merged.at[idx, 'ad_count'] = result['ad_count']
            df_merged.at[idx, 'ad_count_text'] = result['ad_count_text']

    df_merged.to_csv('fast_ads_check_results.csv', index=False, encoding='utf-8-sig')

    # 保存JSON
    with open('fast_ads_check_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 结果已保存:")
    print(f"  - fast_ads_check_results.csv")
    print(f"  - fast_ads_check_results.json")
    print(f"  - ads_cache.json (缓存文件)")

    # 显示有广告的店铺
    print(f"\n{'='*100}")
    print(f"✅ 有广告的店铺:")
    print(f"{'='*100}")
    for r in sorted(results, key=lambda x: x['ad_count'], reverse=True):
        if r['has_ads']:
            print(f"  🎯 {r['domain']}: {r['ad_count_text']}")


if __name__ == '__main__':
    # 运行异步主函数
    asyncio.run(main())
