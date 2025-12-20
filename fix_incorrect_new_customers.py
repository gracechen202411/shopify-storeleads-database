#!/usr/bin/env python3
"""
Fix incorrect new customer data in database
Only chicdecent.com and sunvivi.com should be marked as new customers
"""

import psycopg2

NEON_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

def fix_data():
    conn = psycopg2.connect(**NEON_CONFIG)
    cur = conn.cursor()

    print('='*100)
    print('修正错误的新客户标记')
    print('='*100)

    # 1. Fix stores with has_google_ads = False but is_new_customer = True
    # These should be 'never_advertised'
    print('\n1️⃣ 修正没有广告但标记为新客户的店铺...')
    cur.execute('''
        UPDATE stores
        SET
            customer_type = 'never_advertised',
            is_new_customer = false,
            ads_check_level = '1'
        WHERE is_new_customer = true
        AND (has_google_ads = false OR has_google_ads IS NULL)
        AND customer_type IS NULL
        RETURNING domain, city, state
    ''')

    fixed_never_advertised = cur.fetchall()
    print(f'✅ 修正了 {len(fixed_never_advertised)} 个店铺为 never_advertised:')
    for domain, city, state in fixed_never_advertised:
        print(f'   - {domain} ({city}, {state})')

    # 2. Fix goretroid.com - has 6 ads, need to check if it's old or new
    # Based on user feedback, it had ads 30 days ago, so it's old_advertiser
    print('\n2️⃣ 修正 goretroid.com (有6个广告，但不是30天内新客户)...')
    cur.execute('''
        UPDATE stores
        SET
            customer_type = 'old_advertiser',
            is_new_customer = false,
            ads_check_level = '2'
        WHERE domain = 'www.goretroid.com'
        RETURNING domain, google_ads_count
    ''')

    fixed_goretroid = cur.fetchone()
    if fixed_goretroid:
        print(f'✅ 修正了 {fixed_goretroid[0]} (有 {fixed_goretroid[1]} 个广告) -> old_advertiser')

    conn.commit()

    # 3. Verify the final state
    print('\n3️⃣ 验证修正后的数据...')
    cur.execute('''
        SELECT domain, city, state, has_google_ads, google_ads_count,
               is_new_customer, customer_type
        FROM stores
        WHERE is_new_customer = true
        ORDER BY estimated_monthly_visits DESC
    ''')

    remaining_new_customers = cur.fetchall()
    print(f'\n✅ 现在只有 {len(remaining_new_customers)} 个真正的新客户：')
    for domain, city, state, has_ads, ads_count, is_new, cust_type in remaining_new_customers:
        print(f'   ✓ {domain} ({city}, {state})')
        print(f'     customer_type: {cust_type}, ads_count: {ads_count}')

    # 4. Show summary statistics
    print('\n4️⃣ 数据库统计：')
    cur.execute('''
        SELECT
            customer_type,
            COUNT(*) as count
        FROM stores
        GROUP BY customer_type
        ORDER BY count DESC
    ''')

    stats = cur.fetchall()
    for cust_type, count in stats:
        print(f'   {cust_type or "NULL"}: {count:,} 个店铺')

    cur.close()
    conn.close()

    print('\n' + '='*100)
    print('✅ 数据修正完成！前端会自动显示更新后的数据')
    print('='*100)

if __name__ == '__main__':
    fix_data()
