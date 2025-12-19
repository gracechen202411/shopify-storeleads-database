# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Shopify Store Analysis Project** that analyzes 2.39 million Shopify store records from a comprehensive database. The project focuses on identifying and analyzing specific types of stores based on location, traffic, sales, and business models (particularly POD/custom stores).

**Data Source**: `shopify-storeleads.csv` (2.39M records)

## Core Analysis Scripts

### 1. Store Filtering & Segmentation

#### `analyze_hangzhou_custom.py`
Analyzes Hangzhou stores with 20k-100k monthly visits to identify custom/personalization stores.

**Filters Applied**:
- Country: China (CN)
- City: Hangzhou (杭州)
- Monthly visits: 20,000 - 100,000
- Domain: ends with `.com`
- Domain quality checks (length, hyphens, numbers ratio)
- Keyword search: "custom" in domain/title/meta_description

**Run**: `python3 analyze_hangzhou_custom.py`

**Outputs**:
- `hangzhou_filtered_stores.csv` - All filtered stores
- `hangzhou_custom_stores.csv` - Custom-focused stores
- `hangzhou_non_custom_stores.csv` - Non-custom stores

#### `filter_zhejiang_2024_jan.py`
Filters Zhejiang province stores created in January 2024 with 1000+ monthly visits.

**Run**: `python3 filter_zhejiang_2024_jan.py`

**Output**: `zhejiang_2024_jan_1000plus.csv`

#### `analyze_hangzhou_200k.py`
Analyzes stores with 20k-200k monthly visits (broader range).

**Run**: `python3 analyze_hangzhou_200k.py`

**Output**: `hangzhou_stores_20k_200k.csv`

### 2. POD (Print on Demand) Store Identification

#### `identify_pod_stores.py`
Identifies Print-on-Demand stores using keyword scoring system.

**POD Scoring Algorithm**:
- Core keywords (10 points each): `personalized`, `custom`, `customize`, `print on demand`, etc.
- Product keywords (3 points each): `t-shirt`, `mug`, `canvas`, `hoodie`, etc.
- Feature keywords (2 points each): `unique`, `gift for`, `your name`, etc.

**Usage Examples**:
```python
# Identify all high-traffic POD stores
identify_pod_stores('shopify-storeleads.csv', min_score=15, min_visits=1000)

# Identify Zhejiang POD stores
identify_pod_stores('shopify-storeleads.csv', min_score=10, min_visits=500, location_filter='Zhejiang')

# Identify China POD stores
identify_pod_stores('shopify-storeleads.csv', min_score=12, min_visits=1000, location_filter='China')
```

**Outputs**:
- `pod_stores_identified.csv`
- `zhejiang_pod_stores.csv`
- `china_pod_stores.csv`
- `hongkong_pod_stores.csv`

### 3. Google Ads Detection System

#### Core Tool: `batch_ads_checker_optimized.py`
Optimized batch Google Ads checker with 30-day caching mechanism.

**Features**:
- ✅ Caches Google Ads data for 30 days
- ✅ 99%+ speed improvement on cached queries
- ✅ Incremental updates (only checks uncached domains)
- ✅ Generates query lists for manual verification
- ✅ Auto-saves results to CSV

**Architecture**:
```python
class AdsCache:
    def __init__(self, cache_file='ads_cache.json')
    def get(self, domain) -> dict
    def set(self, domain, has_ads, ad_count, ad_count_text)
    def is_fresh(self, domain, max_age_days=30) -> bool
```

**Run**: `python3 batch_ads_checker_optimized.py`

**Workflow**:
1. Loads domains from CSV
2. Checks cache for existing data
3. Generates `domains_to_check.json` for uncached domains
4. Outputs cached results to `ads_check_results_cached.csv`

**Manual Cache Update**:
```python
from batch_ads_checker_optimized import AdsCache
cache = AdsCache()
cache.set('domain.com', True, 200, '~200 个广告')   # Has ads
cache.set('domain.com', False, 0, '0 个广告')       # No ads
```

#### Supporting Tools

- **`populate_cache.py`**: Quickly populate cache with known results
- **`quick_add_results.py`**: Batch add Google Ads results to cache
- **`batch_ads_check_zhejiang.py`**: Check Google Ads for Zhejiang stores
- **`fast_google_ads_checker.py`**: Fast checker (legacy)
- **`fast_mcp_ads_checker.py`**: MCP Playwright integration (legacy)
- **`check_google_ads.py`**: Original checker (slow, not recommended)
- **`batch_google_ads_scraper.py`**: Batch scraper (legacy)

