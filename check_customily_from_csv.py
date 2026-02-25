#!/usr/bin/env python3
"""
从本地 CSV 文件读取店铺数据并检测 Customily
适用于数据库连接慢的情况
"""

import sys
import csv
import requests
import time
import re
from datetime import datetime
import json

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
                found_patterns.append(pattern.replace('\\', ''))
        
        if found_patterns:
            details = f"Found: {', '.join(found_patterns[:3])}"
            return True, details
        
        return False, "No Customily detected"
        
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.RequestException as e:
        return False, f"Error: {str(e)[:100]}"
    except Exception as e:
        return False, f"Exception: {str(e)[:100]}"

def load_stores_from_csv(csv_file):
    """从 CSV 文件加载店铺数据"""
    stores = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stores.append(row)
    
    return stores

def save_results_to_json(results, output_file):
    """保存结果到 JSON 文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check_customily_from_csv.py <csv_file>")
        print("\nExample:")
        print("  python3 check_customily_from_csv.py stores_us_cn_hk_gt10000_20250225.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    print("=" * 80)
    print("🎯 Customily 检测 - CSV 模式")
    print("=" * 80)
    
    # 加载店铺数据
    print(f"\n📂 Loading stores from {csv_file}...")
    try:
        stores = load_stores_from_csv(csv_file)
        print(f"✅ Loaded {len(stores):,} stores")
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}")
        sys.exit(1)
    
    # 显示前5个
    print("\n📋 Sample stores:")
    for i, store in enumerate(stores[:5], 1):
        visits = store.get('estimated_monthly_visits', 'N/A')
        print(f"  {i}. {store['domain']} ({store['country_code']}) - {visits} visits/month")
    
    # 时间估算
    estimated_hours = (len(stores) * 5) / 3600
    estimated_days = estimated_hours / 24
    
    print(f"\n⏱️  Estimated time: {estimated_days:.1f} days ({estimated_hours:.0f} hours)")
    
    print("\n" + "=" * 80)
    print("🚀 Starting detection...")
    print("=" * 80)
    
    # 开始检查
    start_time = time.time()
    customily_found = 0
    results = []
    
    for i, store in enumerate(stores, 1):
        domain = store['domain']
        country = store['country_code']
        visits = store.get('estimated_monthly_visits', 'N/A')
        
        print(f"\n[{i}/{len(stores)}] {domain} ({country}, {visits})...", end=" ", flush=True)
        
        # 检测 Customily
        has_customily, details = check_customily_installed(domain)
        
        if has_customily:
            print(f"✅ CUSTOMILY!")
            print(f"    └─ {details}")
            customily_found += 1
        else:
            print(f"⭕")
        
        # 保存结果
        result = {
            'domain': domain,
            'country_code': country,
            'estimated_monthly_visits': visits,
            'has_customily': has_customily,
            'customily_details': details,
            'check_date': datetime.now().isoformat()
        }
        results.append(result)
        
        # 每100个显示进度并保存
        if i % 100 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = (len(stores) - i) * avg_time
            remaining_hours = remaining / 3600
            
            print(f"\n{'='*80}")
            print(f"📊 Progress: {i:,}/{len(stores):,} ({i/len(stores)*100:.1f}%)")
            print(f"✅ Customily found: {customily_found} ({customily_found/i*100:.2f}%)")
            print(f"⏱️  Elapsed: {elapsed/3600:.1f}h | Remaining: ~{remaining_hours:.1f}h")
            print(f"{'='*80}")
            
            # 保存中间结果
            output_file = f"customily_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_results_to_json(results, output_file)
            print(f"💾 Results saved to {output_file}")
        
        # 延迟
        if i < len(stores):
            time.sleep(2)
    
    # 最终统计
    elapsed_total = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("✅ 检测完成！")
    print("=" * 80)
    print(f"\n📊 统计结果:")
    print(f"  • 总检测数: {len(stores):,}")
    print(f"  • 安装 Customily: {customily_found} ({customily_found/len(stores)*100:.2f}%)")
    print(f"  • 未安装: {len(stores) - customily_found:,}")
    print(f"\n⏱️  总耗时: {elapsed_total/3600:.1f} 小时 ({elapsed_total/86400:.1f} 天)")
    print(f"  • 平均速度: {elapsed_total/len(stores):.1f}秒/店铺")
    
    # 保存最终结果
    output_file = f"customily_results_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_results_to_json(results, output_file)
    
    # 保存 Customily 店铺到单独的文件
    customily_stores = [r for r in results if r['has_customily']]
    if customily_stores:
        customily_file = f"customily_stores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_results_to_json(customily_stores, customily_file)
        print(f"\n💾 Results saved:")
        print(f"  • All results: {output_file}")
        print(f"  • Customily stores: {customily_file}")
    else:
        print(f"\n💾 Results saved: {output_file}")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
