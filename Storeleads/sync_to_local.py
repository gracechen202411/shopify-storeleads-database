#!/usr/bin/env python3
"""
Sync Neon data to local SQLite for fast verification
"""

import psycopg2
import sqlite3

NEON_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

LOCAL_DB = 'local_stores.db'


def sync_to_local():
    """Sync Neon data to local SQLite"""
    print("=" * 100)
    print("🔄 同步 Neon 数据到本地 SQLite")
    print("=" * 100)
    print()

    # Connect to Neon
    print("连接到 Neon...")
    neon_conn = psycopg2.connect(**NEON_CONFIG)
    neon_cur = neon_conn.cursor()

    # Get all stores
    neon_cur.execute("""
        SELECT domain, estimated_monthly_visits, city, customer_type,
               has_google_ads, is_new_customer, google_ads_count, google_ads_url,
               ads_check_level
        FROM stores
        WHERE estimated_monthly_visits >= 1000
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
    """)

    stores = neon_cur.fetchall()
    print(f"✅ 从 Neon 获取了 {len(stores)} 个店铺")
    print()

    # Create local SQLite
    print("创建本地 SQLite 数据库...")
    local_conn = sqlite3.connect(LOCAL_DB)
    local_cur = local_conn.cursor()

    # Create table
    local_cur.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            domain TEXT PRIMARY KEY,
            estimated_monthly_visits INTEGER,
            city TEXT,
            customer_type TEXT,
            has_google_ads INTEGER,
            is_new_customer INTEGER,
            google_ads_count INTEGER,
            google_ads_url TEXT,
            ads_check_level TEXT
        )
    """)

    # Clear existing data
    local_cur.execute("DELETE FROM stores")

    # Insert data
    for store in stores:
        local_cur.execute("""
            INSERT INTO stores VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, store)

    local_conn.commit()
    print(f"✅ 已同步 {len(stores)} 个店铺到本地数据库")
    print()

    # Show summary
    local_cur.execute("SELECT customer_type, COUNT(*) FROM stores GROUP BY customer_type")
    summary = local_cur.fetchall()

    print("本地数据库统计：")
    for customer_type, count in summary:
        print(f"  - {customer_type or 'NULL'}: {count} 个")
    print()

    print(f"✅ 本地数据库已保存到: {LOCAL_DB}")
    print("=" * 100)

    neon_cur.close()
    neon_conn.close()
    local_cur.close()
    local_conn.close()


if __name__ == '__main__':
    sync_to_local()
