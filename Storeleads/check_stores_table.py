#!/usr/bin/env python3
import psycopg2

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# 查看 stores 表结构
cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'stores'
    ORDER BY ordinal_position
""")
columns = cur.fetchall()

print("="*80)
print("stores 表字段结构")
print("="*80)
for col in columns:
    nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
    print(f"{col[0]:30} {col[1]:20} {nullable}")

# 统计
cur.execute("SELECT COUNT(*) FROM stores")
count = cur.fetchone()[0]
print(f"\n总记录数：{count:,}")

# 查看示例数据
cur.execute("SELECT domain, country_code, estimated_monthly_visits FROM stores LIMIT 5")
samples = cur.fetchall()
print(f"\n示例数据：")
for s in samples:
    print(f"  {s[0]:40} {s[1]:5} {s[2]:10,} visits/月")

# 检查是否已有谷歌广告相关字段
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'stores' 
    AND column_name LIKE '%google%' OR column_name LIKE '%ads%'
""")
google_cols = cur.fetchall()

if google_cols:
    print(f"\n✅ 已有谷歌广告相关字段：")
    for col in google_cols:
        print(f"   - {col[0]}")
else:
    print(f"\n⚠️ 还没有谷歌广告相关字段")
    print(f"\n建议增加以下字段：")
    print("""
    ALTER TABLE stores ADD COLUMN has_google_ads BOOLEAN DEFAULT NULL;
    ALTER TABLE stores ADD COLUMN google_ads_count INTEGER DEFAULT NULL;
    ALTER TABLE stores ADD COLUMN ads_last_checked TIMESTAMP DEFAULT NULL;
    ALTER TABLE stores ADD COLUMN is_new_customer BOOLEAN DEFAULT NULL;
    """)

cur.close()
conn.close()