**Deprecated Tools** (use `batch_ads_checker_optimized.py` instead):
- `check_google_ads.py`
- `fast_google_ads_checker.py`
- `fast_mcp_ads_checker.py`
- `batch_google_ads_scraper.py`

### 4. Google Ads Manual Verification Workflow

**Recommended Process** (uses MCP Playwright):

1. Run the optimizer to generate query list:
   ```bash
   python3 batch_ads_checker_optimized.py
   ```

2. Open `domains_to_check.json` to see uncached domains

3. Use Claude Code MCP Playwright to visit:
   ```
   https://adstransparency.google.com/?region=anywhere&domain={domain}
   ```

4. Check ad count on page, then add to cache:
   ```python
   from batch_ads_checker_optimized import AdsCache
   cache = AdsCache()
   cache.set('example.com', True, 200, '~200 个广告')
   ```

5. Rerun optimizer to see updated progress:
   ```bash
   python3 batch_ads_checker_optimized.py
   ```

**Performance**:
- First query: ~2-3 minutes for 11 domains
- Cached query: **< 1 second** for 11 domains
- 100 domains: ~20 minutes first time, < 1 second after caching

## Data Files

### Input Data
- **`shopify-storeleads.csv`** - Main dataset (2.39M records)

### Output Data

**Store Lists**:
- `hangzhou_filtered_stores.csv`
- `hangzhou_custom_stores.csv`
- `hangzhou_non_custom_stores.csv`
- `hangzhou_stores_20k_200k.csv`
- `zhejiang_2024_jan_1000plus.csv`
- `zhejiang_2024_1000plus.csv`
- `pod_stores_identified.csv`
- `zhejiang_pod_stores.csv`
- `china_pod_stores.csv`
- `hongkong_pod_stores.csv`

**Google Ads Data**:
- `ads_cache.json` - Cached Google Ads data (30-day TTL)
- `domains_to_check.json` - Pending domains for manual check
- `google_ads_check_list.csv` - Query checklist
- `google_ads_summary.csv` - Summary report
- `ads_check_results_cached.csv` - Results with cache
- `zhejiang_2024_with_google_ads.csv` - Zhejiang 2024 stores with ads status
- `google_ads_batch_results.json` - Batch query results (legacy)
- `zhejiang_domains_to_check.json` - Zhejiang domain list

**Reports**:
- `google_ads_analysis_report.md`
- `evridwearcustom_analysis.md`
- `google_ads_scraper_evaluation.md`
- `speed_optimization_guide.md` - Optimization guide
- `zhejiang_2024_summary.md` - 17 Zhejiang 2024 stores analysis

## Key Data Filters

### Common Filter Patterns

**Geographic Filters**:
```python
df[df['country_code'] == 'CN']  # China
df[df['city'].str.contains('Hangzhou|杭州', case=False, na=False)]  # Hangzhou
df[df['company_location'].str.contains('Zhejiang', case=False, na=False)]  # Zhejiang
```

**Traffic Filters**:
```python
df[(df['estimated_monthly_visits'] >= 20000) & (df['estimated_monthly_visits'] <= 100000)]
df[df['estimated_monthly_visits'] >= 1000]
```

**Time Filters**:
```python
df[df['created'].str.contains('2024', na=False)]  # Created in 2024
df[df['created'].str.contains('2024/01', na=False)]  # January 2024
```

**Domain Quality Checks**:
- Length: 3-30 characters (excluding .com)
- Hyphens: ≤ 2
- Number ratio: ≤ 50%
- Must end with `.com`

## CSV Data Schema

**Key Columns**:
- `domain` - Store domain
- `merchant_name` - Business name
- `company_location` - Full location string
- `country_code` - 2-letter country code
- `city` - City name
- `created` - Store creation date (YYYY/MM/DD)
- `estimated_monthly_visits` - Monthly visitor count
- `estimated_yearly_sales` - Annual sales (USD string)
- `employee_count` - Team size
- `plan` - Shopify plan tier
- `categories` - Product categories
- `title` - Store title
- `description` - Full description
- `meta_description` - SEO description
- `emails` - Contact emails
- `phones` - Phone numbers
- `instagram`, `facebook`, `tiktok`, `youtube` - Social media

## Development Commands

