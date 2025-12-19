#!/usr/bin/env python3
"""
批量查询浙江2024年店铺的Google广告
使用缓存机制
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

# 导入缓存类
from batch_ads_checker_optimized import AdsCache

def main():
    print("="*100)
    print("批量查询浙江2024年店铺的Google广告")
    print("="*100)

    # 读取筛选后的数据
    df = pd.read_csv('zhejiang_2024_1000plus.csv')
    print(f"\n📊 共 {len(df)} 家店铺需要查询\n")

    # 初始化缓存
    cache = AdsCache()

    # 准备查询
    results = []
    cached_count = 0
    to_check_count = 0

    print("="*100)
    print("检查缓存状态...")
    print("="*100 + "\n")

    for idx, row in df.iterrows():
        domain = row['domain'].replace('www.', '')
        merchant_name = row['merchant_name']
        monthly_visits = row['estimated_monthly_visits']

        # 检查缓存
        if cache.is_fresh(domain):
            cached_data = cache.get(domain)
            result = {
                'index': idx + 1,
                'domain': row['domain'],
                'merchant_name': merchant_name,
                'company_location': row['company_location'],
                'created': row['created'],
                'estimated_monthly_visits': monthly_visits,
                'estimated_yearly_sales': row['estimated_yearly_sales'],
                'has_google_ads': '✅ 有' if cached_data['has_ads'] else '❌ 无',
                'ad_count': cached_data['ad_count'],
                'ad_count_text': cached_data['ad_count_text'],
                'from_cache': True
            }
            status = '✅' if cached_data['has_ads'] else '⭕'
            print(f"{idx+1}. {status} 缓存: {merchant_name} ({domain}) - {cached_data['ad_count_text']}")
            cached_count += 1
        else:
            result = {
                'index': idx + 1,
                'domain': row['domain'],
                'merchant_name': merchant_name,
                'company_location': row['company_location'],
                'created': row['created'],
                'estimated_monthly_visits': monthly_visits,
                'estimated_yearly_sales': row['estimated_yearly_sales'],
                'has_google_ads': '⏳ 待查询',
                'ad_count': None,
                'ad_count_text': '待查询',
                'from_cache': False,
                'check_url': f"https://adstransparency.google.com/?region=anywhere&domain={domain}"
            }
            print(f"{idx+1}. 🔍 待查: {merchant_name} ({domain})")
            to_check_count += 1

        results.append(result)

    # 保存结果
    df_results = pd.DataFrame(results)

    # 选择要保存的列
    output_cols = [
        'index', 'domain', 'merchant_name', 'company_location', 'created',
        'estimated_monthly_visits', 'estimated_yearly_sales',
        'has_google_ads', 'ad_count_text'
    ]

    df_output = df_results[output_cols].copy()
    df_output.to_csv('zhejiang_2024_with_google_ads.csv', index=False, encoding='utf-8-sig')

    print(f"\n{'='*100}")
    print("统计")
    print(f"{'='*100}")
    print(f"总店铺数: {len(results)}")
    print(f"已缓存: {cached_count} 个")
    print(f"待查询: {to_check_count} 个")

    if cached_count > 0:
        has_ads = sum(1 for r in results if r.get('from_cache') and '✅' in r.get('has_google_ads', ''))
        print(f"\n已查询店铺中:")
        print(f"  有广告: {has_ads} 个")
        print(f"  无广告: {cached_count - has_ads} 个")

    print(f"\n✅ 结果已保存到: zhejiang_2024_with_google_ads.csv")

    # 如果有待查询的域名
    if to_check_count > 0:
        print(f"\n{'='*100}")
        print(f"🔍 待查询列表 ({to_check_count}个):")
        print(f"{'='*100}\n")

        to_check_list = [r for r in results if not r['from_cache']]

        for item in to_check_list:
            print(f"{item['index']}. {item['merchant_name']} ({item['domain']})")
            print(f"   月访问量: {item['estimated_monthly_visits']:,.0f}")
            print(f"   查询URL: {item['check_url']}")
            print()

        # 保存待查询列表
        with open('zhejiang_domains_to_check.json', 'w', encoding='utf-8') as f:
            json.dump(to_check_list, f, ensure_ascii=False, indent=2)

        print(f"✅ 待查询列表已保存到: zhejiang_domains_to_check.json")

        print(f"\n{'='*100}")
        print("📝 查询步骤:")
        print(f"{'='*100}")
        print("1. 使用Claude Code的MCP Playwright工具访问上述URL")
        print("2. 查看页面中的广告数量（如 '~200 个广告' 或 '0 个广告'）")
        print("3. 将结果添加到缓存:")
        print("\n   python3 -c \"")
        print("from batch_ads_checker_optimized import AdsCache")
        print("cache = AdsCache()")
        print("cache.set('domain.com', True, 200, '~200 个广告')  # 有广告")
        print("cache.set('domain.com', False, 0, '0 个广告')      # 无广告")
        print("\"")
        print("\n4. 重新运行此脚本查看更新后的结果:")
        print("   python3 batch_ads_check_zhejiang.py")
        print(f"{'='*100}")

    else:
        print(f"\n{'='*100}")
        print("✅ 全部店铺已查询完成！")
        print(f"{'='*100}")

        # 显示最终统计
        print(f"\n📊 最终统计:")
        has_ads_list = [r for r in results if '✅' in r.get('has_google_ads', '')]
        no_ads_list = [r for r in results if '❌' in r.get('has_google_ads', '')]

        print(f"  有广告: {len(has_ads_list)} 个")
        print(f"  无广告: {len(no_ads_list)} 个")

        if has_ads_list:
            print(f"\n有广告的店铺（按广告数量排序）:")
            print("-"*100)
            sorted_ads = sorted(has_ads_list, key=lambda x: x.get('ad_count', 0) or 0, reverse=True)
            for r in sorted_ads:
                print(f"  ✅ {r['merchant_name']:40} - {r['ad_count_text']:20} (月访问{r['estimated_monthly_visits']:,.0f})")


if __name__ == '__main__':
    main()
