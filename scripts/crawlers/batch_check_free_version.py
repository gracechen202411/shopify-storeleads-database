#!/usr/bin/env python3
"""
批量检查谷歌广告 - 免费版本（不消耗Claude Code Token）

使用纯Python + Playwright库，完全本地运行
性能：每个店铺2-5秒，100个店铺 ≈ 5-8分钟

安装依赖：
pip install playwright psycopg2-binary
playwright install chromium
"""

import psycopg2
from playwright.sync_api import sync_playwright
from datetime import datetime
import time
import json

# 数据库配置
DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}


class FreeGoogleAdsChecker:
    """完全免费的谷歌广告检查器（不消耗Claude Code Token）"""

    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()
        self.browser = None
        self.page = None

    def start_browser(self):
        """启动浏览器（只启动一次，重复使用）"""
        print("启动浏览器...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        print("✅ 浏览器已启动\n")

    def check_google_ads(self, domain):
        """
        检查单个域名的谷歌广告
        返回：{
            'has_any_ads': True/False,
            'total_ad_count': 数量,
            'is_new_customer': True/False,
            'advertiser': '广告主名称' (如果有)
        }
        """
        # 去掉 www. 前缀，确保查询准确
        check_domain = domain.replace('www.', '').strip()
        url = f'https://adstransparency.google.com/?region=anywhere&domain={check_domain}'

        try:
            # 访问页面
            self.page.goto(url, timeout=30000)
            time.sleep(2)  # 等待加载

            # 获取页面内容
            content = self.page.content()

            # 判断是否有广告
            if '0 个广告' in content or '未找到任何广告' in content:
                return {
                    'has_any_ads': False,
                    'total_ad_count': 0,
                    'is_new_customer': True,  # 从来没打过广告
                    'advertiser': None
                }

            # 有广告，提取广告数量
            ad_count = 0
            if '个广告' in content:
                # 尝试提取数字
                import re
                match = re.search(r'(\d+|~\d+) 个广告', content)
                if match:
                    count_str = match.group(1).replace('~', '')
                    ad_count = int(count_str)

            # 提取广告主名称
            advertiser = None
            if '已验证' in content:
                # 简单提取，可能需要改进
                match = re.search(r'<generic[^>]*>([^<]+)</generic>\s*<generic[^>]*>已验证', content)
                if match:
                    advertiser = match.group(1)

            # 检查30天前是否有广告（简化版：如果广告数 > 50，大概率是老客户）
            is_new = ad_count < 10  # 广告少于10个，可能是新客户

            return {
                'has_any_ads': True,
                'total_ad_count': ad_count,
                'is_new_customer': is_new,
                'advertiser': advertiser
            }

        except Exception as e:
            print(f"❌ 检查失败 {domain}: {e}")
            return None

    def get_unchecked_stores(self, limit=100, country_code=None):
        """获取未检查的店铺"""
        query = """
            SELECT domain, country_code, estimated_monthly_visits
            FROM stores
            WHERE (
                ads_last_checked IS NULL
                OR ads_last_checked < NOW() - INTERVAL '30 days'
            )
        """

        params = []
        if country_code:
            query += " AND country_code = %s"
            params.append(country_code)

        query += " ORDER BY estimated_monthly_visits DESC NULLS LAST LIMIT %s"
        params.append(limit)

        self.cur.execute(query, params)
        return self.cur.fetchall()

    def save_result(self, domain, result):
        """保存检查结果到数据库"""
        try:
            self.cur.execute("""
                UPDATE stores
                SET
                    has_google_ads = %s,
                    google_ads_count = %s,
                    is_new_customer = %s,
                    ads_last_checked = NOW()
                WHERE domain = %s
            """, (
                result['has_any_ads'],
                result['total_ad_count'],
                result['is_new_customer'],
                domain
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ 保存失败 {domain}: {e}")
            self.conn.rollback()
            return False

    def batch_check(self, limit=100, country_code=None):
        """批量检查"""
        print("="*80)
        print("🎯 批量检查谷歌广告 - 免费版本（不消耗Token）")
        print("="*80)
        print()

        # 获取店铺列表
        print(f"从数据库读取店铺...")
        stores = self.get_unchecked_stores(limit=limit, country_code=country_code)

        if not stores:
            print("✅ 所有店铺已检查完毕！")
            return

        print(f"✅ 找到 {len(stores)} 个需要检查的店铺\n")

        # 启动浏览器
        self.start_browser()

        # 统计
        stats = {
            'total': len(stores),
            'success': 0,
            'failed': 0,
            'new_customers': 0,
            'has_ads': 0
        }

        print("="*80)
        print("开始检查...")
        print("="*80)
        print()

        start_time = time.time()

        for i, (domain, country, visits) in enumerate(stores, 1):
            print(f"[{i}/{len(stores)}] 检查 {domain} ({country}, {visits:,} visits/月)...")

            result = self.check_google_ads(domain)

            if result:
                # 显示结果
                if result['has_any_ads']:
                    status = f"✅ 有广告 ({result['total_ad_count']}个)"
                    if not result['is_new_customer']:
                        status += " - 老客户"
                    else:
                        status += " - 🔥 可能是新客户"
                        stats['new_customers'] += 1
                    stats['has_ads'] += 1
                else:
                    status = "🔥 新客户（从未投放）"
                    stats['new_customers'] += 1

                print(f"         {status}")

                # 保存到数据库
                if self.save_result(domain, result):
                    stats['success'] += 1
                else:
                    stats['failed'] += 1
            else:
                print(f"         ❌ 检查失败")
                stats['failed'] += 1

            print()

            # 每10个显示一次进度
            if i % 10 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                remaining = (len(stores) - i) * avg_time
                print(f"📊 进度：{i}/{len(stores)} ({i/len(stores)*100:.1f}%)")
                print(f"⏱️  已用时：{elapsed/60:.1f}分钟，预计剩余：{remaining/60:.1f}分钟")
                print(f"🔥 发现新客户：{stats['new_customers']}个")
                print()

        # 总结
        elapsed = time.time() - start_time
        print("="*80)
        print("检查完成！")
        print("="*80)
        print(f"总计：{stats['total']}个店铺")
        print(f"成功：{stats['success']}个")
        print(f"失败：{stats['failed']}个")
        print(f"有广告：{stats['has_ads']}个")
        print(f"🔥 新客户：{stats['new_customers']}个")
        print(f"⏱️  总耗时：{elapsed/60:.1f}分钟")
        print(f"平均：{elapsed/len(stores):.1f}秒/个")

        self.close()

    def close(self):
        """关闭浏览器和数据库连接"""
        if self.browser:
            self.browser.close()
            self.playwright.stop()
        if self.conn:
            self.cur.close()
            self.conn.close()


def main():
    """主函数"""
    import sys

    # 参数
    limit = 100  # 默认检查100个
    country_code = 'CN'  # 默认中国

    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    if len(sys.argv) > 2:
        country_code = sys.argv[2]

    print(f"参数：检查 {limit} 个店铺，国家：{country_code}")
    print()

    checker = FreeGoogleAdsChecker()
    checker.batch_check(limit=limit, country_code=country_code)


if __name__ == '__main__':
    main()
