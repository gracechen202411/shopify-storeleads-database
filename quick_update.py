#!/usr/bin/env python3
"""
快速更新客户类型的交互式脚本
直接运行，根据提示输入验证结果即可
"""

import psycopg2
from datetime import datetime

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

def update_store(domain, customer_type, evidence):
    """更新店铺分类"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 查询旧状态
        cur.execute("SELECT customer_type FROM stores WHERE domain = %s", (domain,))
        old_type = cur.fetchone()
        old_type = old_type[0] if old_type else 'unknown'

        # 更新
        cur.execute("""
            UPDATE stores
            SET customer_type = %s,
                ads_check_level = 'precise_manual_verified',
                ads_last_checked = NOW()
            WHERE domain = %s
        """, (customer_type, domain))

        conn.commit()
        cur.close()
        conn.close()

        return True, old_type

    except Exception as e:
        return False, str(e)

def main():
    print("\n" + "=" * 80)
    print("30天新客户验证 - 快速更新工具")
    print("=" * 80)
    print(f"今天: 2025-12-19")
    print(f"30天前: 2025-11-18")
    print()
    print("定义:")
    print("  new_advertiser_30d: 30天前无广告，现在有广告")
    print("  old_advertiser: 30天前就有广告")
    print("=" * 80)

    stores = [
        {
            'domain': 'joetoyss.com',
            'url': 'https://adstransparency.google.com/?region=anywhere&domain=joetoyss.com'
        },
        {
            'domain': 'dolcewe.com',
            'url': 'https://adstransparency.google.com/?region=anywhere&domain=dolcewe.com'
        }
    ]

    results = []

    for store in stores:
        print(f"\n{'='*80}")
        print(f"店铺: {store['domain']}")
        print(f"检查链接: {store['url']}")
        print(f"{'='*80}")
        print()
        print("请打开上面的链接，找到最老的广告，查看其'最后展示时间'")
        print()

        # 获取用户输入
        while True:
            oldest_ad_date = input("最老广告的日期 (格式: YYYY-MM-DD，例如 2025-12-20): ").strip()
            if len(oldest_ad_date) == 10 and oldest_ad_date[4] == '-' and oldest_ad_date[7] == '-':
                break
            print("❌ 日期格式不正确，请使用 YYYY-MM-DD 格式")

        # 判断分类
        cutoff_date = '2025-11-18'
        if oldest_ad_date > cutoff_date:
            suggested_type = 'new_advertiser_30d'
            reason = f"最老广告日期 {oldest_ad_date} 晚于 {cutoff_date}"
        else:
            suggested_type = 'old_advertiser'
            reason = f"最老广告日期 {oldest_ad_date} 早于或等于 {cutoff_date}"

        print(f"\n建议分类: {suggested_type}")
        print(f"判断依据: {reason}")

        confirm = input(f"\n确认更新为 {suggested_type}? (y/n): ").strip().lower()

        if confirm == 'y':
            evidence = f"Oldest ad last seen: {oldest_ad_date}, verified on {datetime.now().strftime('%Y-%m-%d')}"
            success, info = update_store(store['domain'], suggested_type, evidence)

            if success:
                print(f"✅ 更新成功!")
                print(f"   旧分类: {info}")
                print(f"   新分类: {suggested_type}")
                results.append({
                    'domain': store['domain'],
                    'status': 'updated',
                    'old_type': info,
                    'new_type': suggested_type,
                    'evidence': evidence
                })
            else:
                print(f"❌ 更新失败: {info}")
                results.append({
                    'domain': store['domain'],
                    'status': 'failed',
                    'error': info
                })
        else:
            print("⚠️ 跳过更新")
            results.append({
                'domain': store['domain'],
                'status': 'skipped'
            })

    # 总结
    print("\n" + "=" * 80)
    print("更新总结")
    print("=" * 80)

    for result in results:
        print(f"\n{result['domain']}:")
        if result['status'] == 'updated':
            print(f"  ✅ 已更新: {result['old_type']} → {result['new_type']}")
            print(f"  证据: {result['evidence']}")
        elif result['status'] == 'skipped':
            print(f"  ⚠️ 跳过")
        else:
            print(f"  ❌ 失败: {result.get('error', 'unknown')}")

    print("\n" + "=" * 80)
    print("完成！")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