### Running Analysis Scripts
```bash
# Analyze Hangzhou custom stores (20k-100k visits)
python3 analyze_hangzhou_custom.py

# Analyze Hangzhou stores (20k-200k visits)
python3 analyze_hangzhou_200k.py

# Filter Zhejiang 2024 stores
python3 filter_zhejiang_2024_jan.py

# Identify POD stores
python3 identify_pod_stores.py

# Check Google Ads (optimized)
python3 batch_ads_checker_optimized.py

# Check Google Ads for Zhejiang stores
python3 batch_ads_check_zhejiang.py

# Populate cache with known results
python3 populate_cache.py

# Quick add batch results to cache
python3 quick_add_results.py
```

### Cache Management
```python
# Load cache
from batch_ads_checker_optimized import AdsCache
cache = AdsCache()

# Add single domain
cache.set('example.com', True, 200, '~200 个广告')

# Check cache status
cached_data = cache.get('example.com')
is_fresh = cache.is_fresh('example.com', max_age_days=30)

# Get all cached data
all_cache = cache.get_all()
```

## Important Notes

### Performance Optimization
- **ALWAYS use `batch_ads_checker_optimized.py`** for Google Ads checks (not the legacy tools)
- **Cache system provides 99%+ speed improvement** on repeated queries
- **Batch processing**: Process 10 domains at a time, save to cache, then continue
- **Incremental updates**: Only new domains are queried, cached results are instant

### Data Filtering Best Practices
- **Always check data types** before numeric filters (use `pd.to_numeric(..., errors='coerce')`)
- **Use `.str.contains()` with `na=False`** to avoid NaN errors
- **Clean domains** by removing `www.` prefix before comparisons
- **Validate domain quality** to avoid garbage data

### Google Ads Verification
- **Manual verification recommended** for accuracy (use MCP Playwright)
- **Cache results immediately** to avoid re-querying
- **Google Ads Transparency URL format**: `https://adstransparency.google.com/?region=anywhere&domain={domain}`
- **Ad count formats**: `~200 个广告`, `42 个广告`, `0 个广告`

### POD Store Detection
- **Minimum score of 15** recommended for high confidence
- **Core keywords** (personalized, custom) are strongest signals
- **Multiple field analysis** improves accuracy (check domain, title, description)
- **Combine with traffic filters** to find successful POD stores

## Architecture Insights

### Caching System Design
The Google Ads caching system is the key performance optimization:

```
┌─────────────────────┐
│  CSV Store Data     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Check Cache        │ ◄─── ads_cache.json (30-day TTL)
│  (ads_cache.json)   │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
   Cached     Uncached
     │           │
     │           ▼
     │     ┌─────────────────────┐
     │     │ Generate Query List │
     │     │ (domains_to_check)  │
     │     └─────────┬───────────┘
     │               │
     │               ▼
     │     ┌─────────────────────┐
     │     │ Manual Verification │
     │     │  (MCP Playwright)   │
     │     └─────────┬───────────┘
     │               │
     │               ▼
     │     ┌─────────────────────┐
     │     │  Update Cache       │
     │     └─────────┬───────────┘
     │               │
     └───────────────┘
                     │
                     ▼
           ┌─────────────────────┐
           │  Generate Report    │
           │  (CSV + Stats)      │
           └─────────────────────┘
```

### POD Scoring Algorithm
```
Total Score = (Core Keywords × 10) + (Product Keywords × 3) + (Feature Keywords × 2)

Core Keywords: personalized, custom, customize, print on demand, etc.
Product Keywords: t-shirt, mug, canvas, hoodie, poster, etc.
Feature Keywords: unique, gift for, your name, etc.

Thresholds:
- 15+ points: High confidence POD store
- 10-14 points: Medium confidence
- < 10 points: Low confidence
```

## Project Context

This project analyzes Shopify stores from a database of 2.39 million records to identify:
1. **High-traffic stores** in specific regions (Hangzhou, Zhejiang, China)
2. **POD/Custom stores** using keyword analysis
3. **Google Ads users** to understand marketing strategies
4. **New stores** (2024) to identify emerging businesses

**Common Analysis Goals**:
- Find successful custom/POD stores for market research
- Identify advertising strategies of competitors
- Discover high-potential stores in specific regions
- Analyze traffic and sales correlations

**Current Status**:
- ✅ 11 Hangzhou domains cached with Google Ads data
- ✅ 17 Zhejiang 2024 stores identified (1 ads checked, 16 pending)
- ✅ POD identification system fully functional
- ✅ Caching system achieving 99%+ speed improvement
