#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POD (Print on Demand) Store Identifier
识别按需打印类型的Shopify店铺
"""

import pandas as pd
import re

# POD关键词库
POD_KEYWORDS = {
    # 核心POD关键词
    'core': [
        'personalized', 'personalize', 'custom', 'customize', 'customized',
        'print on demand', 'pod', 'print-on-demand',
        'design your own', 'create your own', 'make your own',
        'bespoke', 'tailor', 'tailored', 'made to order',
    ],

    # POD产品类型
    'products': [
        't-shirt', 'tshirt', 'mug', 'mugs', 'canvas', 'poster', 'posters',
        'hoodie', 'hoodies', 'sweatshirt', 'doormat', 'doormats',
        'ornament', 'ornaments', 'pillow', 'cushion', 'blanket', 'blankets',
        'phone case', 'tote bag', 'garden flag', 'metal sign', 'yard sign',
        'throw pillow', 'wall art', 'print', 'prints', 'tumbler', 'tumblers',
        'apparel', 'clothing', 'gift', 'gifts', 'home decor',
    ],

    # POD特征词
    'features': [
        'unique', 'one of a kind', 'special gift', 'gift for',
        'imagination', 'your story', 'your name', 'with name',
        'photo', 'picture', 'upload', 'design', 'choose',
        'wide range', 'variety', 'collection',
    ],
}

def calculate_pod_score(text):
    """计算POD得分"""
    if pd.isna(text):
        return 0

    text_lower = str(text).lower()
    score = 0

    # 核心关键词权重最高
    for keyword in POD_KEYWORDS['core']:
        if keyword in text_lower:
            score += 10

    # 产品类型关键词
    for keyword in POD_KEYWORDS['products']:
        if keyword in text_lower:
            score += 3

    # 特征词
    for keyword in POD_KEYWORDS['features']:
        if keyword in text_lower:
            score += 2

    return score

def identify_pod_stores(csv_file, min_score=15, min_visits=1000, location_filter=None):
    """
    识别POD店铺

    参数:
        csv_file: CSV文件路径
        min_score: 最低POD得分（默认15分）
        min_visits: 最低月访问量（默认1000）
        location_filter: 位置筛选（如 'Zhejiang', 'China' 等）
    """
    print("=" * 100)
    print("POD店铺识别系统")
    print("=" * 100)

    # 读取数据
    print("\n📂 正在读取数据...")
    df = pd.read_csv(csv_file, low_memory=False)
    print(f"✅ 共读取 {len(df):,} 条记录")

    # 计算POD得分
    print("\n🔍 正在分析POD特征...")
    df['pod_score'] = 0

    # 对多个字段进行评分
    text_fields = ['description', 'meta_description', 'title', 'merchant_name', 'domain']
    for field in text_fields:
        if field in df.columns:
            df['pod_score'] += df[field].apply(calculate_pod_score)

    # 筛选条件
    print("\n📊 应用筛选条件...")
    filters = []

    # POD得分筛选
    pod_candidates = df[df['pod_score'] >= min_score].copy()
    filters.append(f"POD得分 >= {min_score}")

    # 月访问量筛选
    if min_visits:
        pod_candidates['estimated_monthly_visits'] = pd.to_numeric(
            pod_candidates['estimated_monthly_visits'], errors='coerce'
        )
        pod_candidates = pod_candidates[pod_candidates['estimated_monthly_visits'] >= min_visits]
        filters.append(f"月访问量 >= {min_visits:,}")

    # 位置筛选
    if location_filter:
        pod_candidates = pod_candidates[
            pod_candidates['company_location'].str.contains(location_filter, case=False, na=False)
        ]
        filters.append(f"位置包含 '{location_filter}'")

    print(f"筛选条件: {' + '.join(filters)}")
    print(f"✅ 找到 {len(pod_candidates)} 家POD候选店铺")

    # 按POD得分和月访问量排序
    pod_candidates = pod_candidates.sort_values(
        ['pod_score', 'estimated_monthly_visits'],
        ascending=[False, False]
    )

    # 显示结果
    print("\n" + "=" * 100)
    print("POD店铺列表 (按POD得分排序)")
    print("=" * 100)

    for idx, (_, row) in enumerate(pod_candidates.head(50).iterrows(), 1):
        print(f"\n【{idx}】{row['merchant_name']} ({row['domain']})")
        print(f"    POD得分: {int(row['pod_score'])} 分")
        print(f"    月访问: {int(row['estimated_monthly_visits']) if pd.notna(row['estimated_monthly_visits']) else 'N/A':,}")
        print(f"    年销售: {row['estimated_yearly_sales']}")
        print(f"    位置: {row['company_location']}")
        print(f"    创建: {row['created']}")
        if pd.notna(row['description']):
            desc = str(row['description'])[:150]
            print(f"    描述: {desc}...")
        print("-" * 100)

    # 保存结果
    output_file = 'pod_stores_identified.csv'
    columns_to_save = [
        'domain', 'merchant_name', 'company_location', 'created',
        'estimated_monthly_visits', 'estimated_yearly_sales',
        'pod_score', 'description', 'categories', 'emails',
        'facebook', 'instagram', 'tiktok'
    ]

    available_columns = [col for col in columns_to_save if col in pod_candidates.columns]
    pod_candidates[available_columns].to_csv(output_file, index=False, encoding='utf-8-sig')

    print("\n" + "=" * 100)
    print(f"✅ 结果已保存到: {output_file}")
    print("=" * 100)

    # 统计信息
    print("\n📊 统计信息:")
    print(f"  总POD店铺: {len(pod_candidates)}")
    if len(pod_candidates) > 0:
        print(f"  平均POD得分: {pod_candidates['pod_score'].mean():.1f}")
        print(f"  最高POD得分: {int(pod_candidates['pod_score'].max())}")
        print(f"  平均月访问: {pod_candidates['estimated_monthly_visits'].mean():,.0f}")
        print(f"  总年销售额: ${pod_candidates['estimated_yearly_sales'].str.replace('USD $', '').str.replace(',', '').astype(float).sum():,.2f}")

    return pod_candidates


if __name__ == '__main__':
    # 示例1: 识别所有POD店铺（月访问>1000）
    print("\n" + "🔍 场景1: 识别所有高流量POD店铺".center(100, "="))
    identify_pod_stores('shopify-storeleads.csv', min_score=15, min_visits=1000)

    # 示例2: 识别浙江的POD店铺
    # print("\n" + "🔍 场景2: 识别浙江地区POD店铺".center(100, "="))
    # identify_pod_stores('shopify-storeleads.csv', min_score=10, min_visits=500, location_filter='Zhejiang')

    # 示例3: 识别中国的POD店铺
    # print("\n" + "🔍 场景3: 识别中国地区POD店铺".center(100, "="))
    # identify_pod_stores('shopify-storeleads.csv', min_score=12, min_visits=1000, location_filter='China')
