#!/usr/bin/env python3
"""
Parallel verification of never_advertised stores
Uses multiple browser instances to speed up verification
"""

import psycopg2
import time
from stage1_fast_check_selenium import FastJudgeSelenium
from multiprocessing import Pool, Manager
import sys

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}


def get_never_advertised_stores():
    """Get all stores marked as never_advertised"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT domain, estimated_monthly_visits, city
        FROM stores
        WHERE customer_type = 'never_advertised'
        AND estimated_monthly_visits >= 1000
        AND (city LIKE '%杭州%' OR city LIKE '%Hangzhou%'
             OR city LIKE '%浙江%' OR city LIKE '%Zhejiang%'
             OR city LIKE '%宁波%' OR city LIKE '%Ningbo%'
             OR city LIKE '%温州%' OR city LIKE '%Wenzhou%'
             OR city LIKE '%嘉兴%' OR city LIKE '%Jiaxing%'
             OR city LIKE '%金华%' OR city LIKE '%Jinhua%'
             OR city LIKE '%绍兴%' OR city LIKE '%Shaoxing%'
             OR city LIKE '%湖州%' OR city LIKE '%Huzhou%'
             OR city LIKE '%衢州%' OR city LIKE '%Quzhou%'
             OR city LIKE '%台州%' OR city LIKE '%Taizhou%'
             OR city LIKE '%丽水%' OR city LIKE '%Lishui%'
             OR city LIKE '%舟山%' OR city LIKE '%Zhoushan%')
        ORDER BY estimated_monthly_visits DESC
    """)

    stores = cur.fetchall()
    cur.close()
    conn.close()

    return stores


def verify_store(args):
    """Verify a single store (worker function)"""
    domain, visits, city, worker_id, total = args

    result_type = None
    ads_count = None
    result = None

    # Create browser instance (no DB connection yet)
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    import re

    try:
        # Init browser
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)

        # Check ads
        check_domain = domain.replace('www.', '') if domain.startswith('www.') else domain
        url = f"https://adstransparency.google.com/?region=anywhere&domain={check_domain}"

        driver.get(url)

        try:
            wait = WebDriverWait(driver, 20)
            wait.until(lambda d: "个广告" in d.find_element(By.TAG_NAME, 'body').text)
            time.sleep(3)
        except:
            pass

        page_text = driver.find_element(By.TAG_NAME, 'body').text

        match = re.search(r'~?(\d+)\+?\s*个广告', page_text)
        if match:
            ads_count = int(match.group(1))
            result_type = 'never_advertised' if ads_count == 0 else 'has_ads'
        elif '未找到任何广告' in page_text:
            ads_count = 0
            result_type = 'never_advertised'
        else:
            ads_count = -1
            result_type = 'has_ads'

        driver.quit()

        # Now connect to DB to update (one connection per update)
        if result_type:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()

            try:
                if result_type == 'has_ads':
                    cur.execute("""
                        UPDATE stores
                        SET customer_type = %s,
                            has_google_ads = %s,
                            google_ads_count = %s,
                            google_ads_url = %s
                        WHERE domain = %s
                    """, ('has_ads', True, ads_count, url, domain))

                conn.commit()
            finally:
                cur.close()
                conn.close()

    except Exception as e:
        result_type = 'failed'
        print(f"[Worker {worker_id}] ❌ Error: {domain} - {e}", file=sys.stderr)

    return {
        'domain': domain,
        'visits': visits,
        'city': city,
        'result_type': result_type,
        'ads_count': ads_count
    }


def main():
    print("=" * 100)
    print("🚀 并行重新验证所有标记为'从未打广告'的店铺")
    print("=" * 100)
    print()
    print("使用 5 个并行进程加速验证")
    print()

    stores = get_never_advertised_stores()
    print(f"找到 {len(stores)} 个店铺需要重新验证")
    print()

    if not stores:
        print("没有需要验证的店铺")
        return

    # Show some examples
    print("示例店铺：")
    for i, (domain, visits, city) in enumerate(stores[:10], 1):
        print(f"  {i}. {domain} - {visits:,} 访问/月 - {city}")
    if len(stores) > 10:
        print(f"  ... 还有 {len(stores) - 10} 个店铺")
    print()

    print(f"自动开始并行验证这 {len(stores)} 个店铺...")
    print()
    print("=" * 100)
    print("开始验证...")
    print("=" * 100)
    print()

    # Prepare arguments for workers
    total = len(stores)
    worker_args = []
    for i, (domain, visits, city) in enumerate(stores):
        worker_id = i % 5  # 5 workers
        worker_args.append((domain, visits, city, worker_id, total))

    # Use multiprocessing pool
    results = {
        'still_never_advertised': [],
        'actually_has_ads': [],
        'failed': []
    }

    start_time = time.time()
    completed = 0

    # Process in parallel with 5 workers
    with Pool(processes=5) as pool:
        for result in pool.imap_unordered(verify_store, worker_args):
            completed += 1
            domain = result['domain']
            result_type = result['result_type']
            ads_count = result['ads_count']

            elapsed = time.time() - start_time
            rate = completed / elapsed if elapsed > 0 else 0
            eta = (total - completed) / rate if rate > 0 else 0

            if result_type == 'never_advertised':
                results['still_never_advertised'].append(domain)
                print(f"[{completed}/{total}] ✅ {domain} - 确认无广告 (ETA: {eta/60:.1f}分钟)")
            elif result_type == 'has_ads':
                results['actually_has_ads'].append((domain, ads_count))
                print(f"[{completed}/{total}] ⚠️  {domain} - 实际有 {ads_count} 个广告 - 之前误判！")
            else:
                results['failed'].append(domain)
                print(f"[{completed}/{total}] ❌ {domain} - 检测失败")

            sys.stdout.flush()

    # Summary
    print()
    print("=" * 100)
    print("📊 验证结果")
    print("=" * 100)
    print()

    print(f"✅ 确认无广告: {len(results['still_never_advertised'])} 个店铺")
    print()

    print(f"⚠️  误判（实际有广告）: {len(results['actually_has_ads'])} 个店铺")
    if results['actually_has_ads']:
        print("   误判的店铺：")
        for domain, ads_count in results['actually_has_ads']:
            print(f"   - {domain} ({ads_count} 个广告)")
    print()

    if results['failed']:
        print(f"❌ 检测失败: {len(results['failed'])} 个店铺")
        for domain in results['failed']:
            print(f"   - {domain}")
        print()

    print("=" * 100)
    print(f"✅ 验证完成")
    print(f"准确率: {len(results['still_never_advertised'])}/{total} = {len(results['still_never_advertised'])/total*100:.1f}%")
    print(f"总耗时: {(time.time() - start_time)/60:.1f} 分钟")
    print("=" * 100)


if __name__ == '__main__':
    main()
