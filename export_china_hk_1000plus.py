#!/usr/bin/env python3
"""
Export Shopify stores from China and Hong Kong with 1000+ monthly visits
导出中国和香港月访问量1000以上的Shopify店铺
"""

import psycopg2
import csv
from datetime import datetime

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}


def export_china_hk_stores():
    """Export China and HK stores with 1000+ monthly visits"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print("=" * 80)
    print("📊 中国和香港 Shopify 店铺列表（月访问量 ≥ 1000）")
    print("=" * 80)
    print()

    # Query stores from China (CN) and Hong Kong (HK) with 1000+ monthly visits
    cur.execute("""
        SELECT
            domain,
            country_code,
            estimated_monthly_visits,
            city,
            state,
            employee_count,
            customer_type,
            google_ads_count,
            ads_last_seen_date,
            instagram,
            facebook,
            emails,
            phones,
            ads_last_checked
        FROM stores
        WHERE country_code IN ('CN', 'HK')
          AND estimated_monthly_visits >= 1000
        ORDER BY estimated_monthly_visits DESC
    """)

    stores = cur.fetchall()

    print(f"✅ 找到 {len(stores)} 个店铺")
    print()

    # Show summary by country
    cur.execute("""
        SELECT
            country_code,
            COUNT(*) as store_count,
            SUM(estimated_monthly_visits) as total_visits,
            AVG(estimated_monthly_visits) as avg_visits
        FROM stores
        WHERE country_code IN ('CN', 'HK')
          AND estimated_monthly_visits >= 1000
        GROUP BY country_code
        ORDER BY store_count DESC
    """)

    summary = cur.fetchall()
    print("📊 分国家/地区统计：")
    print("-" * 80)
    for country, count, total, avg in summary:
        country_name = "中国大陆" if country == 'CN' else "香港"
        print(f"{country_name} ({country}):")
        print(f"  店铺数量: {count:,}")
        print(f"  总访问量: {total:,}/月")
        print(f"  平均访问量: {int(avg):,}/月")
        print()

    # Export to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = f'china_hk_stores_1000plus_{timestamp}.csv'

    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow([
            '域名', '国家/地区', '月访问量', '城市', '省份', '员工数',
            '客户类型', '广告数量', '最后广告时间',
            'Instagram', 'Facebook', '邮箱', '电话', '广告检查时间'
        ])

        for row in stores:
            writer.writerow(row)

    print("=" * 80)
    print(f"✅ 数据已导出到: {csv_file}")
    print()

    # Show top 10 stores
    print("=" * 80)
    print("🏆 访问量前10名店铺：")
    print("-" * 80)
    print()

    for i, row in enumerate(stores[:10], 1):
        domain, country, visits, city, state, employees, customer_type, ads_count, last_seen, ig, fb, emails, phones, checked = row
        country_name = "🇨🇳 中国" if country == 'CN' else "🇭🇰 香港"
        print(f"{i}. {domain}")
        print(f"   国家/地区: {country_name}")
        print(f"   月访问量: {visits:,}")
        print(f"   位置: {city or state or 'N/A'}")
        print(f"   员工数: {employees or 'N/A'}")
        print(f"   客户类型: {customer_type or 'N/A'}")
        if ads_count:
            print(f"   广告数量: {ads_count}")
        if last_seen:
            print(f"   最后广告: {last_seen}")
        if emails:
            print(f"   邮箱: {emails}")
        print()

    print("=" * 80)
    print("✅ 导出完成！")
    print("=" * 80)

    cur.close()
    conn.close()


if __name__ == '__main__':
    export_china_hk_stores()
