#!/usr/bin/env python3
"""
优化的批量Google广告查询脚本
使用缓存机制，生成待查询列表供Claude Code MCP Playwright工具使用
"""

import pandas as pd
import json
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

    def set(self, domain, has_ads, ad_count, ad_count_text):
        self.cache[domain] = {
            'domain': domain,
            'has_ads': has_ads,
            'ad_count': ad_count,
            'ad_count_text': ad_count_text,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()

    def is_fresh(self, domain, max_age_days=30):
        if domain not in self.cache:
            return False
        cached_time = datetime.fromisoformat(self.cache[domain]['timestamp'])
        age = (datetime.now() - cached_time).days
        return age < max_age_days

    def get_all(self):
        return self.cache


def parse_ad_count_text(text):
    """从广告数量文本中解析出数字"""
    if not text or '0 个广告' in text or '未找到' in text:
        return False, 0

    try:
        if '~' in text:
            # ~200 个广告
            num = int(text.split('~')[1].split(' ')[0])
            return True, num
        elif text[0].isdigit():
            # 42 个广告
            num = int(text.split(' ')[0])
            return True, num
    except:
        pass

    return False, 0


def main():
    print("="*100)
    print("📊 批量Google广告查询工具（带缓存）")
    print("="*100)

    # 读取数据
    df = pd.read_csv('hangzhou_stores_20k_200k.csv')

    # 初始化缓存
    cache = AdsCache()

    # 准备数据
    all_domains = []
    cached_domains = []
    to_check_domains = []

    print(f"\n📦 检查缓存状态...\n")

    for _, row in df.iterrows():
        domain = row['domain'].replace('www.', '')
        merchant_name = row['merchant_name']
        monthly_visits = row['estimated_monthly_visits']

        domain_info = {
            'domain': domain,
            'merchant_name': merchant_name,
            'monthly_visits': monthly_visits,
            'url': f"https://adstransparency.google.com/?region=anywhere&domain={domain}"
        }

        all_domains.append(domain_info)

        if cache.is_fresh(domain):
            cached_data = cache.get(domain)
            domain_info.update(cached_data)
            cached_domains.append(domain_info)
            status = '✅' if cached_data.get('has_ads') else '⭕'
            print(f"  {status} 缓存命中: {domain} - {cached_data.get('ad_count_text', '未知')}")
        else:
            to_check_domains.append(domain_info)

    # 统计
    print(f"\n{'='*100}")
    print(f"📊 统计：")
    print(f"  总域名数: {len(all_domains)}")
    print(f"  已缓存: {len(cached_domains)} 个")
    print(f"  需要查询: {len(to_check_domains)} 个")
    print(f"{'='*100}\n")

    # 如果全部已缓存
    if not to_check_domains:
        print("✅ 全部域名已缓存！\n")
        generate_report(cached_domains)
        return

    # 生成待查询列表
    print(f"{'='*100}")
    print(f"🔍 待查询域名列表 ({len(to_check_domains)}个)：")
    print(f"{'='*100}\n")

    # 生成一个查询命令列表文件
    commands = []

    for idx, item in enumerate(to_check_domains, 1):
        print(f"{idx}. {item['merchant_name']} ({item['domain']})")
        print(f"   月访问量: {item['monthly_visits']:,.0f}")
        print(f"   URL: {item['url']}")
        print()

        commands.append({
            'index': idx,
            'domain': item['domain'],
            'merchant_name': item['merchant_name'],
            'url': item['url']
        })

    # 保存为JSON方便后续使用
    with open('domains_to_check.json', 'w', encoding='utf-8') as f:
        json.dump(commands, f, ensure_ascii=False, indent=2)

    print(f"{'='*100}")
    print(f"✅ 待查询列表已保存到: domains_to_check.json")
    print(f"{'='*100}\n")

    # 提供使用说明
    print("📝 使用说明：")
    print("="*100)
    print("1. 使用Claude Code的MCP Playwright工具逐个访问上述URL")
    print("2. 在页面中查找广告数量（如 '~200 个广告' 或 '0 个广告'）")
    print("3. 将结果保存到缓存：")
    print("   python3 -c \"")
    print("from batch_ads_checker_optimized import AdsCache")
    print("cache = AdsCache()")
    print("cache.set('domain.com', True, 200, '~200 个广告')  # 有广告")
    print("cache.set('domain.com', False, 0, '0 个广告')      # 无广告")
    print("\"")
    print("4. 重新运行此脚本查看更新后的结果")
    print("="*100)

    # 如果有已缓存的数据，显示统计
    if cached_domains:
        print(f"\n\n{'='*100}")
        print(f"📊 已缓存的{len(cached_domains)}个域名统计：")
        print(f"{'='*100}\n")
        generate_report(cached_domains)


def generate_report(domains):
    """生成报告"""
    # 统计
    has_ads_count = sum(1 for d in domains if d.get('has_ads', False))
    no_ads_count = len(domains) - has_ads_count
    total_ads = sum(d.get('ad_count', 0) for d in domains)

    print(f"统计结果：")
    print(f"  ✅ 有广告: {has_ads_count} 个")
    print(f"  ⭕ 无广告: {no_ads_count} 个")
    print(f"  📊 广告总数: {total_ads} 个\n")

    # 按广告数量排序
    sorted_domains = sorted(domains, key=lambda x: x.get('ad_count', 0), reverse=True)

    print("详细列表（按广告数量排序）：")
    print("-"*100)
    for d in sorted_domains:
        status = '✅' if d.get('has_ads') else '⭕'
        ad_text = d.get('ad_count_text', '未知')
        print(f"{status} {d['merchant_name']:30} ({d['domain']:30}) - {ad_text}")

    # 保存结果
    df_results = pd.DataFrame(sorted_domains)
    df_results.to_csv('ads_check_results_cached.csv', index=False, encoding='utf-8-sig')
    print(f"\n✅ 结果已保存到: ads_check_results_cached.csv\n")


if __name__ == '__main__':
    main()
