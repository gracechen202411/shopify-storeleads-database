#!/usr/bin/env python3
"""
检测 Shopify 店铺是否安装了 Customily 应用
并将结果记录到数据库
"""

import os
import sys
import psycopg2
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime

# 数据库连接
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL_NON_POOLING')

if not DATABASE_URL:
    print("ERROR: Please set DATABASE_URL or POSTGRES_URL_NON_POOLING environment variable")
    print("Run: source .env")
    sys.exit(1)

# Customily 检测特征
CUSTOMILY_PATTERNS = [
    r'customily',
    r'cdn\.shopify\.com/s/files/.*customily',
    r'app\.customily\.com',
    r'customily-app',
    r'customily\.js',
    r'customily-widget'
]

def check_customily_installed(domain):
    """
    检测店铺是否安装了 Customily 应用
    
    返回: (has_customily: bool, details: str)
    """
    try:
        # 确保域名格式正确
        if not domain.startswith('http'):
            url = f'https://{domain}'
        else:
            url = domain
        
        # 请求页面
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        
        if response.status_code != 200:
            return False, f"HTTP {response.status_code}"
        
        html_content = response.text.lower()
        
        # 检查所有 Customily 特征
        found_patterns = []
        for pattern in CUSTOMILY_PATTERNS:
            if re.search(pattern, html_content, re.IGNORECASE):
                found_patterns.append(pattern)
        
        if found_patterns:
            details = f"Found: {', '.join(found_patterns)}"
            return True, details
        
        return False, "No Customily detected"
        
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.RequestException as e:
        return False, f"Error: {str(e)[:100]}"
    except Exception as e:
        return False, f"Exception: {str(e)[:100]}"

def update_store_customily_status(conn, domain, has_customily, details):
    """更新店铺的 Customily 状态到数据库"""
    cur = conn.cursor()
    
    try:
        # 首先检查 stores 表是否有 has_customily 列
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='stores' AND column_name='has_customily'
        """)
        
        if not cur.fetchone():
            # 如果列不存在，创建它
            print("Creating has_customily column...")
            cur.execute("""
                ALTER TABLE stores 
                ADD COLUMN IF NOT EXISTS has_customily BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS customily_check_date TIMESTAMP,
                ADD COLUMN IF NOT EXISTS customily_details TEXT
            """)
            conn.commit()
        
        # 更新店铺记录
        cur.execute("""
            UPDATE stores 
            SET has_customily = %s,
                customily_check_date = %s,
                customily_details = %s
            WHERE domain = %s
        """, (has_customily, datetime.now(), details, domain))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Database error for {domain}: {e}")
        return False
    finally:
        cur.close()

def get_stores_to_check(conn, country_filter=None, limit=None):
    """获取需要检查的店铺列表"""
    cur = conn.cursor()
    
    query = """
        SELECT domain, country_code, estimated_monthly_visits, city, state
        FROM stores
        WHERE domain IS NOT NULL 
        AND domain != ''
        AND (has_customily IS NULL OR customily_check_date IS NULL)
    """
    
    params = []
    
    if country_filter:
        if isinstance(country_filter, list):
            placeholders = ','.join(['%s'] * len(country_filter))
            query += f" AND country_code IN ({placeholders})"
            params.extend(country_filter)
        else:
            query += " AND country_code = %s"
            params.append(country_filter)
    
    query += " ORDER BY estimated_monthly_visits DESC NULLS LAST"
    
    if limit:
        query += f" LIMIT {limit}"
    
    cur.execute(query, params)
    stores = cur.fetchall()
    cur.close()
    
    return stores

def main():
    print("=" * 80)
    print("Customily App Detector for Shopify Stores")
    print("=" * 80)
    
    # 连接数据库
    print("\nConnecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    # 获取要检查的店铺
    print("\nFetching stores to check...")
    
    # 可以指定国家过滤，例如只检查中国和美国的店铺
    # countries = ['CN', 'US']  # 中国和美国
    countries = ['CN', 'HK']  # 或者只检查中国和香港
    
    stores = get_stores_to_check(conn, country_filter=countries, limit=100)
    
    print(f"Found {len(stores)} stores to check")
    
    if not stores:
        print("No stores to check. Exiting.")
        conn.close()
        return
    
    # 显示前几个店铺
    print("\nFirst 5 stores:")
    for i, store in enumerate(stores[:5], 1):
        domain, country, visits, city, state = store
        print(f"  {i}. {domain} ({country}) - {visits:,} visits/month")
    
    # 确认开始
    print("\n" + "=" * 80)
    response = input("Start checking? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        conn.close()
        return
    
    # 开始检查
    print("\n" + "=" * 80)
    print("Starting Customily detection...")
    print("=" * 80)
    
    success_count = 0
    error_count = 0
    customily_found = 0
    
    for i, store in enumerate(stores, 1):
        domain, country, visits, city, state = store
        
        print(f"\n[{i}/{len(stores)}] Checking {domain}...", end=" ")
        
        # 检测 Customily
        has_customily, details = check_customily_installed(domain)
        
        if has_customily:
            print(f"✅ HAS CUSTOMILY - {details}")
            customily_found += 1
        else:
            print(f"⭕ No Customily - {details}")
        
        # 更新数据库
        if update_store_customily_status(conn, domain, has_customily, details):
            success_count += 1
        else:
            error_count += 1
        
        # 每10个显示进度
        if i % 10 == 0:
            print(f"\n{'='*80}")
            print(f"Progress: {i}/{len(stores)} ({i/len(stores)*100:.1f}%)")
            print(f"Customily found: {customily_found}")
            print(f"Success: {success_count}, Errors: {error_count}")
            print(f"{'='*80}")
        
        # 延迟避免被封
        time.sleep(2)
    
    # 最终统计
    print("\n" + "=" * 80)
    print("✅ Detection Complete!")
    print("=" * 80)
    print(f"Total checked: {len(stores)}")
    print(f"Customily found: {customily_found} ({customily_found/len(stores)*100:.1f}%)")
    print(f"Database updates: {success_count}")
    print(f"Errors: {error_count}")
    print("=" * 80)
    
    conn.close()

if __name__ == "__main__":
    main()
