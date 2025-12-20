#!/usr/bin/env python3
"""
Re-verify all stores marked as 'never_advertised'
Fix false negatives caused by www prefix issue and timing issues
"""

import psycopg2
import time
from stage1_fast_check_selenium import FastJudgeSelenium

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
        ORDER BY estimated_monthly_visits DESC
    """)

    stores = cur.fetchall()
    cur.close()
    conn.close()

    return stores


def main():
    print("=" * 100)
    print("🔍 重新验证所有标记为'从未打广告'的店铺")
    print("=" * 100)
    print()
    print("原因：修复了 www 前缀问题和动态加载问题")
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

    print(f"自动开始验证这 {len(stores)} 个店铺...")
    print()
    print("=" * 100)
    print("开始验证...")
    print("=" * 100)
    print()

    judge = FastJudgeSelenium()
    judge.init_browser(headless=True)

    results = {
        'still_never_advertised': [],
        'actually_has_ads': [],
        'failed': []
    }

    for i, (domain, visits, city) in enumerate(stores, 1):
        print(f"[{i}/{len(stores)}] {domain}...", end=' ')

        result = judge.check_ads(domain)

        if result:
            customer_type = result['customer_type']
            ads_count = result['ads_count']

            if customer_type == 'never_advertised':
                results['still_never_advertised'].append(domain)
                print(f"✅ 确认无广告")
            elif customer_type == 'has_ads':
                results['actually_has_ads'].append((domain, ads_count))
                print(f"⚠️  实际有 {ads_count} 个广告 - 之前误判！")
                # Update database
                judge.update_store(domain, result)
            else:
                results['failed'].append(domain)
                print(f"❌ 检测失败")
        else:
            results['failed'].append(domain)
            print("❌ 检测失败")

        time.sleep(2)  # Rate limiting

    judge.close()

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
    print(f"准确率: {len(results['still_never_advertised'])}/{len(stores)} = {len(results['still_never_advertised'])/len(stores)*100:.1f}%")
    print("=" * 100)


if __name__ == '__main__':
    main()
