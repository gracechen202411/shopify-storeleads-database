import pandas as pd
import re
from datetime import datetime

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
    df_filtered['city'].str.contains('Hangzhou|杭州', case=False, na=False) |
    df_filtered['company_location'].str.contains('Hangzhou|杭州', case=False, na=False)
]
print(f"After Hangzhou filter: {len(df_filtered)}")

# 3. Monthly visits: 20,000 - 100,000
df_filtered['estimated_monthly_visits'] = pd.to_numeric(df_filtered['estimated_monthly_visits'], errors='coerce')
df_filtered = df_filtered[
    (df_filtered['estimated_monthly_visits'] >= 20000) &
    (df_filtered['estimated_monthly_visits'] <= 100000)
]
print(f"After monthly visits filter (20k-100k): {len(df_filtered)}")

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

# 6. Find stores with "Custom" in domain, meta_description, or title
df_filtered['has_custom'] = (
    df_filtered['domain'].str.contains('custom', case=False, na=False) |
    df_filtered['meta_description'].str.contains('custom', case=False, na=False) |
    df_filtered['title'].str.contains('custom', case=False, na=False)
)

df_custom = df_filtered[df_filtered['has_custom'] == True].copy()
df_non_custom = df_filtered[df_filtered['has_custom'] == False].copy()

print(f"\n=== RESULTS ===")
print(f"Total filtered stores: {len(df_filtered)}")
print(f"Stores with 'Custom': {len(df_custom)}")
print(f"Stores without 'Custom': {len(df_non_custom)}")

# Save results
print("\nSaving results...")
df_filtered.to_csv('hangzhou_filtered_stores.csv', index=False)
df_custom.to_csv('hangzhou_custom_stores.csv', index=False)
df_non_custom.to_csv('hangzhou_non_custom_stores.csv', index=False)

# Detailed analysis of Custom stores
if len(df_custom) > 0:
    print("\n" + "="*80)
    print("DETAILED ANALYSIS: STORES WITH 'CUSTOM'")
    print("="*80)

    for idx, row in df_custom.iterrows():
        print(f"\n{'='*80}")
        print(f"Domain: {row['domain']}")
        print(f"Merchant Name: {row['merchant_name']}")
        print(f"Title: {row['title']}")
        print(f"Categories: {row['categories']}")
        print(f"Location: {row['company_location']}")
        print(f"Monthly Visits: {row['estimated_monthly_visits']:,.0f}")
        print(f"Yearly Sales: {row['estimated_yearly_sales']}")
        print(f"Employees: {row['employee_count']}")
        print(f"Plan: {row['plan']}")
        print(f"Created: {row['created']}")
        print(f"\nMeta Description:")
        print(f"  {row['meta_description']}")
        print(f"\nContact Info:")
        print(f"  Email: {row['emails']}")
        print(f"  Phone: {row['phones']}")
        print(f"\nSocial Media:")
        print(f"  Instagram: {row['instagram']}")
        print(f"  Facebook: {row['facebook']}")
        print(f"  TikTok: {row['tiktok']}")
        print(f"  YouTube: {row['youtube']}")

        # Highlight where "Custom" appears
        custom_locations = []
        if pd.notna(row['domain']) and 'custom' in row['domain'].lower():
            custom_locations.append("Domain")
        if pd.notna(row['meta_description']) and 'custom' in row['meta_description'].lower():
            custom_locations.append("Meta Description")
        if pd.notna(row['title']) and 'custom' in row['title'].lower():
            custom_locations.append("Title")
        print(f"\n⭐ 'Custom' found in: {', '.join(custom_locations)}")

# Statistics comparison
if len(df_custom) > 0 and len(df_non_custom) > 0:
    print("\n" + "="*80)
    print("COMPARISON: Custom vs Non-Custom Stores")
    print("="*80)

    print("\nAverage Monthly Visits:")
    print(f"  Custom stores: {df_custom['estimated_monthly_visits'].mean():,.0f}")
    print(f"  Non-Custom stores: {df_non_custom['estimated_monthly_visits'].mean():,.0f}")

    # Convert sales to numeric for comparison
    df_custom['sales_numeric'] = pd.to_numeric(
        df_custom['estimated_yearly_sales'].str.replace(r'[^\d.]', '', regex=True),
        errors='coerce'
    )
    df_non_custom['sales_numeric'] = pd.to_numeric(
        df_non_custom['estimated_yearly_sales'].str.replace(r'[^\d.]', '', regex=True),
        errors='coerce'
    )

    print("\nAverage Yearly Sales:")
    print(f"  Custom stores: ${df_custom['sales_numeric'].mean():,.2f}")
    print(f"  Non-Custom stores: ${df_non_custom['sales_numeric'].mean():,.2f}")

    print("\nAverage Employee Count:")
    print(f"  Custom stores: {df_custom['employee_count'].mean():.1f}")
    print(f"  Non-Custom stores: {df_non_custom['employee_count'].mean():.1f}")

    print("\nPlan Distribution:")
    print("  Custom stores:")
    print(df_custom['plan'].value_counts())
    print("\n  Non-Custom stores:")
    print(df_non_custom['plan'].value_counts())

print("\n✅ Analysis complete!")
print(f"\nOutput files:")
print(f"  - hangzhou_filtered_stores.csv (all {len(df_filtered)} stores)")
print(f"  - hangzhou_custom_stores.csv ({len(df_custom)} stores)")
print(f"  - hangzhou_non_custom_stores.csv ({len(df_non_custom)} stores)")
