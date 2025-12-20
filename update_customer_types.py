#!/usr/bin/env python3
"""
更新店铺的customer_type分类
使用方法: python3 update_customer_types.py
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

# 检查结果 - 请根据手动检查更新此字典
STORE_RESULTS = {
    'joetoyss.com': {
        'customer_type': 'PENDING_CHECK',  # new_advertiser_30d 或 old_advertiser
        'evidence': 'PENDING_CHECK',        # 例如: "First ad last seen: 2025-12-20"
        'had_ads_30_days_ago': None,        # True 或 False
        'has_ads_now': True                 # True 或 False
    },
    'dolcewe.com': {
        'customer_type': 'PENDING_CHECK',  # new_advertiser_30d 或 old_advertiser
        'evidence': 'PENDING_CHECK',        # 例如: "First ad last seen: 2025-12-05"
        'had_ads_30_days_ago': None,        # True 或 False
        'has_ads_now': True                 # True 或 False
    }
}

def update_store(domain, customer_type, evidence):
    """更新单个店铺的分类"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 先查询当前状态
        cur.execute("""
            SELECT domain, customer_type
            FROM stores
            WHERE domain = %s
        """, (domain,))

        current = cur.fetchone()
        if current:
            print(f"\n当前状态: {current[0]}")
            print(f"  旧分类: {current[1]}")

        # 更新 (不使用notes字段，因为表里没有这个字段)
        cur.execute("""
            UPDATE stores
            SET customer_type = %s,
                ads_check_level = 'precise_manual_verified',
                ads_last_checked = NOW()
            WHERE domain = %s
        """, (customer_type, domain))

        conn.commit()
        print(f"  ✅ 已更新为: {customer_type}")
        print(f"  验证证据: {evidence}")

        cur.close()
        conn.close()
        return True

    except Exception as e:
        print(f"  ❌ 更新失败: {str(e)}")
        return False

def main():
    print("=" * 80)
    print("30天新客户分类更新脚本")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"参考日期: 今天=2025-12-19, 30天前=2025-11-18")
    print("=" * 80)

    pending_count = 0
    updated_count = 0
    failed_count = 0

    for domain, info in STORE_RESULTS.items():
        print(f"\n处理店铺: {domain}")

        if info['customer_type'] == 'PENDING_CHECK':
            print("  ⚠️ 状态: 等待手动检查")
            pending_count += 1
            continue

        if info['customer_type'] not in ['new_advertiser_30d', 'old_advertiser']:
            print(f"  ❌ 无效分类: {info['customer_type']}")
            failed_count += 1
            continue

        # 更新数据库
        if update_store(domain, info['customer_type'], info['evidence']):
            updated_count += 1
        else:
            failed_count += 1

    # 总结
    print("\n" + "=" * 80)
    print("执行总结")
    print("=" * 80)
    print(f"等待检查: {pending_count} 个")
    print(f"成功更新: {updated_count} 个")
    print(f"更新失败: {failed_count} 个")
    print("=" * 80)

    if pending_count > 0:
        print("\n⚠️ 还有店铺等待手动检查！")
        print("请按照 manual_check_guide.md 的指引完成检查后，")
        print("更新本脚本中的 STORE_RESULTS 字典，然后重新运行。")

if __name__ == '__main__':
    main()
