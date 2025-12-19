#!/usr/bin/env python3
"""
保存测试的5个店铺结果到数据库
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

# 5个店铺的检查结果
results = {
    'qudahalloween.com': {
        'has_google_ads': False,
        'google_ads_count': 0,
        'is_new_customer': True  # 从来没打过广告
    },
    'www.goretroid.com': {
        'has_google_ads': True,
        'google_ads_count': 6,
        'is_new_customer': True  # 只有6个广告，可能是新客户
    },
    'kbdfans.com': {
        'has_google_ads': True,
        'google_ads_count': 200,
        'is_new_customer': False  # ~200个广告，长期投放，老客户
    },
    'www.redragonzone.com': {
        'has_google_ads': False,
        'google_ads_count': 0,
        'is_new_customer': True  # 从来没打过广告
    },
    'cn.turtlebeach.com': {
        'has_google_ads': False,
        'google_ads_count': 0,
        'is_new_customer': True  # 从来没打过广告
    }
}

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

print("="*80)
print("保存测试结果到数据库")
print("="*80)
print()

for domain, data in results.items():
    if data['has_google_ads'] is not None:
        try:
            cur.execute("""
                UPDATE stores
                SET
                    has_google_ads = %s,
                    google_ads_count = %s,
                    is_new_customer = %s,
                    ads_last_checked = NOW()
                WHERE domain = %s
            """, (
                data['has_google_ads'],
                data['google_ads_count'],
                data['is_new_customer'],
                domain
            ))
            conn.commit()
            
            status = "🔥 新客户" if data['is_new_customer'] else "老客户"
            ads = data['google_ads_count']
            print(f"✅ {domain}: {status} ({ads}个广告)")
        except Exception as e:
            print(f"❌ {domain}: 保存失败 - {e}")
            conn.rollback()
    else:
        print(f"⏳ {domain}: 待检查")

print()
print("="*80)
print("验证数据库")
print("="*80)
print()

# 验证数据
cur.execute("""
    SELECT domain, has_google_ads, google_ads_count, is_new_customer, ads_last_checked
    FROM stores
    WHERE domain IN ('qudahalloween.com', 'www.goretroid.com', 'kbdfans.com', 'www.redragonzone.com', 'cn.turtlebeach.com')
    ORDER BY domain
""")

rows = cur.fetchall()
for row in rows:
    print(f"域名: {row[0]}")
    print(f"  有广告: {row[1]}")
    print(f"  广告数: {row[2]}")
    print(f"  新客户: {row[3]}")
    print(f"  检查时间: {row[4]}")
    print()

# 统计
cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN has_google_ads = TRUE THEN 1 END) as has_ads,
        COUNT(CASE WHEN is_new_customer = TRUE THEN 1 END) as new_customers
    FROM stores
    WHERE ads_last_checked IS NOT NULL
""")

stats = cur.fetchone()
print("="*80)
print("数据库统计")
print("="*80)
print(f"已检查店铺: {stats[0]}")
print(f"有广告: {stats[1]}")
print(f"🔥 新客户: {stats[2]}")

cur.close()
conn.close()
