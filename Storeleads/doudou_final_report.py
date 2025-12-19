#!/usr/bin/env python3
"""
豆豆的新客户报告 - 最终版本
"""
from datetime import datetime
import json

# 检查结果
results = {
    '新客户（从来没打过广告）': [
        {'domain': 'www.tfsafari.com', 'monthly_visits': 75729, 'reason': '从来没打过谷歌广告'},
        {'domain': 'rhinowalk.com', 'monthly_visits': 41266, 'reason': '从来没打过谷歌广告'},
        {'domain': 'www.changliev.com', 'monthly_visits': None, 'reason': '从来没打过谷歌广告'},
        {'domain': 'www.realsteelknives.com', 'monthly_visits': None, 'reason': '从来没打过谷歌广告'},
        {'domain': 'mall.sur-ron.com', 'monthly_visits': None, 'reason': '从来没打过谷歌广告'},
        {'domain': 'www.aostirmotor.com', 'monthly_visits': None, 'reason': '从来没打过谷歌广告'},
    ],
    '老客户（不适合）': [
        {'domain': 'www.naturnest.com', 'ads': 200, 'advertiser': '杭州极峰户外用品有限公司', 'reason': '30天前有40个广告，一直在投放'},
        {'domain': 'topens.com', 'ads': 40, 'advertiser': '杭州三富科技有限公司', 'reason': '30天前有40个广告，一直在投放'},
        {'domain': 'shuttleart.com', 'ads': 1, 'advertiser': '杭州简屹进出口有限公司', 'reason': '30天前有1个广告，一直在投放'},
        {'domain': 'www.shopluebona.com', 'ads': 400, 'advertiser': '杭州起兮家具有限公司', 'reason': '大规模投放，老客户'},
        {'domain': 'usinepro.com', 'ads': 63, 'advertiser': 'HANGZHOU YUJING NETWORK TECHNOLOGY CO,.LTD.', 'reason': '中规模投放，老客户'},
    ]
}

print("="*100)
print("🎯 豆豆的新客户报告 - 2025年12月18日")
print("="*100)

print(f"\n📊 检查统计：")
print(f"- 总共检查：11个店铺")
print(f"- 🔥 新客户（从来没打过广告）：{len(results['新客户（从来没打过广告）'])}个")
print(f"- ❌ 老客户（不适合）：{len(results['老客户（不适合）'])}个")

print(f"\n{'='*100}")
print(f"🔥 豆豆的目标客户清单（从来没打过谷歌广告）")
print(f"{'='*100}")

for i, customer in enumerate(results['新客户（从来没打过广告）'], 1):
    print(f"\n{i}. {customer['domain']}")
    if customer['monthly_visits']:
        print(f"   月访问量：{customer['monthly_visits']:,}")
    print(f"   状态：{customer['reason']}")
    print(f"   💡 豆豆的策略：联系他们，介绍谷歌广告的价值，帮助他们开始投放")

print(f"\n{'='*100}")
print(f"❌ 老客户（暂时不适合）")
print(f"{'='*100}")

for i, customer in enumerate(results['老客户（不适合）'], 1):
    print(f"\n{i}. {customer['domain']}")
    print(f"   广告数量：{customer['ads']}个")
    if 'advertiser' in customer:
        print(f"   广告主：{customer['advertiser']}")
    print(f"   原因：{customer['reason']}")

print(f"\n{'='*100}")
print(f"总结")
print(f"{'='*100}")
print(f"""
豆豆有 6 个高质量的新客户线索！

这些店铺的特点：
✅ 都是浙江（主要是杭州）的Shopify店铺
✅ 从来没打过谷歌广告 = 没有被代理商签走
✅ 有一定的流量和规模（前两个月访问量不错）
✅ 可以直接联系，介绍谷歌广告的好处

建议豆豆的话术：
1. "您好，我是谷歌广告的直客经理..."
2. "发现贵公司还没开始做谷歌广告，想介绍一下..."
3. "谷歌广告可以帮您获取海外精准客户..."
4. "我们提供免费的账号诊断和投放建议..."

⚠️ 注意：老客户已经有代理商或自己在投放，暂时不要打扰
""")

# 保存JSON报告
report = {
    'generated_at': datetime.now().isoformat(),
    'total_checked': 11,
    'new_customers': len(results['新客户（从来没打过广告）']),
    'old_customers': len(results['老客户（不适合）']),
    'details': results
}

with open('doudou_new_customers_final_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"✅ 详细报告已保存：doudou_new_customers_final_report.json")
