#!/usr/bin/env python3
from batch_check_new_starters import NewStarterChecker, DB_CONFIG
from datetime import datetime

checker = NewStarterChecker(DB_CONFIG)

# 已检查的结果
results = {
    'www.tfsafari.com': {
        'has_any_ads': False,
        'total_ad_count': 0,
        'has_ads_before_30_days': False,
        'ad_count_before_30_days': 0,
        'is_new_customer': True,  # 从来没打过广告
        'checked_at': datetime.now().isoformat()
    },
    'rhinowalk.com': {
        'has_any_ads': False,
        'total_ad_count': 0,
        'has_ads_before_30_days': False,
        'ad_count_before_30_days': 0,
        'is_new_customer': True,  # 从来没打过广告
        'checked_at': datetime.now().isoformat()
    },
    'www.naturnest.com': {
        'has_any_ads': True,
        'total_ad_count': 200,
        'has_ads_before_30_days': True,  # 30天前有40个广告
        'ad_count_before_30_days': 40,
        'is_new_customer': False,  # 老客户
        'checked_at': datetime.now().isoformat()
    },
    'topens.com': {
        'has_any_ads': True,
        'total_ad_count': 40,
        'has_ads_before_30_days': True,  # 30天前也有40个广告
        'ad_count_before_30_days': 40,
        'is_new_customer': False,  # 老客户
        'checked_at': datetime.now().isoformat()
    }
}

for domain, result in results.items():
    checker.add_check_result(domain, result)
    print(f"✅ 已保存 {domain} 的结果")

print("\n当前进度：已检查 4/11 个店铺")
