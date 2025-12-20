#!/usr/bin/env python3
"""
阶段一：快速筛选（MCP 版本）
由 Claude Code 执行，使用 MCP Playwright

输出：
- never_advertised：待保存列表
- suspected_new_advertiser：待保存列表
- skip：待保存列表
"""

import psycopg2

# 数据库配置
DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}


def get_target_stores(min_visits=100000):
    """SQL 层筛选目标店铺"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    query = """
        SELECT domain, estimated_monthly_visits, city, state
        FROM stores
        WHERE country_code = 'CN'
          AND (
            city ILIKE %s OR city ILIKE %s
            OR region ILIKE %s OR state ILIKE %s
          )
          AND estimated_monthly_visits >= %s
          AND (
            ads_last_checked IS NULL
            OR ads_last_checked < NOW() - INTERVAL '30 days'
          )
        ORDER BY estimated_monthly_visits DESC
    """

    cur.execute(query, (
        '%Hangzhou%', '%杭州%',
        '%Zhejiang%', '%Zhejiang%',
        min_visits
    ))

    stores = cur.fetchall()
    cur.close()
    conn.close()

    return stores


def save_result(domain, customer_type, ads_count):
    """保存检查结果"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE stores
            SET
                customer_type = %s,
                google_ads_count = %s,
                has_google_ads = %s,
                ads_check_level = 'fast',
                ads_last_checked = NOW()
            WHERE domain = %s
        """, (
            customer_type,
            ads_count,
            ads_count > 0 if ads_count is not None else None,
            domain
        ))
        conn.commit()
        print(f"  💾 已保存：{domain} -> {customer_type}")
        return True

    except Exception as e:
        print(f"  ❌ 保存失败: {e}")
        conn.rollback()
        return False

    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 获取目标店铺列表")
    print("=" * 80)
    print()

    stores = get_target_stores(100000)

    print(f"找到 {len(stores)} 个目标店铺：")
    print()
    for i, (domain, visits, city, state) in enumerate(stores, 1):
        print(f"{i}. {domain}")
        print(f"   访问量：{visits:,}/月")
        print(f"   位置：{city or state}")
        print()

    print("=" * 80)
    print("✅ 准备完成")
    print()
    print("下一步：Claude Code 使用 MCP Playwright 逐个检查")
    print("=" * 80)
