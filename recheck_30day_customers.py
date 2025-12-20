import psycopg2
from datetime import datetime

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

def update_customer_type(domain, customer_type, evidence):
    """Update customer type in database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("""
            UPDATE stores
            SET customer_type = %s,
                ads_check_level = 'precise',
                ads_last_checked = NOW(),
                notes = %s
            WHERE domain = %s
        """, (customer_type, evidence, domain))

        conn.commit()
        print(f"✅ Updated {domain} to {customer_type}")
        print(f"   Evidence: {evidence}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error updating {domain}: {str(e)}")

# 待检查的店铺
stores_to_check = [
    'joetoyss.com',
    'dolcewe.com'
]

print("=" * 80)
print("30天新客户重新验证脚本")
print("=" * 80)
print(f"今天日期: 2025-12-19")
print(f"30天前日期: 2025-11-18")
print()
print("正确定义:")
print("- 30天前(2025-11-18)无广告 + 现在有广告 = new_advertiser_30d")
print("- 30天前就有广告 = old_advertiser")
print("=" * 80)
print()

for domain in stores_to_check:
    print(f"\n{'='*80}")
    print(f"店铺: {domain}")
    print(f"Google Ads检查页面: https://adstransparency.google.com/?region=anywhere&domain={domain}")
    print(f"{'='*80}")
    print()
    print("请手动检查以下信息:")
    print("1. 当前是否有广告?")
    print("2. 查看最早的广告，检查'最后展示时间':")
    print("   - 如果最早的广告首次出现在 2025-11-19 之后 → new_advertiser_30d")
    print("   - 如果最早的广告在 2025-11-18 或更早就存在 → old_advertiser")
    print()
    print("或者尝试使用日期过滤器:")
    print("   - 设置结束日期为 2025-11-18")
    print("   - 如果显示0个广告 → new_advertiser_30d")
    print("   - 如果显示有广告 → old_advertiser")
    print()

    # 等待用户输入
    customer_type = input(f"\n输入分类 (new_advertiser_30d / old_advertiser): ").strip()
    evidence = input("输入证据说明 (例如: First ad last seen: 2025-12-20): ").strip()

    if customer_type in ['new_advertiser_30d', 'old_advertiser']:
        update_customer_type(domain, customer_type, evidence)
    else:
        print(f"⚠️ 跳过 {domain} - 无效的分类")

print("\n" + "=" * 80)
print("检查完成！")
print("=" * 80)
