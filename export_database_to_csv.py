#!/usr/bin/env python3
"""
从数据库导出店铺数据到 CSV 文件
用于在另一台电脑上运行检测（避免数据库连接慢）
"""

import os
import sys
import psycopg2
import csv
from datetime import datetime

# 数据库连接
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL_NON_POOLING') or os.environ.get('POSTGRES_URL')

if not DATABASE_URL:
    print("❌ ERROR: Please set DATABASE_URL or POSTGRES_URL environment variable")
    sys.exit(1)

def export_stores_to_csv(countries, min_visits=None, output_file=None):
    """导出店铺数据到 CSV"""
    
    print("=" * 80)
    print("📊 导出店铺数据到 CSV")
    print("=" * 80)
    
    # 连接数据库
    print("\n📡 Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    cur = conn.cursor()
    
    # 构建查询
    placeholders = ','.join(['%s'] * len(countries))
    
    if min_visits:
        query = f"""
            SELECT 
                domain, country_code, estimated_monthly_visits, 
                city, state, merchant_name, categories,
                emails, instagram, facebook, phones
            FROM stores
            WHERE country_code IN ({placeholders})
            AND estimated_monthly_visits > %s
            AND domain IS NOT NULL 
            AND domain != ''
            ORDER BY estimated_monthly_visits DESC NULLS LAST
        """
        params = countries + [min_visits]
    else:
        query = f"""
            SELECT 
                domain, country_code, estimated_monthly_visits, 
                city, state, merchant_name, categories,
                emails, instagram, facebook, phones
            FROM stores
            WHERE country_code IN ({placeholders})
            AND domain IS NOT NULL 
            AND domain != ''
            ORDER BY estimated_monthly_visits DESC NULLS LAST
        """
        params = countries
    
    print(f"\n📊 Fetching stores...")
    print(f"  Countries: {', '.join(countries)}")
    if min_visits:
        print(f"  Min visits: {min_visits:,}")
    
    cur.execute(query, params)
    stores = cur.fetchall()
    
    print(f"✅ Found {len(stores):,} stores")
    
    # 生成文件名
    if not output_file:
        countries_str = '_'.join(countries).lower()
        visits_str = f"_gt{min_visits}" if min_visits else ""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"stores_{countries_str}{visits_str}_{timestamp}.csv"
    
    # 写入 CSV
    print(f"\n💾 Writing to {output_file}...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # 写入表头
        writer.writerow([
            'domain', 'country_code', 'estimated_monthly_visits',
            'city', 'state', 'merchant_name', 'categories',
            'emails', 'instagram', 'facebook', 'phones'
        ])
        
        # 写入数据
        for store in stores:
            writer.writerow(store)
    
    # 检查文件大小
    file_size = os.path.getsize(output_file)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"✅ Export complete!")
    print(f"\n📊 File info:")
    print(f"  File: {output_file}")
    print(f"  Size: {file_size_mb:.1f} MB")
    print(f"  Stores: {len(stores):,}")
    
    if file_size_mb > 100:
        print(f"\n⚠️  Warning: File is larger than 100MB")
        print(f"  GitHub has a 100MB file size limit")
        print(f"  Consider using Git LFS or splitting the file")
    
    cur.close()
    conn.close()
    
    return output_file

def main():
    print("=" * 80)
    print("📊 数据库导出工具")
    print("=" * 80)
    
    print("\n选择导出方案:")
    print("1) 高流量店铺 (US+CN+HK, >10k visits) - 推荐")
    print("2) 中国 + 香港 (全部)")
    print("3) 美国 (>10k visits)")
    print("4) 所有国家 (>10k visits)")
    print("5) 自定义")
    
    choice = input("\n请选择 (1-5): ")
    
    if choice == '1':
        output_file = export_stores_to_csv(['US', 'CN', 'HK'], min_visits=10000)
    elif choice == '2':
        output_file = export_stores_to_csv(['CN', 'HK'])
    elif choice == '3':
        output_file = export_stores_to_csv(['US'], min_visits=10000)
    elif choice == '4':
        output_file = export_stores_to_csv(['US', 'CN', 'HK', 'VN'], min_visits=10000)
    elif choice == '5':
        countries = input("输入国家代码 (用逗号分隔，如 US,CN,HK): ").split(',')
        countries = [c.strip().upper() for c in countries]
        min_visits_str = input("最小访问量 (留空表示不限制): ")
        min_visits = int(min_visits_str) if min_visits_str else None
        output_file = export_stores_to_csv(countries, min_visits)
    else:
        print("❌ 无效选择")
        return
    
    print("\n" + "=" * 80)
    print("🎯 下一步:")
    print("=" * 80)
    print(f"""
1. 将 CSV 文件提交到 Git:
   git add {output_file}
   git commit -m "Add exported stores CSV"
   git push

2. 在另一台电脑上使用:
   git pull
   python3 check_customily_from_csv.py {output_file}
    """)
    print("=" * 80)

if __name__ == "__main__":
    main()
