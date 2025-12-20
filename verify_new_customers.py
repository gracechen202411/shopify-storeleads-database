#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证30天新客户脚本
用于手动验证店铺的最老广告日期，并更新数据库分类

今天日期: 2025-12-19
分类标准: 最老广告日期 >= 2025-11-19 → new_advertiser_30d
         最老广告日期 <= 2025-11-18 → old_advertiser
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

STORES_TO_VERIFY = [
    {
        'domain': 'dolcewe.com',
        'url': 'https://adstransparency.google.com/?region=anywhere&domain=dolcewe.com',
        'total_ads': 4
    },
    {
        'domain': 'joetoyss.com',
        'url': 'https://adstransparency.google.com/?region=anywhere&domain=joetoyss.com',
        'total_ads': 6
    }
]

def classify_customer(oldest_ad_date):
    """
    根据最老广告日期分类客户类型
    """
    cutoff_date = datetime(2025, 11, 19).date()

    if oldest_ad_date >= cutoff_date:
        return 'new_advertiser_30d'
    else:
        return 'old_advertiser'

def update_store_classification(domain, customer_type, oldest_ad_date):
    """
    更新店铺的客户分类
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE stores
            SET customer_type = %s,
                ads_last_seen_date = %s,
                ads_check_level = 'precise_manual',
                ads_last_checked = NOW()
            WHERE domain = %s
        """, (customer_type, oldest_ad_date, domain))

        conn.commit()
        print(f"✅ 成功更新 {domain} 为 {customer_type}")
        return True
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def verify_store(store_info):
    """
    验证单个店铺
    """
    print("\n" + "="*70)
    print(f"店铺: {store_info['domain']}")
    print(f"预期广告数量: {store_info['total_ads']}")
    print(f"广告页面: {store_info['url']}")
    print("="*70)

    print("\n请按照以下步骤操作：")
    print("1. 在浏览器中打开上面的URL")
    print("2. 滚动到页面底部，找到最老的广告（通常在最下方）")
    print("3. 点击最老的广告，查看详情")
    print("4. 找到「最后展示时间：YYYY年M月D日」")
    print("5. 输入该日期\n")

    # 获取用户输入
    while True:
        date_input = input(f"请输入 {store_info['domain']} 最老广告的日期 (格式: YYYY-MM-DD，例如: 2025-11-20): ").strip()

        if date_input.lower() == 'skip':
            print("⏭️  跳过此店铺")
            return

        try:
            oldest_ad_date = datetime.strptime(date_input, '%Y-%m-%d').date()
            break
        except ValueError:
            print("❌ 日期格式错误，请使用 YYYY-MM-DD 格式")

    # 分类
    customer_type = classify_customer(oldest_ad_date)
    cutoff = datetime(2025, 11, 19).date()

    print(f"\n📊 分析结果：")
    print(f"   最老广告日期: {oldest_ad_date}")
    print(f"   分界日期: {cutoff}")
    print(f"   客户类型: {customer_type}")

    if customer_type == 'new_advertiser_30d':
        print(f"   ✅ 确认为30天新客户 (最老广告日期 >= 2025-11-19)")
    else:
        print(f"   ❌ 不是30天新客户 (最老广告在 2025-11-18 或之前就存在)")

    # 确认更新
    confirm = input("\n是否更新数据库? (y/n): ").strip().lower()
    if confirm == 'y':
        update_store_classification(store_info['domain'], customer_type, oldest_ad_date)
    else:
        print("⏭️  跳过更新")

def main():
    print("\n" + "🔍 30天新客户验证工具".center(70, "="))
    print(f"\n今天日期: 2025-12-19")
    print(f"分类标准: 最老广告日期 >= 2025-11-19 为新客户")
    print(f"需要验证 {len(STORES_TO_VERIFY)} 个店铺")

    for store in STORES_TO_VERIFY:
        verify_store(store)

    print("\n" + "="*70)
    print("✅ 验证完成！")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断操作")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
