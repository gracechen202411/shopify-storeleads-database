#!/usr/bin/env python3
"""
估算 Customily 检测所需时间
"""

import os
import psycopg2

# 数据库连接
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL_NON_POOLING')

def estimate_detection_time():
    print("="*80)
    print("Customily Detection Time Estimation")
    print("="*80)
    
    if not DATABASE_URL:
        print("\n⚠️  Database URL not found, using CSV file estimate")
        print("\nFrom CSV file: ~6,251 stores (China + Hong Kong)")
        total_stores = 6251
    else:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            # 统计各国店铺数量
            cur.execute("""
                SELECT 
                    country_code,
                    COUNT(*) as count
                FROM stores
                WHERE domain IS NOT NULL AND domain != ''
                GROUP BY country_code
                ORDER BY count DESC
            """)
            
            countries = cur.fetchall()
            
            print("\n📊 Stores by Country:")
            print("-" * 40)
            
            cn_count = 0
            hk_count = 0
            us_count = 0
            total_stores = 0
            
            for country, count in countries[:10]:
                print(f"  {country}: {count:,} stores")
                if country == 'CN':
                    cn_count = count
                elif country == 'HK':
                    hk_count = count
                elif country == 'US':
                    us_count = count
                total_stores += count
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"\n⚠️  Database error: {e}")
            print("Using CSV file estimate instead")
            cn_count = 4000
            hk_count = 2251
            us_count = 0
            total_stores = 6251
    
    print("\n" + "="*80)
    print("Time Estimation")
    print("="*80)
    
    # 快速版估算
    print("\n🚀 Quick Mode (requests):")
    print("-" * 40)
    quick_time_per_store = 2.5  # 秒
    
    scenarios = [
        ("China + Hong Kong", cn_count + hk_count if cn_count else 6251),
        ("China only", cn_count if cn_count else 4000),
        ("Hong Kong only", hk_count if hk_count else 2251),
        ("First 100 stores", 100),
        ("First 50 stores", 50),
    ]
    
    for name, count in scenarios:
        total_seconds = count * quick_time_per_store
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        print(f"  {name} ({count:,} stores):")
        if hours > 0:
            print(f"    ⏱️  ~{hours}h {minutes}m")
        else:
            print(f"    ⏱️  ~{minutes}m")
    
    # Selenium 版估算
    print("\n🔍 Selenium Mode (more accurate):")
    print("-" * 40)
    selenium_time_per_store = 6.5  # 秒
    
    for name, count in scenarios:
        total_seconds = count * selenium_time_per_store
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        print(f"  {name} ({count:,} stores):")
        if hours > 0:
            print(f"    ⏱️  ~{hours}h {minutes}m")
        else:
            print(f"    ⏱️  ~{minutes}m")
    
    print("\n" + "="*80)
    print("💡 Recommendations")
    print("="*80)
    print("""
1. 🎯 Start Small (Recommended):
   - Test with 50-100 stores first
   - Time: ~2-4 minutes (Quick) or ~5-10 minutes (Selenium)
   - Verify results before full run

2. 📊 Medium Batch:
   - Run 500-1000 stores
   - Time: ~20-40 minutes (Quick) or ~50-100 minutes (Selenium)
   - Good for initial screening

3. 🚀 Full Run:
   - All 6,251 stores
   - Time: ~4-5 hours (Quick) or ~11-12 hours (Selenium)
   - Best to run overnight or in background

4. ⚡ Parallel Processing (Advanced):
   - Split into multiple processes
   - Can reduce time by 50-70%
   - Requires more system resources
    """)
    
    print("="*80)
    print("🎬 Ready to Start?")
    print("="*80)
    print("""
Quick Start Commands:

# Test with 10 stores (2 minutes)
python3 check_customily_app.py  # Edit line 145: limit=10

# Small batch - 50 stores (2 minutes)
python3 check_customily_app.py  # Edit line 145: limit=50

# Medium batch - 500 stores (20 minutes)
python3 check_customily_app.py  # Edit line 145: limit=500

# Full run - All stores (4-5 hours)
python3 check_customily_app.py  # Default: no limit

# Run in background (recommended for large batches)
nohup python3 check_customily_app.py > customily_check.log 2>&1 &
    """)

if __name__ == "__main__":
    estimate_detection_time()
