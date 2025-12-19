#!/usr/bin/env python3
"""
批量查询杭州店铺的Google广告数据
使用 Google-Ads-Transparency-Scraper 工具
"""

import pandas as pd
from GoogleAds import GoogleAds
import time
import json

# Initialize scraper
scraper = GoogleAds()

# 读取杭州店铺数据
df = pd.read_csv('hangzhou_stores_20k_200k.csv')

# 准备结果存储
results = []

print("="*100)
print("开始批量查询11家杭州店铺的Google广告数据")
print("="*100)

# 遍历每个店铺
for idx, row in df.iterrows():
    store_num = idx + 1
    domain = row['domain'].replace('www.', '')
    merchant_name = row['merchant_name']

    print(f"\n{'='*100}")
    print(f"[{store_num}/11] 正在查询: {merchant_name} ({domain})")
    print(f"{'='*100}")

    try:
        # 搜索广告主
        print(f"🔍 搜索广告主...")
        suggestions = scraper.get_all_search_suggestions(domain)

        if not suggestions or 'advertisers' not in suggestions:
            print(f"❌ 未找到广告数据")
            results.append({
                'store_num': store_num,
                'domain': domain,
                'merchant_name': merchant_name,
                'has_ads': False,
                'advertiser_count': 0,
                'total_creatives': 0,
                'advertisers': []
            })
            continue

        advertisers = suggestions.get('advertisers', [])

        if not advertisers:
            print(f"❌ 未找到广告主")
            results.append({
                'store_num': store_num,
                'domain': domain,
                'merchant_name': merchant_name,
                'has_ads': False,
                'advertiser_count': 0,
                'total_creatives': 0,
                'advertisers': []
            })
            continue

        print(f"✅ 找到 {len(advertisers)} 个广告主")

        # 获取每个广告主的创意数量
        advertiser_details = []
        total_creatives = 0

        for adv in advertisers:
            advertiser_id = adv.get('advertiser_id', '')
            advertiser_name = adv.get('advertiser_name', '')

            print(f"  📊 广告主: {advertiser_name}")

            try:
                # 获取创意ID列表
                creative_ids = scraper.get_creative_Ids(domain, count=200)

                if creative_ids:
                    creative_count = len(creative_ids)
                    total_creatives += creative_count
                    print(f"     └─ 找到 {creative_count} 个广告创意")

                    advertiser_details.append({
                        'advertiser_id': advertiser_id,
                        'advertiser_name': advertiser_name,
                        'creative_count': creative_count,
                        'creative_ids': creative_ids[:5]  # 只保存前5个ID作为样本
                    })
                else:
                    print(f"     └─ 未找到广告创意")
                    advertiser_details.append({
                        'advertiser_id': advertiser_id,
                        'advertiser_name': advertiser_name,
                        'creative_count': 0,
                        'creative_ids': []
                    })

            except Exception as e:
                print(f"     └─ ⚠️ 查询失败: {str(e)}")
                advertiser_details.append({
                    'advertiser_id': advertiser_id,
                    'advertiser_name': advertiser_name,
                    'creative_count': 0,
                    'creative_ids': [],
                    'error': str(e)
                })

        print(f"\n✅ {merchant_name} 总计: {total_creatives} 个广告")

        results.append({
            'store_num': store_num,
            'domain': domain,
            'merchant_name': merchant_name,
            'has_ads': True,
            'advertiser_count': len(advertisers),
            'total_creatives': total_creatives,
            'advertisers': advertiser_details
        })

    except Exception as e:
        print(f"❌ 查询出错: {str(e)}")
        results.append({
            'store_num': store_num,
            'domain': domain,
            'merchant_name': merchant_name,
            'has_ads': False,
            'advertiser_count': 0,
            'total_creatives': 0,
            'error': str(e)
        })

    # 延迟避免被封
    if store_num < 11:
        print(f"\n⏳ 等待3秒后继续...")
        time.sleep(3)

# 保存结果
print(f"\n{'='*100}")
print("保存结果...")
print(f"{'='*100}")

# 保存JSON格式（完整数据）
with open('google_ads_batch_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# 生成汇总报告
summary = []
for r in results:
    summary.append({
        '店铺序号': r['store_num'],
        '域名': r['domain'],
        '商家名称': r['merchant_name'],
        '有广告': '✅' if r['has_ads'] else '❌',
        '广告主数量': r['advertiser_count'],
        '广告总数': r['total_creatives']
    })

df_summary = pd.DataFrame(summary)
df_summary.to_csv('google_ads_summary.csv', index=False, encoding='utf-8-sig')

# 打印汇总
print(f"\n{'='*100}")
print("查询汇总")
print(f"{'='*100}\n")
print(df_summary.to_string(index=False))

print(f"\n{'='*100}")
print("统计")
print(f"{'='*100}")
print(f"总店铺数: 11")
print(f"有广告: {sum(1 for r in results if r['has_ads'])}")
print(f"无广告: {sum(1 for r in results if not r['has_ads'])}")
print(f"广告总数: {sum(r['total_creatives'] for r in results)}")

print(f"\n✅ 结果已保存:")
print(f"  - google_ads_batch_results.json (完整数据)")
print(f"  - google_ads_summary.csv (汇总表)")

print(f"\n{'='*100}")
print("完成！")
print(f"{'='*100}")
