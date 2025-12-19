#!/usr/bin/env python3
"""
快速添加查询结果到缓存
"""

from batch_ads_checker_optimized import AdsCache

cache = AdsCache()

# 根据MCP Playwright查询结果，快速批量添加
# 格式: (domain, has_ads, ad_count, ad_count_text)

results_to_add = [
    # 第1个已查询
    ('dp200.yeswelder.com', False, 0, '0 个广告'),

    # 待添加其他查询结果...
    # 使用方式: 查询完一个就添加一个，然后重新运行 batch_ads_check_zhejiang.py
]

for domain, has_ads, ad_count, ad_count_text in results_to_add:
    cache.set(domain, has_ads, ad_count, ad_count_text)
    status = '✅' if has_ads else '⭕'
    print(f"{status} 已添加: {domain} - {ad_count_text}")

print(f"\n✅ 共添加 {len(results_to_add)} 条记录到缓存")
print(f"\n运行以下命令查看更新后的结果:")
print(f"python3 batch_ads_check_zhejiang.py")
