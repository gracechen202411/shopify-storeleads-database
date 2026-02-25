#!/usr/bin/env python3
"""
Customily 检测 - 测试版（前100个店铺）
预计时间：4 分钟
"""

import os
import sys
import psycopg2
import requests
import time
import re
from datetime import datetime

# 数据库连接
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL_NON_POOLING') or os.environ.get('POSTGRES_URL')

if not DATABASE_URL:
    print("❌ ERROR: Please set DATABASE_URL or POSTGRES_URL environment variable")
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
    """检测店铺是否安装了 Customily 应用"""
    try:
        if not domain.startswith('http'):
            url = f'https://{domain}'
        else:
            url = domain
        
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
        # 检查并创建列
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='stores' AND column_name='has_customily'
        """)
        
        if not cur.fetchone():
            print("\n📝 Creating has_customily columns in database...")
            cur.execute("""
                ALTER TABLE stores 
                ADD COLUMN IF NOT EXISTS has_customily BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS customily_check_date TIMESTAMP,
                ADD COLUMN IF NOT EXISTS customily_details TEXT
            """)
            conn.commit()
            print("✅ Columns created successfully")
        
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

def get_stores_to_check(conn, limit=100):
    """获取需要检查的店铺列表"""
    cur = conn.cursor()
    
    # 先检查列是否存在
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='stores' AND column_name='has_customily'
    """)
    
    if not cur.fetchone():
        # 如果列不存在，先创建
        print("📝 Creating has_customily columns...")
        cur.execute("""
            ALTER TABLE stores 
            ADD COLUMN IF NOT EXISTS has_customily BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS customily_check_date TIMESTAMP,
            ADD COLUMN IF NOT EXISTS customily_details TEXT
        """)
        conn.commit()
        print("✅ Columns created")
    
    query = """
        SELECT domain, country_code, estimated_monthly_visits, city, state
        FROM stores
        WHERE domain IS NOT NULL 
        AND domain != ''
        AND country_code IN ('CN', 'HK')
        AND (has_customily IS NULL OR customily_check_date IS NULL)
        ORDER BY estimated_monthly_visits DESC NULLS LAST
        LIMIT %s
    """
    
    cur.execute(query, (limit,))
    stores = cur.fetchall()
    cur.close()
    
    return stores

def main():
    print("=" * 80)
    print("🧪 Customily 检测 - 测试版（前100个店铺）")
    print("=" * 80)
    
    # 连接数据库
    print("\n📡 Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    # 获取要检查的店铺
    print("\n📊 Fetching stores to check...")
    stores = get_stores_to_check(conn, limit=100)
    
    print(f"✅ Found {len(stores)} stores to check")
    
    if not stores:
        print("⚠️  No stores to check. All stores may have been checked already.")
        conn.close()
        return
    
    # 显示前5个店铺
    print("\n📋 First 5 stores:")
    for i, store in enumerate(stores[:5], 1):
        domain, country, visits, city, state = store
        location = f"{city}, {state}" if city and state else country
        visits_str = f"{visits:,}" if visits else "N/A"
        print(f"  {i}. {domain} ({location}) - {visits_str} visits/month")
    
    # 确认开始
    print("\n" + "=" * 80)
    print("⏱️  Estimated time: ~4 minutes")
    print("=" * 80)
    response = input("\n▶️  Start checking? (y/n): ")
    if response.lower() != 'y':
        print("❌ Cancelled.")
        conn.close()
        return
    
    # 开始检查
    print("\n" + "=" * 80)
    print("🚀 Starting Customily detection...")
    print("=" * 80)
    
    start_time = time.time()
    success_count = 0
    error_count = 0
    customily_found = 0
    
    for i, store in enumerate(stores, 1):
        domain, country, visits, city, state = store
        
        visits_str = f"{visits:,}" if visits else "N/A"
        print(f"\n[{i}/{len(stores)}] {domain} ({country}, {visits_str} visits)...", end=" ")
        
        # 检测 Customily
        has_customily, details = check_customily_installed(domain)
        
        if has_customily:
            print(f"✅ CUSTOMILY!")
            print(f"    └─ {details}")
            customily_found += 1
        else:
            print(f"⭕ No Customily")
        
        # 更新数据库
        if update_store_customily_status(conn, domain, has_customily, details):
            success_count += 1
        else:
            error_count += 1
        
        # 每10个显示进度
        if i % 10 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = (len(stores) - i) * avg_time
            
            print(f"\n{'='*80}")
            print(f"📊 Progress: {i}/{len(stores)} ({i/len(stores)*100:.1f}%)")
            print(f"✅ Customily found: {customily_found} ({customily_found/i*100:.1f}%)")
            print(f"⏱️  Elapsed: {int(elapsed//60)}m {int(elapsed%60)}s | Remaining: ~{int(remaining//60)}m {int(remaining%60)}s")
            print(f"{'='*80}")
        
        # 延迟避免被封
        time.sleep(2)
    
    # 最终统计
    elapsed_total = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("✅ 检测完成！")
    print("=" * 80)
    print(f"\n📊 统计结果:")
    print(f"  • 总检测数: {len(stores)}")
    print(f"  • 安装 Customily: {customily_found} ({customily_found/len(stores)*100:.1f}%)")
    print(f"  • 未安装: {len(stores) - customily_found} ({(len(stores)-customily_found)/len(stores)*100:.1f}%)")
    print(f"  • 数据库更新: {success_count}")
    print(f"  • 错误: {error_count}")
    print(f"\n⏱️  总耗时: {int(elapsed_total//60)}分 {int(elapsed_total%60)}秒")
    print(f"  • 平均速度: {elapsed_total/len(stores):.1f}秒/店铺")
    
    print("\n" + "=" * 80)
    print("🎯 下一步:")
    print("=" * 80)
    print("""
1. 查看结果:
   在 Vercel 网站查询: /api/stores?hasCustomily=true

2. 如果结果正常，运行全量检测:
   python3 check_customily_app.py

3. 或者后台运行:
   nohup python3 check_customily_app.py > check.log 2>&1 &
    """)
    print("=" * 80)
    
    conn.close()

if __name__ == "__main__":
    main()
