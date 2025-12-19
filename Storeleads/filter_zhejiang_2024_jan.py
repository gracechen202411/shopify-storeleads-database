#!/usr/bin/env python3
"""
筛选2024年1月创建的浙江商店
月访问量 >= 1000
"""

import pandas as pd
from datetime import datetime

print("="*100)
print("筛选 2024年全年 + 浙江 + 月访问量>=1000 的商店")
print("="*100)

# 读取CSV
print("\n正在读取数据...")
df = pd.read_csv('shopify-storeleads.csv', low_memory=False)
print(f"总记录数: {len(df):,}")

# 筛选条件
print("\n应用筛选条件...")

# 1. 创建时间：2024年全年
print("  1. 筛选创建时间: 2024年全年")
df_filtered = df[df['created'].str.startswith('2024/', na=False)].copy()
print(f"     → 剩余: {len(df_filtered):,} 条")

# 2. 位置包含 Zhejiang（不区分大小写）
print("  2. 筛选位置: 包含 Zhejiang")
df_filtered = df_filtered[
    df_filtered['company_location'].str.contains('Zhejiang', case=False, na=False)
]
print(f"     → 剩余: {len(df_filtered):,} 条")

# 3. 月访问量 >= 1000
print("  3. 筛选月访问量: >= 1000")
df_filtered['estimated_monthly_visits'] = pd.to_numeric(
    df_filtered['estimated_monthly_visits'],
    errors='coerce'
)
df_filtered = df_filtered[df_filtered['estimated_monthly_visits'] >= 1000]
print(f"     → 剩余: {len(df_filtered):,} 条")

# 排序：按月访问量降序
df_filtered = df_filtered.sort_values('estimated_monthly_visits', ascending=False)

print(f"\n{'='*100}")
print(f"✅ 筛选完成！共找到 {len(df_filtered)} 家店铺")
print(f"{'='*100}")

# 保存结果
output_file = 'zhejiang_2024_1000plus.csv'
df_filtered.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n✅ 已保存到: {output_file}")

# 显示前20条预览
if len(df_filtered) > 0:
    print(f"\n{'='*100}")
    print("前20家店铺预览（按访问量排序）:")
    print(f"{'='*100}\n")

    preview_cols = ['domain', 'merchant_name', 'company_location', 'created',
                   'estimated_monthly_visits', 'estimated_yearly_sales']

    for idx, row in df_filtered.head(20).iterrows():
        print(f"{df_filtered.index.get_loc(idx)+1}. {row['merchant_name']}")
        print(f"   域名: {row['domain']}")
        print(f"   位置: {row['company_location']}")
        print(f"   创建: {row['created']}")
        print(f"   月访问量: {row['estimated_monthly_visits']:,.0f}")
        print(f"   年销售额: {row['estimated_yearly_sales']}")
        print()

    # 统计
    print(f"{'='*100}")
    print("统计信息:")
    print(f"{'='*100}")
    print(f"总店铺数: {len(df_filtered)}")
    print(f"平均月访问量: {df_filtered['estimated_monthly_visits'].mean():,.0f}")
    print(f"中位数月访问量: {df_filtered['estimated_monthly_visits'].median():,.0f}")
    print(f"最高月访问量: {df_filtered['estimated_monthly_visits'].max():,.0f}")
    print(f"最低月访问量: {df_filtered['estimated_monthly_visits'].min():,.0f}")

    # 城市分布
    print(f"\n浙江城市分布 (Top 10):")
    print("-"*50)
    # 提取城市名
    df_filtered['city_extracted'] = df_filtered['company_location'].str.extract(r'([^,]+),\s*Zhejiang')[0]
    city_counts = df_filtered['city_extracted'].value_counts().head(10)
    for city, count in city_counts.items():
        print(f"  {city}: {count} 家")

else:
    print("\n⚠️ 未找到符合条件的店铺")

print(f"\n{'='*100}")
print("下一步: 使用批量查询工具检查Google广告")
print("运行: python3 batch_ads_check_with_zhejiang.py")
print(f"{'='*100}")
