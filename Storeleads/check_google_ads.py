import pandas as pd
import time
from urllib.parse import urlparse

# Read the filtered stores
df = pd.read_csv('hangzhou_stores_20k_200k.csv')

# Extract clean domains
def clean_domain(domain):
    """Extract base domain without www"""
    if pd.isna(domain):
        return None
    domain = domain.replace('www.', '')
    # Remove any path
    if '/' in domain:
        domain = domain.split('/')[0]
    return domain

df['clean_domain'] = df['domain'].apply(clean_domain)

# Generate Google Ads Transparency URLs
df['google_ads_url'] = df['clean_domain'].apply(
    lambda x: f"https://adstransparency.google.com/?region=anywhere&domain={x}" if pd.notna(x) else None
)

print("=" * 100)
print("杭州店铺 Google 广告透明度检查链接")
print("=" * 100)
print("\n请手动访问以下链接检查每个店铺的Google广告投放情况：")
print("有广告数据 = 正在投放Google广告")
print("无广告数据 = 未投放Google广告\n")

results = []

for idx, row in df.iterrows():
    store_num = df.index.get_loc(idx) + 1
    print(f"\n{'='*100}")
    print(f"店铺 #{store_num}: {row['merchant_name']}")
    print(f"{'='*100}")
    print(f"域名: {row['domain']}")
    print(f"月访问量: {row['estimated_monthly_visits']:,.0f}")
    print(f"年销售额: {row['estimated_yearly_sales']}")
    print(f"\n🔍 Google Ads 透明度链接:")
    print(f"   {row['google_ads_url']}")

    results.append({
        'store_number': store_num,
        'domain': row['domain'],
        'merchant_name': row['merchant_name'],
        'monthly_visits': row['estimated_monthly_visits'],
        'google_ads_url': row['google_ads_url'],
        'has_google_ads': '待检查'  # To be filled manually
    })

# Save to CSV for easy checking
results_df = pd.DataFrame(results)
results_df.to_csv('google_ads_check_list.csv', index=False)

print(f"\n\n{'='*100}")
print("汇总")
print(f"{'='*100}")
print(f"\n总共 {len(results)} 家店铺需要检查")
print(f"\n检查清单已保存到: google_ads_check_list.csv")
print("\n建议检查步骤：")
print("1. 逐个访问上述链接")
print("2. 如果看到广告列表（~200个广告），说明该店铺在投放Google广告")
print("3. 如果页面显示'此网域包含多个广告客户账号'或看到广告数量，说明在投放")
print("4. 如果页面显示'没有找到广告'，说明未投放")
print("\n示例：")
print("- naturnest.com: ~200个广告 ✅ (正在投放)")
print("- 其他域名待检查...")

# Generate a quick check script
print("\n\n💡 提示：如果您想自动化检查，我可以：")
print("1. 使用浏览器自动化工具访问每个链接")
print("2. 截图保存每个页面")
print("3. 检测页面上是否有广告数据")
