#!/usr/bin/env python3
"""
测试用户提供的网站
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
        print(f"Content Length: {len(response.text):,} bytes")
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch page")
            return False, "HTTP Error"
        
        html_content = response.text.lower()
        
        # 检测 Customily 特征
        patterns = {
            'customily_keyword': r'customily',
            'cdn_customily': r'cdn\.shopify\.com/s/files/.*customily',
            'app_url': r'app\.customily\.com',
            'customily_app': r'customily-app',
            'customily_js': r'customily\.js',
            'customily_widget': r'customily-widget',
            'data_customily': r'data-customily'
        }
        
        found = {}
        for name, pattern in patterns.items():
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                found[name] = len(matches)
                print(f"✅ Found: {name} ({len(matches)} occurrences)")
        
        if found:
            print(f"\n🎉 Customily DETECTED!")
            print(f"Indicators: {', '.join(found.keys())}")
            details = f"Indicators: {', '.join(found.keys())}"
            return True, details
        else:
            print(f"\n⭕ No Customily detected")
            return False, "No Customily detected"
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, f"Error: {str(e)[:100]}"

def main():
    print("="*80)
    print("Testing User Provided Websites for Customily")
    print("="*80)
    
    # 用户提供的网站
    test_domains = [
        'https://macorner.co/',
        'https://pawfecthouses.com/',
        'https://afroyla.com/'
    ]
    
    results = {}
    
    for domain in test_domains:
        has_customily, details = test_customily_detection(domain)
        results[domain] = (has_customily, details)
    
    # 总结
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    customily_count = 0
    for domain, (has_customily, details) in results.items():
        status = "✅ HAS CUSTOMILY" if has_customily else "⭕ NO CUSTOMILY"
        print(f"\n{domain}")
        print(f"  Status: {status}")
        print(f"  Details: {details}")
        if has_customily:
            customily_count += 1
    
    print("\n" + "="*80)
    print(f"Total tested: {len(test_domains)}")
    print(f"Customily found: {customily_count}")
    print(f"No Customily: {len(test_domains) - customily_count}")
    print("="*80)

if __name__ == "__main__":
    main()
