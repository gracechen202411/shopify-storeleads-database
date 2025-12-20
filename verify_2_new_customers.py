#!/usr/bin/env python3
"""
Verify the 2 new customers are actually new advertisers within 30 days
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import time

def check_domain_ads(domain):
    """Check if domain has ads before 30 days ago"""

    # Remove www prefix
    check_domain = domain.replace('www.', '') if domain.startswith('www.') else domain

    # Calculate 30 days ago
    check_date = datetime.now() - timedelta(days=30)
    end_date = (check_date - timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = "2018-05-31"

    url = f"https://adstransparency.google.com/?region=anywhere&domain={check_domain}&start-date={start_date}&end-date={end_date}"

    print(f"\n{'='*100}")
    print(f"检查域名: {domain}")
    print(f"检查URL: {url}")
    print(f"{'='*100}")

    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)

        # Wait for content to load (20 seconds)
        print(f"等待页面加载 (20秒)...")
        time.sleep(20)

        # Get page source
        page_source = driver.page_source.lower()

        # Check for ads
        if 'no ads found' in page_source or 'no results found' in page_source:
            ads_30days_ago = 0
            result = 'new_advertiser_30d'
            status = '✅ 确认是30天内新广告主'
        elif 'advertiser' in page_source or 'advertisement' in page_source:
            # Try to count ads
            try:
                ad_elements = driver.find_elements(By.CSS_SELECTOR, '[role="listitem"]')
                ads_30days_ago = len(ad_elements)
            except:
                ads_30days_ago = -1  # Unknown

            result = 'old_advertiser'
            status = f'❌ 这是老广告主！30天前有 {ads_30days_ago} 个广告'
        else:
            ads_30days_ago = -1
            result = 'needs_manual_review'
            status = '⚠️ 需要人工审核'

        print(f"分类结果: {result}")
        print(f"30天前广告数: {ads_30days_ago}")
        print(f"状态: {status}")
        print(f"验证链接: {url}")

        return result, ads_30days_ago, url

    except Exception as e:
        print(f"❌ 错误: {e}")
        return 'error', -1, url

    finally:
        driver.quit()

def main():
    domains = ['chicdecent.com', 'sunvivi.com']

    print('='*100)
    print('验证 2 个标记为"30天内新广告主"的店铺')
    print('='*100)

    results = []

    for domain in domains:
        result, ads_count, url = check_domain_ads(domain)
        results.append({
            'domain': domain,
            'result': result,
            'ads_30days_ago': ads_count,
            'url': url
        })
        time.sleep(2)  # Wait between checks

    # Summary
    print('\n' + '='*100)
    print('验证结果汇总')
    print('='*100)

    correct = 0
    incorrect = 0

    for r in results:
        if r['result'] == 'new_advertiser_30d':
            print(f"✅ {r['domain']}: 确认是30天内新广告主")
            correct += 1
        elif r['result'] == 'old_advertiser':
            print(f"❌ {r['domain']}: 实际是老广告主（30天前有 {r['ads_30days_ago']} 个广告）")
            print(f"   验证链接: {r['url']}")
            incorrect += 1
        else:
            print(f"⚠️ {r['domain']}: 需要人工审核")
            print(f"   验证链接: {r['url']}")

    print(f"\n总结: {correct} 个正确, {incorrect} 个错误")
    print('='*100)

if __name__ == '__main__':
    main()
