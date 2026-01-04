#!/usr/bin/env python3
"""
SerpApi-based Google Ads Transparency Center Checker
使用 SerpApi 高速查询 Google 广告透明中心数据
速度更快、更稳定、无需浏览器
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Optional
import psycopg2

# Database config
DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

# SerpApi config - IMPORTANT: You need to sign up at https://serpapi.com/
# Free tier: 100 searches/month
SERPAPI_KEY = "YOUR_SERPAPI_KEY_HERE"  # Replace with your actual key
SERPAPI_ENDPOINT = "https://serpapi.com/search"


class SerpApiAdsChecker:
    """Google Ads checker using SerpApi"""

    def __init__(self, api_key: str = SERPAPI_KEY):
        self.api_key = api_key
        self.results_cache = {}

    def check_domain_ads(self, domain: str) -> Optional[Dict]:
        """
        Check Google Ads for a domain using SerpApi

        Returns:
            {
                'domain': str,
                'has_ads': bool,
                'ad_count': int,
                'ads': List[dict],  # List of ad creatives
                'first_shown': str,  # Earliest ad date
                'last_shown': str,   # Most recent ad date
                'error': str or None
            }
        """
        # Remove www. prefix
        check_domain = domain.replace('www.', '') if domain.startswith('www.') else domain

        # Check cache
        if check_domain in self.results_cache:
            return self.results_cache[check_domain]

        try:
            # SerpApi parameters
            params = {
                'engine': 'google_ads_transparency_center',
                'text': check_domain,
                'api_key': self.api_key,
                'num': 100  # Get up to 100 results
            }

            # Make API request
            response = requests.get(SERPAPI_ENDPOINT, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Parse response
            ad_creatives = data.get('ad_creatives', [])
            total_results = data.get('search_information', {}).get('total_results', 0)

            # Determine if has ads
            has_ads = len(ad_creatives) > 0 or total_results > 0

            # Extract date range if ads exist
            first_shown = None
            last_shown = None

            if ad_creatives:
                # Get earliest and latest dates
                dates = []
                for ad in ad_creatives:
                    if 'first_shown' in ad:
                        dates.append(ad['first_shown'])
                    if 'last_shown' in ad:
                        dates.append(ad['last_shown'])

                if dates:
                    first_shown = min(dates)
                    last_shown = max(dates)

            result = {
                'domain': domain,
                'has_ads': has_ads,
                'ad_count': total_results,
                'ads': ad_creatives,
                'first_shown': first_shown,
                'last_shown': last_shown,
                'google_ads_url': f"https://adstransparency.google.com/?region=anywhere&domain={check_domain}",
                'error': None,
                'checked_at': datetime.now().isoformat()
            }

            # Cache result
            self.results_cache[check_domain] = result

            return result

        except requests.exceptions.RequestException as e:
            return {
                'domain': domain,
                'has_ads': False,
                'ad_count': 0,
                'ads': [],
                'first_shown': None,
                'last_shown': None,
                'google_ads_url': None,
                'error': f"Request error: {str(e)}",
                'checked_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'domain': domain,
                'has_ads': False,
                'ad_count': 0,
                'ads': [],
                'first_shown': None,
                'last_shown': None,
                'google_ads_url': None,
                'error': f"Error: {str(e)}",
                'checked_at': datetime.now().isoformat()
            }

    def batch_check_domains(self, domains: List[str], progress_callback=None) -> List[Dict]:
        """
        Batch check multiple domains

        Args:
            domains: List of domain names
            progress_callback: Optional callback function(current, total)

        Returns:
            List of results
        """
        results = []
        total = len(domains)

        print(f"\n🚀 SerpApi 批量检查开始")
        print(f"📊 总数: {total} 个域名")
        print(f"⚡ 模式: API 并发请求（无需浏览器）\n")

        for i, domain in enumerate(domains, 1):
            print(f"[{i}/{total}] 检查 {domain}...", end=' ')

            result = self.check_domain_ads(domain)
            results.append(result)

            if result['error']:
                print(f"❌ {result['error']}")
            else:
                status = '✅' if result['has_ads'] else '⭕'
                print(f"{status} {result['ad_count']} 个广告")

            if progress_callback:
                progress_callback(i, total)

            # Rate limiting - SerpApi has rate limits
            # Free tier: ~1 request per second
            time.sleep(1)

        return results

    def update_database(self, domain: str, result: Dict) -> bool:
        """Update store in database with result"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()

            # Determine customer type
            if not result['has_ads']:
                customer_type = 'never_advertised'
            else:
                # If has last_shown date, check if it's within 30 days
                if result['last_shown']:
                    last_shown_timestamp = result['last_shown']
                    # Check if within 30 days (30 * 24 * 60 * 60 = 2592000 seconds)
                    now_timestamp = int(time.time())
                    if now_timestamp - last_shown_timestamp <= 2592000:
                        customer_type = 'new_advertiser_30d'
                    else:
                        customer_type = 'old_advertiser'
                else:
                    customer_type = 'has_ads'  # Unknown date, needs verification

            # Convert timestamps to datetime strings if available
            ads_last_seen_date = None
            if result['last_shown']:
                ads_last_seen_date = datetime.fromtimestamp(result['last_shown']).strftime('%Y-%m-%d')

            # Update database
            cur.execute("""
                UPDATE stores
                SET customer_type = %s,
                    ads_check_level = 'serpapi',
                    ads_last_checked = NOW(),
                    has_google_ads = %s,
                    google_ads_count = %s,
                    google_ads_url = %s,
                    ads_last_seen_date = %s
                WHERE domain = %s
            """, (
                customer_type,
                result['has_ads'],
                result['ad_count'],
                result['google_ads_url'],
                ads_last_seen_date,
                domain
            ))

            conn.commit()
            cur.close()
            conn.close()

            return True

        except Exception as e:
            print(f"❌ 数据库更新失败 {domain}: {e}")
            return False


