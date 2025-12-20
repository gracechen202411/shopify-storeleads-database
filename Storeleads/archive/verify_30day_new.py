#!/usr/bin/env python3
"""
验证30天新客户 - 交互式工具

正确定义：
- 30天前（2025-11-18）没有广告
- 现在（2025-12-19）有广告
- = 30天内刚开始投放的新客户

检查方法：
找到最老的广告，看它的"最后展示时间"
- 如果 >= 2025-11-19：新客户 ✅
- 如果 <= 2025-11-18：老客户 ❌
"""

import psycopg2
from datetime import datetime, date

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

CUTOFF_DATE = date(2025, 11, 19)  # 30天前


def get_suspected_stores():
    """获取需要验证的店铺"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT domain, google_ads_count, ads_last_seen_date
        FROM stores
        WHERE customer_type = 'suspected_new_advertiser'
           OR customer_type = 'new_advertiser_30d'
        ORDER BY domain
    """)

    stores = cur.fetchall()
    cur.close()
    conn.close()

    return stores


def update_customer_type(domain, customer_type, oldest_ad_date):
    """更新客户类型"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        UPDATE stores
        SET customer_type = %s,
            ads_last_seen_date = %s,
            ads_check_level = 'precise',
            ads_last_checked = NOW()
        WHERE domain = %s
    """, (customer_type, oldest_ad_date, domain))

    conn.commit()
    cur.close()
    conn.close()


def main():
    print("=" * 80)
    print("🔍 30天新客户验证工具")
    print("=" * 80)
    print()
    print("定义：30天前（2025-11-18）没有广告，现在有广告")
    print("检查：找最老的广告，看它的展示时间")
    print()

    stores = get_suspected_stores()

    if not stores:
        print("✅ 没有需要验证的店铺！")
        return

    print(f"找到 {len(stores)} 个需要验证的店铺：")
    print()

    for domain, ads_count, last_seen in stores:
        print("-" * 80)
        print(f"店铺：{domain}")
        print(f"广告数量：{ads_count}")
        print(f"当前记录的最后展示时间：{last_seen or '未记录'}")
        print()

        # 提供检查链接
        url = f"https://adstransparency.google.com/?region=anywhere&domain={domain}"
        print(f"🔗 检查链接：{url}")
        print()

        print("请在浏览器中打开上面的链接，找到【最老的广告】")
        print()
        print("重要说明：")
        print("1. 滚动到广告列表的【最底部】")
        print("2. 点击【最后一个】（最老的）广告")
        print("3. 查看它的【最后展示时间】")
        print()

        # 用户输入
        oldest_date_str = input("请输入最老广告的最后展示时间（格式：YYYY-MM-DD，如 2025-12-18）：").strip()

        if not oldest_date_str:
            print("⏭️  跳过这个店铺")
            print()
            continue

        try:
            # 解析日期
            oldest_date = datetime.strptime(oldest_date_str, '%Y-%m-%d').date()

            # 判断
            if oldest_date >= CUTOFF_DATE:
                customer_type = 'new_advertiser_30d'
                print(f"✅ 判断：新客户（最老广告是 {oldest_date}，在 {CUTOFF_DATE} 之后）")
            else:
                customer_type = 'old_advertiser'
                print(f"❌ 判断：老客户（最老广告是 {oldest_date}，在 {CUTOFF_DATE} 之前）")

            # 确认更新
            confirm = input(f"确认更新 {domain} 为 {customer_type}？(y/n)：").strip().lower()

            if confirm == 'y':
                update_customer_type(domain, customer_type, oldest_date)
                print(f"💾 已更新数据库！")
            else:
                print("❌ 已取消")

        except ValueError:
            print("⚠️  日期格式错误，跳过")

        print()

    print("=" * 80)
    print("✅ 验证完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
