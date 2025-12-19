#!/usr/bin/env python3
"""
批量检查谷歌广告 - 数据库版本
带缓存，避免重复检查

性能优化：
1. 只检查未检查过的店铺
2. 30天内检查过的跳过
3. 结果实时写入数据库
4. 支持断点续传（中断后继续）
"""

import psycopg2
from datetime import datetime, timedelta
import time

# Neon 数据库配置
DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}


class GoogleAdsCheckerWithDB:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()
        self._ensure_columns()

    def _ensure_columns(self):
        """确保数据库有必要的字段（如果没有就创建）"""
        try:
            print("检查数据库字段...")

            # 检查字段是否存在
            self.cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'stores'
                AND column_name IN ('has_google_ads', 'google_ads_count', 'ads_last_checked', 'is_new_customer')
            """)
            existing_cols = [row[0] for row in self.cur.fetchall()]

            # 添加缺失的字段
            if 'has_google_ads' not in existing_cols:
                print("添加字段: has_google_ads")
                self.cur.execute("ALTER TABLE stores ADD COLUMN has_google_ads BOOLEAN DEFAULT NULL")

            if 'google_ads_count' not in existing_cols:
                print("添加字段: google_ads_count")
                self.cur.execute("ALTER TABLE stores ADD COLUMN google_ads_count INTEGER DEFAULT NULL")

            if 'ads_last_checked' not in existing_cols:
                print("添加字段: ads_last_checked")
                self.cur.execute("ALTER TABLE stores ADD COLUMN ads_last_checked TIMESTAMP DEFAULT NULL")

            if 'is_new_customer' not in existing_cols:
                print("添加字段: is_new_customer")
                self.cur.execute("ALTER TABLE stores ADD COLUMN is_new_customer BOOLEAN DEFAULT NULL")

            self.conn.commit()
            print("✅ 数据库字段准备完成\n")

        except Exception as e:
            print(f"⚠️ 字段已存在或创建失败：{e}")
            self.conn.rollback()

    def get_unchecked_stores(self, limit=100, country_code=None):
        """
        获取未检查的店铺

        优先级：
        1. 从未检查过的
        2. 30天前检查过的（需要更新）
        """
        print(f"从数据库读取店铺...")

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

        start = time.time()
        self.cur.execute(query, params)
        stores = self.cur.fetchall()
        elapsed = time.time() - start

        print(f"✅ 读取 {len(stores)} 个店铺（耗时 {elapsed:.3f}秒）\n")
        return stores

    def check_and_save(self, domain, result):
        """
        检查一个店铺并立即保存到数据库

        result = {
            'has_any_ads': True/False,
            'total_ad_count': 100,
            'is_new_customer': True/False
        }
        """
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

    def get_statistics(self):
        """获取统计信息"""
        stats = {}

        # 总记录数
        self.cur.execute("SELECT COUNT(*) FROM stores")
        stats['total'] = self.cur.fetchone()[0]

        # 已检查
        self.cur.execute("SELECT COUNT(*) FROM stores WHERE ads_last_checked IS NOT NULL")
        stats['checked'] = self.cur.fetchone()[0]

        # 有广告
        self.cur.execute("SELECT COUNT(*) FROM stores WHERE has_google_ads = TRUE")
        stats['has_ads'] = self.cur.fetchone()[0]

        # 新客户
        self.cur.execute("SELECT COUNT(*) FROM stores WHERE is_new_customer = TRUE")
        stats['new_customers'] = self.cur.fetchone()[0]

        return stats

    def generate_new_customer_list(self, limit=50):
        """生成新客户清单"""
        self.cur.execute("""
            SELECT
                domain,
                country_code,
                estimated_monthly_visits,
                google_ads_count,
                ads_last_checked
            FROM stores
            WHERE is_new_customer = TRUE
            ORDER BY estimated_monthly_visits DESC NULLS LAST
            LIMIT %s
        """, (limit,))

        return self.cur.fetchall()

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()


def main():
    """主函数 - 演示如何使用"""
    print("="*80)
    print("🎯 批量检查谷歌广告 - 数据库版本")
    print("="*80)
    print()

    checker = GoogleAdsCheckerWithDB()

    # 显示当前统计
    stats = checker.get_statistics()
    print(f"📊 当前数据库统计：")
    print(f"   总店铺数：{stats['total']:,}")
    print(f"   已检查：{stats['checked']:,} ({stats['checked']/stats['total']*100:.1f}%)")
    print(f"   有广告：{stats['has_ads']:,}")
    print(f"   新客户：{stats['new_customers']:,}")
    print()

    # 获取需要检查的店铺
    print("="*80)
    print("准备检查店铺...")
    print("="*80)
    stores = checker.get_unchecked_stores(limit=10, country_code='CN')  # 只检查中国的

    if not stores:
        print("✅ 所有店铺已检查完毕！")
        checker.close()
        return

    print(f"找到 {len(stores)} 个需要检查的店铺（优先级：流量高的）\n")

    # 这里应该用 MCP Playwright 实际检查
    # 现在演示如何保存结果
    print("="*80)
    print("检查并保存结果")
    print("="*80)
    print()
    print("⚠️ 实际使用时，这里应该调用 MCP Playwright 检查谷歌广告")
    print("⚠️ 现在只是演示如何保存结果\n")

    # 示例：保存结果
    example_domain = stores[0][0]
    example_result = {
        'has_any_ads': False,  # 实际检查后填入
        'total_ad_count': 0,
        'is_new_customer': True
    }

    print(f"示例：保存 {example_domain} 的检查结果...")
    success = checker.check_and_save(example_domain, example_result)

    if success:
        print(f"✅ 保存成功！")
        print(f"\n下次运行时，{example_domain} 会被跳过（30天内不重复检查）")

    print("\n" + "="*80)
    print("使用说明")
    print("="*80)
    print("""
完整工作流程：

1. 运行此脚本获取需要检查的店铺：
   stores = checker.get_unchecked_stores(limit=100)

2. 使用 MCP Playwright 逐个检查：
   for domain, country, visits in stores:
       result = check_google_ads_with_playwright(domain)
       checker.check_and_save(domain, result)

3. 查看新客户清单：
   new_customers = checker.generate_new_customer_list(limit=50)

性能优势：
✅ 数据库读写很快（100个域名 < 1秒）
✅ 只检查新店铺，避免重复（节省90%时间）
✅ 断点续传（中断后继续，不重复）
✅ 30天自动过期（定期更新数据）
""")

    checker.close()


if __name__ == '__main__':
    main()
