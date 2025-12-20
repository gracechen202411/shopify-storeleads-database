#!/usr/bin/env python3
"""
Parallel verification using local SQLite (no Neon connection issues!)
"""

import sqlite3
import time
from multiprocessing import Pool
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import re
import sys

LOCAL_DB = 'local_stores.db'


def get_never_advertised_stores():
    """Get all never_advertised stores from local DB"""
    conn = sqlite3.connect(LOCAL_DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT domain, estimated_monthly_visits, city
        FROM stores
        WHERE customer_type = 'never_advertised'
        ORDER BY estimated_monthly_visits DESC
    """)

    stores = cur.fetchall()
    cur.close()
    conn.close()

    return stores


def verify_store(args):
    """Verify a single store (worker function)"""
    domain, visits, city, worker_id = args

    result_type = None
    ads_count = None

    try:
        # Init browser
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
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

        # Update local SQLite (no connection limit!)
        if result_type == 'has_ads':
            conn = sqlite3.connect(LOCAL_DB)
            cur = conn.cursor()
            cur.execute("""
                UPDATE stores
                SET customer_type = ?,
                    has_google_ads = 1,
                    google_ads_count = ?,
                    google_ads_url = ?
                WHERE domain = ?
            """, ('has_ads', ads_count, url, domain))
            conn.commit()
            cur.close()
            conn.close()

    except Exception as e:
        result_type = 'failed'
        print(f"[Worker {worker_id}] ❌ Error: {domain} - {e}", file=sys.stderr, flush=True)

    return {
        'domain': domain,
        'visits': visits,
        'city': city,
        'result_type': result_type,
        'ads_count': ads_count
    }


def main():
    print("=" * 100)
    print("🚀 并行验证（本地 SQLite）")
    print("=" * 100)
    print()
    print("使用 10 个并行进程 + 本地数据库")
    print()

    stores = get_never_advertised_stores()
    print(f"找到 {len(stores)} 个 never_advertised 店铺需要验证")
    print()

    if not stores:
        print("没有需要验证的店铺")
        return

    # Show examples
    print("示例店铺：")
    for i, (domain, visits, city) in enumerate(stores[:10], 1):
        print(f"  {i}. {domain} - {visits:,} 访问/月 - {city}")
    if len(stores) > 10:
        print(f"  ... 还有 {len(stores) - 10} 个店铺")
    print()

    print("开始并行验证...")
    print("=" * 100)
    print()

    # Prepare worker args
    worker_args = []
    for i, (domain, visits, city) in enumerate(stores):
        worker_id = i % 10
        worker_args.append((domain, visits, city, worker_id))

    results = {
        'still_never_advertised': [],
        'actually_has_ads': [],
        'failed': []
    }

    start_time = time.time()
    completed = 0
    total = len(stores)

    # Process with 10 workers
    with Pool(processes=10) as pool:
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
                print(f"[{completed}/{total}] ✅ {domain} - 确认无广告 (ETA: {eta/60:.1f}分钟)", flush=True)
            elif result_type == 'has_ads':
                results['actually_has_ads'].append((domain, ads_count))
                print(f"[{completed}/{total}] ⚠️  {domain} - 实际有 {ads_count} 个广告！", flush=True)
            else:
                results['failed'].append(domain)
                print(f"[{completed}/{total}] ❌ {domain} - 检测失败", flush=True)

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
    print()

    print("=" * 100)
    print(f"✅ 验证完成")
    print(f"准确率: {len(results['still_never_advertised'])}/{total} = {len(results['still_never_advertised'])/total*100:.1f}%")
    print(f"总耗时: {(time.time() - start_time)/60:.1f} 分钟")
    print("=" * 100)
    print()
    print("💾 结果已保存到本地数据库，运行 sync_to_neon.py 同步回 Neon")


if __name__ == '__main__':
    main()
