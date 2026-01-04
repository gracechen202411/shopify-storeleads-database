#!/usr/bin/env python3
"""
Reset all Google Ads data in Neon and resync from local verified data
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

def reset_and_resync():
    print('='*100)
    print('重置并重新同步 Google Ads 数据')
    print('='*100)

    # Step 1: Clear all Google Ads data in Neon
    print('\n1️⃣ 清空 Neon 数据库中的所有 Google Ads 数据...')
    neon_conn = psycopg2.connect(**NEON_CONFIG)
    neon_cur = neon_conn.cursor()

    neon_cur.execute('''
        UPDATE stores
        SET
            has_google_ads = NULL,
            google_ads_count = NULL,
            is_new_customer = NULL,
            customer_type = NULL,
            ads_check_level = NULL,
            ads_last_checked = NULL
        WHERE has_google_ads IS NOT NULL
           OR google_ads_count IS NOT NULL
           OR is_new_customer IS NOT NULL
           OR customer_type IS NOT NULL
    ''')

    cleared_count = neon_cur.rowcount
    neon_conn.commit()
    print(f'   ✅ 已清空 {cleared_count:,} 条记录的广告数据')

    # Step 2: Check if local database exists
    print('\n2️⃣ 检查本地数据库...')
    try:
        local_conn = sqlite3.connect('local_stores.db')
        local_cur = local_conn.cursor()

        local_cur.execute('''
            SELECT COUNT(*)
            FROM stores
            WHERE has_google_ads IS NOT NULL OR customer_type IS NOT NULL
        ''')
        local_count = local_cur.fetchone()[0]
        print(f'   ✅ 本地数据库有 {local_count} 条已验证的记录')

        # Step 3: Sync from local to Neon
        if local_count > 0:
            print('\n3️⃣ 从本地数据库同步到 Neon...')

            local_cur.execute('''
                SELECT domain, has_google_ads, google_ads_count, is_new_customer,
                       customer_type, ads_check_level
                FROM stores
                WHERE has_google_ads IS NOT NULL OR customer_type IS NOT NULL
            ''')

            records = local_cur.fetchall()
            updated = 0

            for domain, has_ads, ads_count, is_new, ctype, check_level in records:
                # Convert SQLite boolean to PostgreSQL boolean
                has_ads_bool = bool(has_ads) if has_ads is not None else None
                is_new_bool = bool(is_new) if is_new is not None else None

                neon_cur.execute('''
                    UPDATE stores
                    SET
                        has_google_ads = %s,
                        google_ads_count = %s,
                        is_new_customer = %s,
                        customer_type = %s,
                        ads_check_level = %s,
                        ads_last_checked = NOW()
                    WHERE domain = %s
                ''', (has_ads_bool, ads_count, is_new_bool, ctype, check_level, domain))

                if neon_cur.rowcount > 0:
                    updated += 1

            neon_conn.commit()
            print(f'   ✅ 已同步 {updated} 条记录到 Neon')
        else:
            print('   ⚠️ 本地数据库没有已验证的数据，跳过同步')

        local_cur.close()
        local_conn.close()

    except Exception as e:
        print(f'   ❌ 本地数据库错误: {e}')
        print('   跳过同步步骤')

    # Step 4: Show final statistics
    print('\n4️⃣ Neon 数据库最终统计（浙江省 + ≥1000访问/月）:')
    neon_cur.execute('''
        SELECT
            customer_type,
            COUNT(*) as count
        FROM stores
        WHERE state = 'Zhejiang'
        AND estimated_monthly_visits >= 1000
        GROUP BY customer_type
        ORDER BY count DESC
    ''')

    print('='*100)
    for ctype, count in neon_cur.fetchall():
        print(f'  {ctype or "NULL":>20}: {count:>3} 个')
    print('='*100)

    # Step 5: Target customers
    neon_cur.execute('''
        SELECT COUNT(*), SUM(estimated_monthly_visits)
        FROM stores
        WHERE state = 'Zhejiang'
        AND estimated_monthly_visits >= 1000
        AND customer_type IN ('never_advertised', 'new_advertiser_30d')
    ''')

    target_count, target_visits = neon_cur.fetchone()
    print(f'\n🎯 目标客户总计:')
    print('='*100)
    print(f'  总数: {target_count or 0} 个店铺')
    print(f'  总访问量: {target_visits or 0:,}/月')
    print('='*100)

    neon_cur.close()
    neon_conn.close()

    print('\n✅ 重置并同步完成！Vercel 前端会自动显示最新数据')
    print('='*100)

if __name__ == '__main__':
    reset_and_resync()
