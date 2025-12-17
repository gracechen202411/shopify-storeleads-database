#!/usr/bin/env python3
"""
店铺分析脚本 - 检测Google Ads, 社交媒体数据, 技术栈等
支持批量分析和增量更新
"""
import os
import sys
import psycopg2
import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime
from urllib.parse import urlparse

# 配置
DATABASE_URL = os.environ.get('DATABASE_URL')
BATCH_SIZE = 50  # 每批处理的店铺数量
DELAY_SECONDS = 2  # 请求间隔，避免被封

if not DATABASE_URL:
    print("ERROR: Please set DATABASE_URL environment variable")
    sys.exit(1)


class StoreAnalyzer:
    """店铺分析器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def analyze_store(self, domain, domain_url):
        """分析单个店铺"""
        result = {
            'has_google_ads': None,
            'technologies': [],
            'has_email_popup': None,
            'has_discount_code': None,
            'has_live_chat': None,
            'mobile_friendly': None,
            'page_load_speed': None,
            'product_count': None,
            'analysis_score': 0,
        }

        try:
            url = domain_url or f"https://{domain}"
            start_time = time.time()

            # 获取网页内容
            response = self.session.get(url, timeout=15)
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            load_time = int((time.time() - start_time) * 1000)
            result['page_load_speed'] = load_time

            # 1. 检测 Google Ads
            result['has_google_ads'] = self.detect_google_ads(html)

            # 2. 检测技术栈
            result['technologies'] = self.detect_technologies(html, soup)

            # 3. 检测营销工具
            result['has_email_popup'] = self.detect_email_popup(html, soup)
            result['has_discount_code'] = self.detect_discount_code(html, soup)
            result['has_live_chat'] = self.detect_live_chat(html, soup)

            # 4. 检测移动端友好
            result['mobile_friendly'] = self.detect_mobile_friendly(soup)

            # 5. 估算产品数量（如果可能）
            result['product_count'] = self.estimate_product_count(soup)

            # 6. 计算综合评分
            result['analysis_score'] = self.calculate_score(result)

        except Exception as e:
            print(f"    Error analyzing: {e}")

        return result

    def detect_google_ads(self, html):
        """检测是否使用 Google Ads"""
        ads_indicators = [
            'googlesyndication.com',
            'adsbygoogle',
            'google_ad_client',
            'googleadservices.com',
            'doubleclick.net'
        ]
        return any(indicator in html for indicator in ads_indicators)

    def detect_technologies(self, html, soup):
        """检测使用的技术和工具"""
        technologies = []

        # Shopify Apps 检测
        app_indicators = {
            'Klaviyo': ['klaviyo', 'klaviyo.com'],
            'Judge.me': ['judgeme', 'judge.me'],
            'Yotpo': ['yotpo', 'staticw2.yotpo.com'],
            'Privy': ['privy', 'privy.com'],
            'Gorgias': ['gorgias', 'gorgias.com'],
            'Smile.io': ['smile.io', 'sweettooth'],
            'Loox': ['loox', 'loox.io'],
            'ReCharge': ['recharge', 'rechargepayments.com'],
            'Bold': ['bold', 'boldcommerce.com'],
        }

        for app_name, indicators in app_indicators.items():
            if any(ind in html.lower() for ind in indicators):
                technologies.append(app_name)

        # 支付方式检测
        if 'paypal' in html.lower():
            technologies.append('PayPal')
        if 'shopify payments' in html.lower() or 'shop pay' in html.lower():
            technologies.append('Shop Pay')
        if 'klarna' in html.lower():
            technologies.append('Klarna')
        if 'afterpay' in html.lower():
            technologies.append('Afterpay')

        return technologies

    def detect_email_popup(self, html, soup):
        """检测邮件弹窗"""
        popup_indicators = [
            'email-popup',
            'newsletter-popup',
            'subscribe-modal',
            'email-capture',
            'mc_embed_signup',  # Mailchimp
        ]
        return any(indicator in html.lower() for indicator in popup_indicators)

    def detect_discount_code(self, html, soup):
        """检测折扣码"""
        discount_keywords = ['discount', 'coupon', 'promo', 'code', 'save', 'off']
        text_lower = html.lower()
        # 查找类似 "SAVE20" 或 "GET10OFF" 的折扣码
        return any(keyword in text_lower for keyword in discount_keywords)

    def detect_live_chat(self, html, soup):
        """检测在线客服"""
        chat_indicators = [
            'tawk.to',
            'intercom.io',
            'zendesk',
            'livechat',
            'drift.com',
            'crisp.chat',
            'tidio',
        ]
        return any(indicator in html.lower() for indicator in chat_indicators)

    def detect_mobile_friendly(self, soup):
        """检测是否移动端友好"""
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        return viewport is not None

    def estimate_product_count(self, soup):
        """估算产品数量（基于页面元素）"""
        # 这是一个简化版本，实际可以更复杂
        product_elements = soup.find_all(class_=['product', 'product-item', 'product-card'])
        if product_elements:
            # 假设显示的是部分产品，估算总数
            visible_count = len(product_elements)
            return visible_count * 10  # 粗略估算
        return None

    def calculate_score(self, result):
        """计算店铺质量综合评分 (0-100)"""
        score = 50  # 基础分

        # Google Ads (+10)
        if result['has_google_ads']:
            score += 10

        # 技术栈丰富度 (+15)
        tech_count = len(result['technologies'])
        score += min(tech_count * 3, 15)

        # 营销工具 (+15)
        if result['has_email_popup']:
            score += 5
        if result['has_discount_code']:
            score += 5
        if result['has_live_chat']:
            score += 5

        # 移动端友好 (+10)
        if result['mobile_friendly']:
            score += 10

        # 页面加载速度 (+10)
        if result['page_load_speed']:
            if result['page_load_speed'] < 2000:  # < 2秒
                score += 10
            elif result['page_load_speed'] < 4000:  # < 4秒
                score += 5

        return min(score, 100)


def analyze_batch(analyzer, limit=BATCH_SIZE, offset=0):
    """批量分析店铺"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    try:
        # 获取待分析的店铺
        cur.execute("""
            SELECT id, domain, domain_url
            FROM stores
            WHERE (analysis_status IS NULL OR analysis_status = 'pending')
                AND status = 'Active'
            ORDER BY estimated_monthly_visits DESC NULLS LAST
            LIMIT %s OFFSET %s
        """, (limit, offset))

        stores = cur.fetchall()

        if not stores:
            print("No stores to analyze")
            return 0

        analyzed_count = 0

        for store_id, domain, domain_url in stores:
            print(f"Analyzing: {domain}...")

            # 标记为处理中
            cur.execute("""
                UPDATE stores
                SET analysis_status = 'processing'
                WHERE id = %s
            """, (store_id,))
            conn.commit()

            try:
                # 执行分析
                result = analyzer.analyze_store(domain, domain_url)

                # 更新结果
                cur.execute("""
                    UPDATE stores
                    SET
                        has_google_ads = %s,
                        google_ads_detected_date = CASE WHEN %s THEN CURRENT_DATE ELSE NULL END,
                        technologies = %s,
                        has_email_popup = %s,
                        has_discount_code = %s,
                        has_live_chat = %s,
                        mobile_friendly = %s,
                        page_load_speed = %s,
                        product_count = %s,
                        analysis_score = %s,
                        analysis_status = 'completed',
                        last_analyzed_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (
                    result['has_google_ads'],
                    result['has_google_ads'],
                    json.dumps(result['technologies']) if result['technologies'] else None,
                    result['has_email_popup'],
                    result['has_discount_code'],
                    result['has_live_chat'],
                    result['mobile_friendly'],
                    result['page_load_speed'],
                    result['product_count'],
                    result['analysis_score'],
                    store_id
                ))
                conn.commit()

                analyzed_count += 1
                print(f"  ✓ Score: {result['analysis_score']}, "
                      f"Ads: {result['has_google_ads']}, "
                      f"Tech: {len(result['technologies'])}")

            except Exception as e:
                print(f"  ✗ Error: {e}")
                cur.execute("""
                    UPDATE stores
                    SET
                        analysis_status = 'failed',
                        analysis_notes = %s
                    WHERE id = %s
                """, (str(e), store_id))
                conn.commit()

            # 避免被封IP
            time.sleep(DELAY_SECONDS)

        return analyzed_count

    finally:
        cur.close()
        conn.close()


def main():
    """主函数"""
    print("=" * 60)
    print("Shopify Store Analyzer")
    print("=" * 60)
    print(f"Database: {DATABASE_URL[:50]}...")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Delay: {DELAY_SECONDS}s")
    print("=" * 60)

    analyzer = StoreAnalyzer()

    # 获取待分析总数
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*)
        FROM stores
        WHERE (analysis_status IS NULL OR analysis_status = 'pending')
            AND status = 'Active'
    """)
    total_pending = cur.fetchone()[0]
    cur.close()
    conn.close()

    print(f"\nTotal stores to analyze: {total_pending:,}")

    if total_pending == 0:
        print("No stores need analysis. Done!")
        return

    # 询问用户
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        proceed = 'y'
    else:
        proceed = input(f"\nAnalyze {min(BATCH_SIZE, total_pending)} stores? (y/n): ")

    if proceed.lower() != 'y':
        print("Cancelled.")
        return

    # 批量分析
    total_analyzed = 0
    offset = 0

    while offset < total_pending:
        print(f"\n{'='*60}")
        print(f"Batch {offset//BATCH_SIZE + 1} (offset: {offset})")
        print(f"{'='*60}")

        count = analyze_batch(analyzer, limit=BATCH_SIZE, offset=offset)

        if count == 0:
            break

        total_analyzed += count
        offset += BATCH_SIZE

        print(f"\nProgress: {total_analyzed:,} / {total_pending:,} analyzed")

        # 询问是否继续
        if offset < total_pending:
            if len(sys.argv) > 1 and sys.argv[1] == '--auto':
                continue
            else:
                cont = input("\nContinue to next batch? (y/n): ")
                if cont.lower() != 'y':
                    break

    print(f"\n{'='*60}")
    print(f"✓ Analysis complete!")
    print(f"  Total analyzed: {total_analyzed:,}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
