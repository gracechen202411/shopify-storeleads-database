import pandas as pd
import re

# Read CSV file
print("Loading CSV data...")
df = pd.read_csv('shopify-storeleads.csv', low_memory=False)

print(f"Total records: {len(df)}")

# Filter conditions
print("\nApplying filters...")

# 1. Country: CN (China)
df_filtered = df[df['country_code'] == 'CN'].copy()
print(f"After CN filter: {len(df_filtered)}")

# 2. City: Hangzhou (杭州)
df_filtered = df_filtered[
    df_filtered['city'].str.contains('Hangzhou', case=False, na=False) |
    df_filtered['company_location'].str.contains('Hangzhou', case=False, na=False)
]
print(f"After Hangzhou filter: {len(df_filtered)}")

# 3. Monthly visits: 20,000 - 200,000
df_filtered['estimated_monthly_visits'] = pd.to_numeric(df_filtered['estimated_monthly_visits'], errors='coerce')
df_filtered = df_filtered[
    (df_filtered['estimated_monthly_visits'] >= 20000) &
    (df_filtered['estimated_monthly_visits'] <= 200000)
]
print(f"After monthly visits filter (20k-200k): {len(df_filtered)}")

# 4. Domain ends with .com
df_filtered = df_filtered[df_filtered['domain'].str.endswith('.com', na=False)]
print(f"After .com domain filter: {len(df_filtered)}")

# 5. Filter out weird/too long domains
def is_normal_domain(domain):
    if pd.isna(domain):
        return False
    # Remove www. prefix
    domain_clean = domain.replace('www.', '')
    # Check length (without .com)
    domain_name = domain_clean.replace('.com', '')
    if len(domain_name) > 30:  # Too long
        return False
    if len(domain_name) < 3:  # Too short
        return False
    # Check if contains too many hyphens or numbers
    if domain_name.count('-') > 2:
        return False
    # Check if mostly numbers
    digit_count = sum(c.isdigit() for c in domain_name)
    if digit_count > len(domain_name) * 0.5:
        return False
    return True

df_filtered = df_filtered[df_filtered['domain'].apply(is_normal_domain)]
print(f"After domain quality filter: {len(df_filtered)}")

# Sort by monthly visits descending
df_filtered = df_filtered.sort_values('estimated_monthly_visits', ascending=False)

print(f"\n=== RESULTS ===")
print(f"Total filtered stores: {len(df_filtered)}")

# Save results
print("\nSaving results...")
df_filtered.to_csv('hangzhou_stores_20k_200k.csv', index=False)

# Detailed output
print(f"\n{'='*100}")
print(f"符合条件的{len(df_filtered)}家杭州商店（月访问量20k-200k）")
print(f"{'='*100}\n")

for idx, row in df_filtered.iterrows():
    print(f"{'='*100}")
    print(f"店铺 #{df_filtered.index.get_loc(idx)+1}")
    print(f"{'='*100}")
    print(f"域名: {row['domain']}")
    print(f"商家名称: {row['merchant_name']}")
    print(f"标题: {row['title']}")
    print(f"类目: {row['categories']}")
    print(f"位置: {row['company_location']}")
    print(f"月访问量: {row['estimated_monthly_visits']:,.0f}")
    print(f"年销售额: {row['estimated_yearly_sales']}")
    print(f"员工数: {row['employee_count']}")
    print(f"套餐: {row['plan']}")
    print(f"排名: {row['rank']}")
    print(f"创建时间: {row['created']}")
    print(f"\nMeta描述:")
    desc = str(row['meta_description'])
    if len(desc) > 200:
        print(f"  {desc[:200]}...")
    else:
        print(f"  {desc}")
    print(f"\n联系方式:")
    print(f"  邮箱: {row['emails']}")
    print(f"  电话: {row['phones']}")
    print(f"  联系页面: {row['contact_page_url']}")
    print(f"\n社交媒体:")
    socials = []
    if pd.notna(row['instagram']): socials.append(f"Instagram: @{row['instagram']}")
    if pd.notna(row['facebook']): socials.append(f"Facebook: {row['facebook']}")
    if pd.notna(row['tiktok']): socials.append(f"TikTok: @{row['tiktok']}")
    if pd.notna(row['youtube']): socials.append(f"YouTube: {row['youtube']}")
    if pd.notna(row['twitter']): socials.append(f"Twitter: @{row['twitter']}")
    if socials:
        for s in socials:
            print(f"  {s}")
    else:
        print("  无")
    print()

# Statistics
print(f"\n{'='*100}")
print("统计分析")
print(f"{'='*100}")

print(f"\n月访问量统计:")
print(f"  平均值: {df_filtered['estimated_monthly_visits'].mean():,.0f}")
print(f"  中位数: {df_filtered['estimated_monthly_visits'].median():,.0f}")
print(f"  最大值: {df_filtered['estimated_monthly_visits'].max():,.0f}")
print(f"  最小值: {df_filtered['estimated_monthly_visits'].min():,.0f}")

print(f"\n类目分布:")
categories = df_filtered['categories'].value_counts()
for cat, count in categories.head(10).items():
    print(f"  {cat}: {count}")

print(f"\n套餐分布:")
plans = df_filtered['plan'].value_counts()
for plan, count in plans.items():
    print(f"  {plan}: {count}")

print(f"\n社交媒体覆盖率:")
print(f"  有Instagram: {df_filtered['instagram'].notna().sum()} ({df_filtered['instagram'].notna().sum()/len(df_filtered)*100:.1f}%)")
print(f"  有Facebook: {df_filtered['facebook'].notna().sum()} ({df_filtered['facebook'].notna().sum()/len(df_filtered)*100:.1f}%)")
print(f"  有TikTok: {df_filtered['tiktok'].notna().sum()} ({df_filtered['tiktok'].notna().sum()/len(df_filtered)*100:.1f}%)")
print(f"  有YouTube: {df_filtered['youtube'].notna().sum()} ({df_filtered['youtube'].notna().sum()/len(df_filtered)*100:.1f}%)")
print(f"  有Twitter: {df_filtered['twitter'].notna().sum()} ({df_filtered['twitter'].notna().sum()/len(df_filtered)*100:.1f}%)")

print(f"\n创建年份分布:")
df_filtered['year'] = pd.to_datetime(df_filtered['created']).dt.year
years = df_filtered['year'].value_counts().sort_index()
for year, count in years.items():
    print(f"  {int(year)}: {count}")

print("\n✅ Analysis complete!")
print(f"\nOutput file: hangzhou_stores_20k_200k.csv")
