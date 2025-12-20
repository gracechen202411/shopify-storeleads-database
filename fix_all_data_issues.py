#!/usr/bin/env python3
"""
Fix all data integrity issues:
1. Fix chicdecent.com and sunvivi.com - they are old advertisers, not new
2. Ensure all stores have is_new_customer = false by default unless proven new
3. No store should show as "new customer" unless verified
"""

import psycopg2

NEON_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

def fix_all_issues():
    conn = psycopg2.connect(**NEON_CONFIG)
    cur = conn.cursor()

    print('='*100)
    print('修复所有数据完整性问题')
    print('='*100)

    # 1. Fix chicdecent.com and sunvivi.com - mark them as old_advertiser
    print('\n1️⃣ 修正 chicdecent.com 和 sunvivi.com (验证显示它们不是30天内新客户)...')
    cur.execute('''
        UPDATE stores
        SET
            customer_type = 'old_advertiser',
            is_new_customer = false,
            ads_check_level = '2'
        WHERE domain IN ('chicdecent.com', 'sunvivi.com')
        RETURNING domain, google_ads_count
    ''')

    fixed = cur.fetchall()
    if fixed:
        for domain, ads_count in fixed:
            print(f'   ✅ {domain} -> old_advertiser')
    else:
        print('   没有需要修正的店铺')

    # 2. Set all stores with is_new_customer = NULL to false by default
    print('\n2️⃣ 将所有 is_new_customer = NULL 的店铺设为 false (默认不是新客户)...')
    cur.execute('''
        UPDATE stores
        SET is_new_customer = false
        WHERE is_new_customer IS NULL
    ''')
    null_count = cur.rowcount
    print(f'   ✅ 更新了 {null_count:,} 个店铺')

    conn.commit()

    # 3. Verify final state - should have ZERO new customers now
    print('\n3️⃣ 验证最终状态...')
    cur.execute('''
        SELECT domain, customer_type, has_google_ads, google_ads_count
        FROM stores
        WHERE is_new_customer = true
        ORDER BY estimated_monthly_visits DESC
    ''')

    new_customers = cur.fetchall()
    print(f'\n   现在有 {len(new_customers)} 个标记为新客户的店铺:')
    if new_customers:
        for domain, ctype, has_ads, ads_count in new_customers:
            print(f'     - {domain}: customer_type={ctype}, has_ads={has_ads}, ads_count={ads_count}')
    else:
        print('     ✅ 没有任何店铺标记为新客户（正确！）')

    # 4. Show customer_type distribution
    print('\n4️⃣ customer_type 分布:')
    cur.execute('''
        SELECT
            customer_type,
            COUNT(*) as count
        FROM stores
        GROUP BY customer_type
        ORDER BY count DESC
    ''')

    stats = cur.fetchall()
    for ctype, count in stats:
        print(f'   {ctype or "NULL"}: {count:,} 个店铺')

    # 5. Show is_new_customer distribution
    print('\n5️⃣ is_new_customer 分布:')
    cur.execute('''
        SELECT
            is_new_customer,
            COUNT(*) as count
        FROM stores
        GROUP BY is_new_customer
        ORDER BY is_new_customer DESC NULLS LAST
    ''')

    stats = cur.fetchall()
    for is_new, count in stats:
        print(f'   {is_new}: {count:,} 个店铺')

    cur.close()
    conn.close()

    print('\n' + '='*100)
    print('✅ 所有数据问题已修复！')
    print('='*100)

if __name__ == '__main__':
    fix_all_issues()
