#!/usr/bin/env python3
"""
手动验证30天新客户 - 简化版
直接输入验证结果更新数据库
"""

import psycopg2
from datetime import date

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

CUTOFF_DATE = date(2025, 11, 19)  # 30天前的截止日期

def update_store(domain, oldest_date_str):
    """根据最老广告日期更新店铺分类"""
    try:
        oldest_date = date.fromisoformat(oldest_date_str)

        if oldest_date >= CUTOFF_DATE:
            customer_type = 'new_advertiser_30d'
            status = '✅ 新客户'
        else:
            customer_type = 'old_advertiser'
            status = '❌ 老客户'

        # 更新数据库
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("""
            UPDATE stores
            SET customer_type = %s,
                ads_last_seen_date = %s,
                ads_check_level = 'precise',
                ads_last_checked = NOW()
            WHERE domain = %s
        """, (customer_type, oldest_date, domain))

        conn.commit()
        cur.close()
        conn.close()

        print(f"\n{status}")
        print(f"域名: {domain}")
        print(f"最老广告日期: {oldest_date}")
        print(f"分类: {customer_type}")
        print(f"判断依据: 最老广告日期{'≥' if oldest_date >= CUTOFF_DATE else '<'} {CUTOFF_DATE}")
        print("💾 已更新数据库\n")

        return True

    except ValueError:
        print(f"❌ 日期格式错误，请使用 YYYY-MM-DD 格式")
        return False
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False


def main():
    print("=" * 80)
    print("🔍 30天新客户手动验证工具")
    print("=" * 80)
    print()
    print(f"定义: 30天前（2025-11-18）没有广告，现在有广告")
    print(f"截止日期: {CUTOFF_DATE}")
    print()
    print("需要验证的店铺：")
    print()

    stores = [
        ('dolcewe.com', 4, 'https://adstransparency.google.com/?region=anywhere&domain=dolcewe.com'),
        ('joetoyss.com', 6, 'https://adstransparency.google.com/?region=anywhere&domain=joetoyss.com')
    ]

    for domain, ads_count, url in stores:
        print("-" * 80)
        print(f"店铺: {domain}")
        print(f"广告数量: {ads_count}")
        print(f"检查链接: {url}")
        print()
        print("步骤:")
        print("1. 打开上面的链接")
        print("2. 滚动到广告列表【最底部】")
        print("3. 点击【最后一个】（最老的）广告")
        print("4. 查看【最后展示时间】字段")
        print()

        oldest_date = input(f"请输入 {domain} 最老广告的【最后展示时间】(YYYY-MM-DD): ").strip()

        if oldest_date:
            update_store(domain, oldest_date)
        else:
            print("⏭️  跳过\n")

    print("=" * 80)
    print("✅ 验证完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
