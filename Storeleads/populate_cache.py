#!/usr/bin/env python3
"""
将之前手动查询的结果填充到缓存中
"""

import json
from datetime import datetime

# 之前的手动查询结果
manual_results = {
    'tfsafari.com': {'has_ads': False, 'ad_count': 0, 'ad_count_text': '0 个广告'},
    'rhinowalk.com': {'has_ads': False, 'ad_count': 0, 'ad_count_text': '0 个广告'},
    'naturnest.com': {'has_ads': True, 'ad_count': 200, 'ad_count_text': '~200 个广告'},
    'topens.com': {'has_ads': True, 'ad_count': 42, 'ad_count_text': '42 个广告'},
    'changliev.com': {'has_ads': False, 'ad_count': 0, 'ad_count_text': '0 个广告'},
    'shuttleart.com': {'has_ads': True, 'ad_count': 1, 'ad_count_text': '1 个广告'},
    'realsteelknives.com': {'has_ads': False, 'ad_count': 0, 'ad_count_text': '0 个广告'},
    'mall.sur-ron.com': {'has_ads': False, 'ad_count': 0, 'ad_count_text': '0 个广告'},
    'shopluebona.com': {'has_ads': True, 'ad_count': 400, 'ad_count_text': '~400 个广告'},
    'usinepro.com': {'has_ads': True, 'ad_count': 62, 'ad_count_text': '62 个广告'},
    'aostirmotor.com': {'has_ads': False, 'ad_count': 0, 'ad_count_text': '0 个广告'},
}

# 创建缓存
cache = {}
timestamp = datetime.now().isoformat()

for domain, data in manual_results.items():
    cache[domain] = {
        'domain': domain,
        'has_ads': data['has_ads'],
        'ad_count': data['ad_count'],
        'ad_count_text': data['ad_count_text'],
        'timestamp': timestamp
    }

# 保存缓存
with open('ads_cache.json', 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

print("✅ 缓存已创建！")
print(f"填充了 {len(cache)} 个域名的数据")
print("\n详细内容：")
for domain, data in cache.items():
    status = '✅' if data['has_ads'] else '⭕'
    print(f"  {status} {domain}: {data['ad_count_text']}")
