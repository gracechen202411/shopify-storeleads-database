#!/usr/bin/env python3
"""
测试 Customily 检测功能
"""

import requests
import re

def test_customily_detection(domain):
    """测试单个域名的 Customily 检测"""
    print(f"\n{'='*80}")
    print(f"Testing: {domain}")
    print(f"{'='*80}")
    
    try:
        if not domain.startswith('http'):
            url = f'https://{domain}'
        else:
            url = domain
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        print(f"Fetching {url}...")
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text)} bytes")
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch page")
            return False
        
        html_content = response.text.lower()
        
        # 检测 Customily 特征
        patterns = {
            'customily_keyword': r'customily',
            'cdn_url': r'cdn\.shopify\.com/s/files/.*customily',
            'app_url': r'app\.customily\.com',
            'customily_app': r'customily-app',
            'customily_js': r'customily\.js',
            'customily_widget': r'customily-widget'
        }
        
        found = {}
        for name, pattern in patterns.items():
            if re.search(pattern, html_content, re.IGNORECASE):
                found[name] = True
                print(f"✅ Found: {name}")
        
        if found:
            print(f"\n🎉 Customily DETECTED!")
            print(f"Indicators: {', '.join(found.keys())}")
            return True
        else:
            print(f"\n⭕ No Customily detected")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("="*80)
    print("Customily Detection Test")
    print("="*80)
    
    # 测试已知安装了 Customily 的网站
    test_domains = [
        'evridwearcustom.com',  # 已知安装了 Customily
        'keychron.com',         # 测试其他店铺
        'nothing.tech',         # 测试其他店铺
    ]
    
    results = {}
    
    for domain in test_domains:
        has_customily = test_customily_detection(domain)
        results[domain] = has_customily
    
    # 总结
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    for domain, has_customily in results.items():
        status = "✅ HAS CUSTOMILY" if has_customily else "⭕ NO CUSTOMILY"
        print(f"{domain}: {status}")
    
    print("="*80)

if __name__ == "__main__":
    main()
