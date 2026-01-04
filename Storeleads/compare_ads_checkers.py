#!/usr/bin/env python3
"""
Performance Comparison: SerpApi vs Selenium vs Playwright
对比三种 Google Ads 检测方法的性能
"""

import time
import json
import asyncio
from datetime import datetime
from typing import List, Dict
import psycopg2

# Import existing checkers
try:
    from serpapi_ads_checker import SerpApiAdsChecker, SERPAPI_KEY
except:
    print("⚠️  serpapi_ads_checker.py not found")
    SerpApiAdsChecker = None

# Selenium checker simulation
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import re

# Database config
DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}


class SeleniumChecker:
    """Selenium-based checker for comparison"""

    def __init__(self):
        self.driver = None

    def init_browser(self):
        """Initialize Chrome browser"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=chrome_options)

    def check_domain(self, domain: str) -> Dict:
        """Check single domain"""
        check_domain = domain.replace('www.', '') if domain.startswith('www.') else domain
        url = f"https://adstransparency.google.com/?region=anywhere&domain={check_domain}"

        try:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 20)
            wait.until(lambda driver: "个广告" in driver.find_element(By.TAG_NAME, 'body').text)
            time.sleep(3)

            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            match = re.search(r'~?(\d+)\+?\s*个广告', page_text)

            if match:
                ads_count = int(match.group(1))
                has_ads = ads_count > 0
            elif '未找到任何广告' in page_text:
                ads_count = 0
                has_ads = False
            else:
                ads_count = -1
                has_ads = True

            return {
                'domain': domain,
                'has_ads': has_ads,
                'ad_count': ads_count,
                'error': None
            }

        except Exception as e:
            return {
                'domain': domain,
                'has_ads': False,
                'ad_count': 0,
                'error': str(e)
            }

    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()


class PlaywrightChecker:
    """Playwright-based checker for comparison"""

    def __init__(self):
        self.playwright = None
        self.browser = None

    async def init_browser(self):
        """Initialize Playwright browser"""
        from playwright.async_api import async_playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)

    async def check_domain(self, domain: str) -> Dict:
        """Check single domain"""
        check_domain = domain.replace('www.', '') if domain.startswith('www.') else domain
        url = f"https://adstransparency.google.com/?region=anywhere&domain={check_domain}"

        page = await self.browser.new_page()

        try:
            await page.goto(url, timeout=15000, wait_until='domcontentloaded')

            try:
                await page.wait_for_selector('text=/个广告/', timeout=3000)
            except:
                return {
                    'domain': domain,
                    'has_ads': False,
                    'ad_count': 0,
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

                return {
                    'domain': domain,
                    'has_ads': has_ads,
                    'ad_count': ad_count,
                    'error': None
                }

        except Exception as e:
            return {
                'domain': domain,
                'has_ads': False,
                'ad_count': 0,
                'error': str(e)
            }
        finally:
            await page.close()

    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


def get_test_domains(limit=10) -> List[str]:
    """Get test domains from database"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT domain
        FROM stores
        WHERE country_code IN ('CN', 'HK')
          AND estimated_monthly_visits >= 10000
        ORDER BY estimated_monthly_visits DESC
        LIMIT %s
    """, (limit,))

    domains = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return domains


async def test_playwright(domains: List[str]) -> Dict:
    """Test Playwright method"""
    print("\n" + "="*100)
    print("🎭 测试方法 1: Playwright（异步并发）")
    print("="*100)

    checker = PlaywrightChecker()
    await checker.init_browser()

    start_time = time.time()
    results = []

    for i, domain in enumerate(domains, 1):
        print(f"[{i}/{len(domains)}] {domain}...", end=' ')
        result = await checker.check_domain(domain)
        results.append(result)
        status = '✅' if result['has_ads'] else '⭕'
        print(f"{status} {result['ad_count']} 个广告")

    elapsed = time.time() - start_time

    await checker.close()

    return {
        'method': 'Playwright',
        'total_time': elapsed,
        'avg_time': elapsed / len(domains),
        'results': results,
        'success_rate': len([r for r in results if not r['error']]) / len(results) * 100
    }


def test_selenium(domains: List[str]) -> Dict:
    """Test Selenium method"""
    print("\n" + "="*100)
    print("🌐 测试方法 2: Selenium（单线程）")
    print("="*100)

    checker = SeleniumChecker()
    checker.init_browser()

    start_time = time.time()
    results = []

    for i, domain in enumerate(domains, 1):
        print(f"[{i}/{len(domains)}] {domain}...", end=' ')
        result = checker.check_domain(domain)
        results.append(result)
        status = '✅' if result['has_ads'] else '⭕'
        print(f"{status} {result['ad_count']} 个广告")
        time.sleep(2)  # Rate limiting

    elapsed = time.time() - start_time

    checker.close()

    return {
        'method': 'Selenium',
        'total_time': elapsed,
        'avg_time': elapsed / len(domains),
        'results': results,
        'success_rate': len([r for r in results if not r['error']]) / len(results) * 100
    }


def test_serpapi(domains: List[str]) -> Dict:
    """Test SerpApi method"""
    print("\n" + "="*100)
    print("🚀 测试方法 3: SerpApi（API 调用）")
    print("="*100)

    if not SerpApiAdsChecker or SERPAPI_KEY == "YOUR_SERPAPI_KEY_HERE":
        print("⚠️  SerpApi 未配置，跳过测试")
        return None

    checker = SerpApiAdsChecker(api_key=SERPAPI_KEY)

    start_time = time.time()
    results = []

    for i, domain in enumerate(domains, 1):
        print(f"[{i}/{len(domains)}] {domain}...", end=' ')
        result = checker.check_domain_ads(domain)
        results.append(result)
        status = '✅' if result['has_ads'] else '⭕'
        print(f"{status} {result['ad_count']} 个广告")
        time.sleep(1)  # SerpApi rate limiting

    elapsed = time.time() - start_time

    return {
        'method': 'SerpApi',
        'total_time': elapsed,
        'avg_time': elapsed / len(domains),
        'results': results,
        'success_rate': len([r for r in results if not r['error']]) / len(results) * 100
    }


def generate_comparison_report(test_results: List[Dict]):
    """Generate comparison report"""
    print("\n" + "="*100)
    print("📊 性能对比报告")
    print("="*100)

    # Filter out None results
    test_results = [r for r in test_results if r is not None]

    # Sort by total time
    test_results.sort(key=lambda x: x['total_time'])

    print("\n🏆 排名（按总耗时）:")
    print("-"*100)

    baseline = test_results[-1]['total_time']  # Slowest method as baseline

    for i, result in enumerate(test_results, 1):
        speedup = baseline / result['total_time']
        print(f"\n{i}. {result['method']}")
        print(f"   总耗时: {result['total_time']:.2f} 秒")
        print(f"   平均耗时: {result['avg_time']:.2f} 秒/域名")
        print(f"   成功率: {result['success_rate']:.1f}%")
        print(f"   速度提升: {speedup:.2f}x 倍（相比最慢方法）")

    print("\n" + "="*100)
    print("💡 结论:")
    print("-"*100)

    fastest = test_results[0]
    slowest = test_results[-1]

    print(f"🥇 最快方法: {fastest['method']}")
    print(f"   - 平均速度: {fastest['avg_time']:.2f} 秒/域名")
    print(f"   - 比 {slowest['method']} 快 {baseline/fastest['total_time']:.2f} 倍")

    print(f"\n🐌 最慢方法: {slowest['method']}")
    print(f"   - 平均速度: {slowest['avg_time']:.2f} 秒/域名")

    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'performance_comparison_{timestamp}.json'

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 详细报告已保存到: {report_file}")
    print("="*100)


async def main():
    """Main function"""
    print("="*100)
    print("🔬 Google Ads 检测方法性能对比测试")
    print("="*100)

    # Get test domains
    print("\n📦 准备测试数据...")
    test_domains = get_test_domains(limit=10)

    print(f"✅ 选取 {len(test_domains)} 个测试域名:")
    for i, domain in enumerate(test_domains, 1):
        print(f"   {i}. {domain}")

    # Run tests
    results = []

    # Test 1: Playwright
    try:
        playwright_result = await test_playwright(test_domains)
        results.append(playwright_result)
    except Exception as e:
        print(f"❌ Playwright 测试失败: {e}")

    # Test 2: Selenium
    try:
        selenium_result = test_selenium(test_domains)
        results.append(selenium_result)
    except Exception as e:
        print(f"❌ Selenium 测试失败: {e}")

    # Test 3: SerpApi
    try:
        serpapi_result = test_serpapi(test_domains)
        if serpapi_result:
            results.append(serpapi_result)
    except Exception as e:
        print(f"❌ SerpApi 测试失败: {e}")

    # Generate report
    if results:
        generate_comparison_report(results)
    else:
        print("\n❌ 没有成功的测试结果")


if __name__ == '__main__':
    asyncio.run(main())