def main():
    """Test the SerpApi checker"""
    print("="*100)
    print("🚀 SerpApi Google Ads Transparency Center Checker")
    print("="*100)
    print()

    # Test domains
    test_domains = [
        'katebackdrop.com',
        'qudahalloween.com',
        'aelfriceden.com',
        'keychron.com',
        'nothing.tech'
    ]

    # Check API key
    if SERPAPI_KEY == "YOUR_SERPAPI_KEY_HERE":
        print("⚠️  警告: 请先设置 SERPAPI_KEY")
        print("📝 步骤:")
        print("   1. 访问 https://serpapi.com/")
        print("   2. 注册免费账号（100次/月免费）")
        print("   3. 获取 API Key")
        print("   4. 在脚本中替换 SERPAPI_KEY 变量")
        print()
        return

    # Initialize checker
    checker = SerpApiAdsChecker(api_key=SERPAPI_KEY)

    # Record start time
    start_time = time.time()

    # Batch check
    results = checker.batch_check_domains(test_domains)

    # Calculate elapsed time
    elapsed = time.time() - start_time

    print(f"\n{'='*100}")
    print(f"⏱️  完成！总耗时: {elapsed:.2f}秒")
    print(f"📈 平均速度: {elapsed/len(test_domains):.2f}秒/域名")
    print(f"{'='*100}")

    # Show results
    print("\n📊 详细结果:")
    print("-"*100)
    for r in results:
        print(f"\n🌐 {r['domain']}")
        print(f"   状态: {'✅ 有广告' if r['has_ads'] else '⭕ 无广告'}")
        print(f"   广告数: {r['ad_count']}")
        if r['first_shown']:
            print(f"   首次展示: {datetime.fromtimestamp(r['first_shown']).strftime('%Y-%m-%d')}")
        if r['last_shown']:
            print(f"   最后展示: {datetime.fromtimestamp(r['last_shown']).strftime('%Y-%m-%d')}")
        if r['error']:
            print(f"   错误: {r['error']}")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'serpapi_results_{timestamp}.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 结果已保存到: {output_file}")


if __name__ == '__main__':
    main()
