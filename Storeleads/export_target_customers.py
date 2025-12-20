#!/usr/bin/env python3
"""
导出目标客户清单
输出两类高价值客户：
1. never_advertised：从未投放广告
2. new_advertiser_30d：30天内刚开始投放
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


def export_target_customers():
    """导出目标客户清单"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print("=" * 80)
    print("📊 目标客户清单")
    print("=" * 80)
    print()

    # 1. Never Advertised（从未投放）
    print("✅ 类型一：从未投放广告的店铺（never_advertised）")
    print("-" * 80)

    cur.execute("""
        SELECT
            domain,
            estimated_monthly_visits,
            city,
            state,
            employee_count,
            instagram,
            facebook,
            emails,
            phones,
            ads_last_checked
        FROM stores
        WHERE customer_type = 'never_advertised'
          AND country_code = 'CN'
        ORDER BY estimated_monthly_visits DESC
    """)

    never_advertised = cur.fetchall()

    print(f"找到 {len(never_advertised)} 个店铺：")
    print()

    for i, row in enumerate(never_advertised, 1):
        domain, visits, city, state, employees, ig, fb, emails, phones, checked = row
        print(f"{i}. {domain}")
        print(f"   访问量：{visits:,}/月")
        print(f"   位置：{city or state}")
        print(f"   员工数：{employees or 'N/A'}")
        print(f"   Instagram：{ig or 'N/A'}")
        print(f"   邮箱：{emails or 'N/A'}")
        print(f"   检查时间：{checked}")
        print()

    # 2. New Advertiser 30d（30天内新客户）
    print("=" * 80)
    print("🔥 类型二：30天内刚开始投放的店铺（new_advertiser_30d）")
    print("-" * 80)

    cur.execute("""
        SELECT
            domain,
            estimated_monthly_visits,
            city,
            state,
            employee_count,
            google_ads_count,
            ads_last_seen_date,
            instagram,
            facebook,
            emails,
            phones,
            ads_last_checked
        FROM stores
        WHERE customer_type = 'new_advertiser_30d'
          AND country_code = 'CN'
        ORDER BY estimated_monthly_visits DESC
    """)

    new_advertisers = cur.fetchall()

    print(f"找到 {len(new_advertisers)} 个店铺：")
    print()

    for i, row in enumerate(new_advertisers, 1):
        domain, visits, city, state, employees, ads_count, last_seen, ig, fb, emails, phones, checked = row
        print(f"{i}. {domain}")
        print(f"   访问量：{visits:,}/月")
        print(f"   位置：{city or state}")
        print(f"   员工数：{employees or 'N/A'}")
        print(f"   广告数：{ads_count}")
        print(f"   最后展示：{last_seen}")
        print(f"   Instagram：{ig or 'N/A'}")
        print(f"   邮箱：{emails or 'N/A'}")
        print(f"   检查时间：{checked}")
        print()

    # 3. 导出 CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # CSV 1: Never Advertised
    csv1_file = f'target_customers_never_advertised_{timestamp}.csv'
    with open(csv1_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow([
            '域名', '月访问量', '城市', '省份', '员工数',
            'Instagram', 'Facebook', '邮箱', '电话', '检查时间'
        ])

        cur.execute("""
            SELECT
                domain, estimated_monthly_visits, city, state, employee_count,
                instagram, facebook, emails, phones, ads_last_checked
            FROM stores
            WHERE customer_type = 'never_advertised'
              AND country_code = 'CN'
            ORDER BY estimated_monthly_visits DESC
        """)

        for row in cur.fetchall():
            writer.writerow(row)

    print("=" * 80)
    print(f"✅ 已导出：{csv1_file}")

    # CSV 2: New Advertiser 30d
    csv2_file = f'target_customers_new_advertiser_30d_{timestamp}.csv'
    with open(csv2_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow([
            '域名', '月访问量', '城市', '省份', '员工数', '广告数', '最后展示时间',
            'Instagram', 'Facebook', '邮箱', '电话', '检查时间'
        ])

        cur.execute("""
            SELECT
                domain, estimated_monthly_visits, city, state, employee_count,
                google_ads_count, ads_last_seen_date,
                instagram, facebook, emails, phones, ads_last_checked
            FROM stores
            WHERE customer_type = 'new_advertiser_30d'
              AND country_code = 'CN'
            ORDER BY estimated_monthly_visits DESC
        """)

        for row in cur.fetchall():
            writer.writerow(row)

    print(f"✅ 已导出：{csv2_file}")
    print()

    # 4. 统计汇总
    print("=" * 80)
    print("📊 最终统计")
    print("=" * 80)
    print()
    print(f"✅ 从未投放广告：{len(never_advertised)} 个店铺")
    print(f"🔥 30天内新广告主：{len(new_advertisers)} 个店铺")
    print(f"📈 总目标客户：{len(never_advertised) + len(new_advertisers)} 个")
    print()
    print("=" * 80)

    cur.close()
    conn.close()


if __name__ == '__main__':
    export_target_customers()
