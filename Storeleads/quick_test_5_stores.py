#!/usr/bin/env python3
"""
快速测试5个店铺 - 手动检查版本
生成一个检查清单，手动用MCP检查
"""
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

# 获取5个中国店铺
cur.execute("""
    SELECT domain, country_code, estimated_monthly_visits
    FROM stores
    WHERE country_code = 'CN'
    AND (ads_last_checked IS NULL OR ads_last_checked < NOW() - INTERVAL '30 days')
    ORDER BY estimated_monthly_visits DESC NULLS LAST
    LIMIT 5
""")

stores = cur.fetchall()

print("="*80)
print("🎯 测试用的5个中国店铺")
print("="*80)
print()

for i, (domain, country, visits) in enumerate(stores, 1):
    print(f"{i}. {domain}")
    print(f"   国家：{country}")
    print(f"   月访问量：{visits:,}" if visits else "   月访问量：未知")
    print(f"   URL：https://adstransparency.google.com/?region=anywhere&domain={domain}")
    print()

# 保存到JSON方便我查看
import json
test_list = [
    {
        'domain': domain,
        'country': country,
        'visits': visits,
        'url': f'https://adstransparency.google.com/?region=anywhere&domain={domain}'
    }
    for domain, country, visits in stores
]

with open('test_5_stores.json', 'w', encoding='utf-8') as f:
    json.dump(test_list, f, ensure_ascii=False, indent=2)

print("✅ 清单已保存到：test_5_stores.json")

cur.close()
conn.close()
