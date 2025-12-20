#!/usr/bin/env python3
"""查询当前店铺状态"""

import psycopg2

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

stores = ['joetoyss.com', 'dolcewe.com']

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print("=" * 100)
    print("当前店铺状态查询")
    print("=" * 100)

    for domain in stores:
        cur.execute("""
            SELECT
                domain,
                customer_type,
                ads_check_level,
                ads_last_checked,
                plan,
                categories
            FROM stores
            WHERE domain = %s
        """, (domain,))

        result = cur.fetchone()
        if result:
            print(f"\n店铺: {result[0]}")
            print(f"  客户类型: {result[1]}")
            print(f"  广告检查级别: {result[2]}")
            print(f"  最后检查时间: {result[3]}")
            print(f"  套餐: {result[4]}")
            print(f"  类别: {result[5]}")
            print(f"  检查链接: https://adstransparency.google.com/?region=anywhere&domain={result[0]}")
        else:
            print(f"\n⚠️ 店铺 {domain} 不在数据库中")

    print("\n" + "=" * 100)

    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ 数据库错误: {str(e)}")
