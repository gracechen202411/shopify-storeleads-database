#!/usr/bin/env python3
"""
Sync local SQLite results back to Neon database
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


def sync_to_neon():
    """Sync local SQLite results back to Neon"""
    print("=" * 100)
    print("🔄 同步本地数据回 Neon")
    print("=" * 100)
    print()

    # Connect to local SQLite
    print("读取本地数据库...")
    local_conn = sqlite3.connect(LOCAL_DB)
    local_cur = local_conn.cursor()

    # Get all stores
    local_cur.execute("""
        SELECT domain, customer_type, has_google_ads, is_new_customer,
               google_ads_count, google_ads_url, ads_check_level
        FROM stores
    """)

    stores = local_cur.fetchall()
    print(f"✅ 从本地数据库读取了 {len(stores)} 个店铺")
    print()

    # Connect to Neon
    print("连接到 Neon...")
    neon_conn = psycopg2.connect(**NEON_CONFIG)
    neon_cur = neon_conn.cursor()

    # Update stores in batches
    updated = 0
    for domain, customer_type, has_google_ads, is_new_customer, google_ads_count, google_ads_url, ads_check_level in stores:
        try:
            # Convert SQLite integers to PostgreSQL booleans
            has_google_ads_bool = bool(has_google_ads) if has_google_ads is not None else None
            is_new_customer_bool = bool(is_new_customer) if is_new_customer is not None else None

            neon_cur.execute("""
                UPDATE stores
                SET customer_type = %s,
                    has_google_ads = %s,
                    is_new_customer = %s,
                    google_ads_count = %s,
                    google_ads_url = %s,
                    ads_check_level = %s
                WHERE domain = %s
            """, (customer_type, has_google_ads_bool, is_new_customer_bool, google_ads_count, google_ads_url, ads_check_level, domain))

            if neon_cur.rowcount > 0:
                updated += 1

        except Exception as e:
            print(f"❌ Error updating {domain}: {e}")

    neon_conn.commit()
    print(f"✅ 已更新 {updated} 个店铺到 Neon")
    print()

    # Show summary
    neon_cur.execute("""
        SELECT customer_type, COUNT(*)
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
        GROUP BY customer_type
        ORDER BY COUNT(*) DESC
    """)

    summary = neon_cur.fetchall()

    print("Neon 数据库最终统计（浙江省 + ≥1000访问/月）：")
    print("=" * 100)
    for customer_type, count in summary:
        print(f"  {customer_type or 'NULL'}: {count} 个")
    print("=" * 100)
    print()

    # Show target customers summary
    neon_cur.execute("""
        SELECT COUNT(*), SUM(estimated_monthly_visits)
        FROM stores
        WHERE customer_type IN ('never_advertised', 'new_advertiser_30d')
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
    """)

    target_count, target_visits = neon_cur.fetchone()

    print("🎯 目标客户总计：")
    print("=" * 100)
    print(f"  总数: {target_count} 个店铺")
    print(f"  总访问量: {target_visits:,}/月" if target_visits else "  总访问量: 0/月")
    print("=" * 100)
    print()

    print("✅ 同步完成！Vercel 前端会自动显示最新数据")
    print("=" * 100)

    local_cur.close()
    local_conn.close()
    neon_cur.close()
    neon_conn.close()


if __name__ == '__main__':
    sync_to_neon()
