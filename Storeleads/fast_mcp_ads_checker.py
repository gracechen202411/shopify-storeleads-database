#!/usr/bin/env python3
"""
使用已有MCP Playwright工具的快速批量查询
通过缓存机制加速
"""

import pandas as pd
import json
import time
from datetime import datetime
from pathlib import Path

# 缓存文件
CACHE_FILE = 'ads_cache.json'

class AdsCache:
    def __init__(self, cache_file=CACHE_FILE):
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self):
        if Path(self.cache_file).exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def get(self, domain):
        return self.cache.get(domain)

    def set(self, domain, data):
        self.cache[domain] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()

    def is_fresh(self, domain, max_age_days=7):
        if domain not in self.cache:
            return False
        cached_time = datetime.fromisoformat(self.cache[domain]['timestamp'])
        age = (datetime.now() - cached_time).days
        return age < max_age_days


def main():
    print("="*100)
    print("📊 Google广告批量查询工具（使用缓存加速）")
    print("="*100)

    # 读取数据
    df = pd.read_csv('hangzhou_stores_20k_200k.csv')

    # 准备域名列表
    domains_data = []
    for _, row in df.iterrows():
        domain = row['domain'].replace('www.', '')
        domains_data.append({
            'domain': domain,
            'merchant_name': row['merchant_name'],
            'monthly_visits': row['estimated_monthly_visits']
        })

    print(f"\n📊 总共 {len(domains_data)} 个域名\n")

    # 初始化缓存
    cache = AdsCache()

    # 检查缓存
    results = []
    to_check = []

    print("📦 检查缓存...")
    for item in domains_data:
        domain = item['domain']
        if cache.is_fresh(domain):
            cached = cache.get(domain)['data']
            results.append(cached)
            print(f"  ✅ 缓存命中: {domain}")
        else:
            to_check.append(item)

    if not to_check:
        print(f"\n✅ 全部来自缓存！")
    else:
        print(f"\n🔍 需要查询: {len(to_check)} 个域名")
        print(f"\n{'='*100}")
        print("请手动使用Claude Code的MCP Playwright工具逐个查询以下域名：")
        print(f"{'='*100}\n")

        for idx, item in enumerate(to_check, 1):
            domain = item['domain']
            url = f"https://adstransparency.google.com/?region=anywhere&domain={domain}"
            print(f"{idx}. {item['merchant_name']} ({domain})")
            print(f"   URL: {url}")
            print()

        print(f"{'='*100}")
        print("提示：对每个域名，查找页面中的广告数量文本（如'~200 个广告'或'0 个广告'）")
        print("然后手动输入结果到缓存中")
        print(f"{'='*100}\n")

        # 提供一个简单的手动输入接口
        print("如果您想手动输入结果，可以编辑 ads_cache.json 文件")
        print("格式示例：")
        print(json.dumps({
            "example.com": {
                "data": {
                    "domain": "example.com",
                    "has_ads": True,
                    "ad_count": 200,
                    "ad_count_text": "~200 个广告"
                },
                "timestamp": datetime.now().isoformat()
            }
        }, ensure_ascii=False, indent=2))

    # 如果有结果，生成报告
    if results:
        print(f"\n{'='*100}")
        print(f"📊 已缓存的{len(results)}个域名的结果：")
        print(f"{'='*100}\n")

        df_results = pd.DataFrame(results)
        print(df_results.to_string(index=False))

        # 统计
        has_ads = sum(1 for r in results if r.get('has_ads', False))
        total_ads = sum(r.get('ad_count', 0) for r in results)

        print(f"\n{'='*100}")
        print(f"统计：")
        print(f"  ✅ 有广告: {has_ads} 个")
        print(f"  ⭕ 无广告: {len(results) - has_ads} 个")
        print(f"  📊 广告总数: {total_ads} 个")
        print(f"{'='*100}\n")


if __name__ == '__main__':
    main()
