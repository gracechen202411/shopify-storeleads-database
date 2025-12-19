#!/usr/bin/env python3
"""
批量检查数据库中的店铺，找出最近30天才开始投放谷歌广告的新客户

策略：
1. 从数据库读取所有店铺
2. 使用 MCP Playwright 访问 Google Ads Transparency
3. 设置日期范围筛选器：
   - 结束日期：今天
   - 开始日期：今天-30天
4. 如果这个时间段内有广告 → 可能是新客户
5. 再检查30天前是否有广告来确认

豆豆的目标客户：
- 🎯 最近30天才开始投放（之前没投过）
- 🎯 已停止180天+（可重新激活）
- 🎯 超新客户（0-30天内开始投放）
"""

import psycopg2
import json
from datetime import datetime, timedelta
from pathlib import Path
import time

# 数据库连接配置
DB_CONFIG = {
    'host': 'ep-odd-bush-a1ixr52d.ap-southeast-1.aws.neon.tech',
    'database': 'storeleads',
    'user': 'storeleads_owner',
    'password': 'npg_jJbMnkDXoqMd',  # 你需要填写实际密码
    'sslmode': 'require'
}

# 输出文件
OUTPUT_FILE = 'potential_new_customers.json'
BATCH_SIZE = 50  # 每批处理的店铺数量


class NewStarterChecker:
    def __init__(self, db_config):
        self.db_config = db_config
        self.results = self._load_results()

    def _load_results(self):
        """加载已有结果"""
        if Path(OUTPUT_FILE).exists():
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'checked_at': datetime.now().isoformat(),
            'last_30_days_check': {},
            'summary': {
                'total_checked': 0,
                'has_recent_ads': 0,
                'needs_manual_verify': 0
            }
        }

    def _save_results(self):
        """保存结果"""
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

    def get_stores_from_file(self, file_path, limit=BATCH_SIZE):
        """
        从CSV文件读取店铺列表
        兼容 import-to-neon.py 生成的CSV格式
        """
        import csv

        domains = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    domain = row.get('domain') or row.get('Domain')
                    if domain:
                        domains.append(domain)
        except Exception as e:
            print(f"❌ 读取文件失败：{e}")
            return []

        # 过滤掉已经检查过的（30天内）
        unchecked = []
        for domain in domains:
            if domain not in self.results['last_30_days_check']:
                unchecked.append(domain)
            else:
                checked_time = datetime.fromisoformat(
                    self.results['last_30_days_check'][domain].get('checked_at', '2000-01-01')
                )
                if (datetime.now() - checked_time).days > 30:
                    unchecked.append(domain)

        return unchecked[:limit]

    def get_stores_to_check(self, limit=BATCH_SIZE):
        """
        从数据库获取需要检查的店铺（需要数据库密码）

        如果没有数据库密码，使用 get_stores_from_file() 从CSV文件读取
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            # 获取所有有 Google Ads 记录的店铺
            cur.execute("""
                SELECT DISTINCT domain
                FROM stores
                WHERE domain IS NOT NULL
                ORDER BY domain
                LIMIT %s
            """, (limit,))

            stores = [row[0] for row in cur.fetchall()]

            # 过滤掉已经检查过的（30天内）
            unchecked = []
            for domain in stores:
                if domain not in self.results['last_30_days_check']:
                    unchecked.append(domain)
                else:
                    checked_time = datetime.fromisoformat(
                        self.results['last_30_days_check'][domain].get('checked_at', '2000-01-01')
                    )
                    if (datetime.now() - checked_time).days > 30:
                        unchecked.append(domain)

            cur.close()
            conn.close()

            return unchecked[:limit]
        except psycopg2.OperationalError as e:
            print(f"❌ 数据库连接失败：{e}")
            print("💡 提示：请使用 get_stores_from_file('你的CSV文件.csv') 从文件读取店铺列表")
            return []

    def generate_check_list(self, domains):
        """
        生成需要手动检查的域名列表（JSON格式）
        用于 MCP Playwright 批量检查

        检查逻辑：
        1. 先看是否有广告（所有时间）
        2. 如果有广告，设置日期范围结束日期 = 30天前
        3. 如果30天前没有广告 → 新客户！
        """
        today = datetime.now()
        thirty_days_ago = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')

        check_list = {
            'strategy': {
                'description': '找出最近30天才开始投放谷歌广告的新客户',
                'step1': '检查是否有谷歌广告（任何时间段）',
                'step2': f'如果有广告，设置日期范围结束 = {thirty_days_ago}（30天前）',
                'step3': '如果30天前没有广告 → 这是新客户！',
                'thirty_days_ago': thirty_days_ago,
                'today': today_str
            },
            'domains_to_check': []
        }

        for domain in domains:
            check_list['domains_to_check'].append({
                'domain': domain,
                'url': f'https://adstransparency.google.com/advertiser?advertiserName={domain}',
                'instructions': [
                    '步骤1：检查是否有广告',
                    '  - 访问 Google Ads Transparency 页面',
                    '  - 查看是否显示任何广告（不设置日期筛选）',
                    '  - 如果没有广告 → 跳过此店铺',
                    '',
                    '步骤2：检查30天前是否有广告（关键！）',
                    '  - 点击"日期范围"筛选器',
                    f'  - 设置结束日期：{thirty_days_ago}（30天前）',
                    '  - 留空开始日期或设置为很早的日期（如2018-01-01）',
                    '  - 查看是否有广告',
                    '',
                    '判断结果：',
                    f'  ✅ 如果30天前（{thirty_days_ago}之前）没有广告 → 🔥 新客户！',
                    f'  ❌ 如果30天前（{thirty_days_ago}之前）有广告 → 老客户，跳过'
                ],
                'check_fields': {
                    'has_any_ads': None,  # 是否有广告（任何时间）
                    'total_ad_count': 0,  # 总广告数
                    'has_ads_before_30_days': None,  # 30天前是否有广告（关键判断）
                    'ad_count_before_30_days': 0,  # 30天前的广告数
                    'is_new_customer': None,  # True = 新客户, False = 老客户
                    'first_ad_date': None,  # 第一个广告的日期
                    'last_seen_date': None   # 最后展示时间
                }
            })

        # 保存检查列表
        output_file = f'check_list_new_customers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(check_list, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 生成检查列表：{output_file}")
        print(f"📋 需要检查 {len(domains)} 个域名")
        print(f"📅 关键日期：30天前 = {thirty_days_ago}")
        print(f"\n🎯 检查策略：")
        print(f"   1. 访问每个店铺的 Google Ads Transparency")
        print(f"   2. 先看是否有广告（任何时间）")
        print(f"   3. 如果有广告，设置日期范围结束 = {thirty_days_ago}")
        print(f"   4. 如果30天前没有广告 → 这是新客户！")

        return output_file

    def add_check_result(self, domain, result):
        """
        添加检查结果

        result = {
            'has_any_ads': True,  # 是否有广告（任何时间）
            'total_ad_count': 100,  # 总广告数
            'has_ads_before_30_days': False,  # 30天前是否有广告（关键！）
            'ad_count_before_30_days': 0,  # 30天前的广告数
            'is_new_customer': True,  # True = 新客户
            'first_ad_date': '2025-11-20',  # 第一个广告日期
            'last_seen_date': '2025-12-18',  # 最后展示时间
            'checked_at': '2025-12-18T16:00:00'
        }
        """
        self.results['last_30_days_check'][domain] = result
        self.results['summary']['total_checked'] += 1

        # 统计新客户数量
        if result.get('is_new_customer'):
            if 'new_customers_found' not in self.results['summary']:
                self.results['summary']['new_customers_found'] = 0
            self.results['summary']['new_customers_found'] += 1

        self._save_results()

    def analyze_potential_new_customers(self):
        """
        分析哪些是潜在的新客户

        新逻辑：
        1. 有广告（任何时间）
        2. 30天前没有广告 → 新客户！
        """
        potential_new = []

        for domain, data in self.results['last_30_days_check'].items():
            # 必须有广告
            if not data.get('has_any_ads'):
                continue

            # 关键判断：30天前没有广告 = 新客户
            if data.get('is_new_customer') or (
                data.get('has_any_ads') and
                not data.get('has_ads_before_30_days')
            ):
                first_ad = data.get('first_ad_date')

                # 计算开始投放的天数
                days_ago = None
                if first_ad:
                    try:
                        first_ad_date = datetime.strptime(first_ad, '%Y-%m-%d')
                        days_ago = (datetime.now() - first_ad_date).days
                    except:
                        days_ago = None

                potential_new.append({
                    'domain': domain,
                    'first_ad_date': first_ad or '未知',
                    'days_ago': days_ago if days_ago is not None else '未知',
                    'total_ad_count': data.get('total_ad_count', 0),
                    'last_seen_date': data.get('last_seen_date', '未知'),
                    'status': '🔥 超新客户（30天内开始投放）',
                    'priority': 100,
                    'recommendation': '立即联系！刚开始投放，最佳时机！',
                    'verification': f"30天前无广告，现在有 {data.get('total_ad_count', 0)} 个广告"
                })

        # 按天数排序（最新的排前面）
        potential_new.sort(key=lambda x: x['days_ago'] if isinstance(x['days_ago'], int) else 999)

        return potential_new

    def generate_report(self):
        """生成豆豆的客户报告"""
        print("\n" + "="*100)
        print("🎯 豆豆的潜在新客户报告")
        print("="*100)

        potential_new = self.analyze_potential_new_customers()

        print(f"\n📊 检查统计：")
        print(f"- 已检查店铺：{self.results['summary']['total_checked']}")
        print(f"- 最近30天有广告：{self.results['summary']['has_recent_ads']}")
        print(f"- 🔥 超新客户（30天内开始）：{len(potential_new)}")

        if potential_new:
            print(f"\n{'='*100}")
            print("🔥 超新客户清单（按时间排序）")
            print(f"{'='*100}")

            for i, customer in enumerate(potential_new, 1):
                print(f"\n{i}. {customer['domain']}")
                print(f"   首次投放：{customer['first_ad_date']} ({customer['days_ago']}天前)")
                print(f"   最后展示：{customer['last_seen_date']}")
                print(f"   广告数量：{customer['ad_count_last_30_days']}")
                print(f"   优先级：{customer['priority']}/150")
                print(f"   建议：{customer['recommendation']}")
        else:
            print("\n⚠️ 暂无超新客户，请先使用 generate_check_list() 生成检查列表")

        # 保存报告
        report_file = f'new_customers_report_{datetime.now().strftime("%Y%m%d")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'summary': self.results['summary'],
                'potential_new_customers': potential_new
            }, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 报告已保存：{report_file}")


def main():
    """主函数"""
    import sys

    print("="*100)
    print("🎯 批量检查新开始投放广告的客户")
    print("="*100)

    checker = NewStarterChecker(DB_CONFIG)

    # 步骤1：获取需要检查的店铺
    print("\n步骤1：获取店铺列表...")

    # 检查是否提供了CSV文件路径
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        print(f"从CSV文件读取：{csv_file}")
        domains = checker.get_stores_from_file(csv_file, limit=BATCH_SIZE)
    else:
        print("尝试从数据库读取...")
        domains = checker.get_stores_to_check(limit=BATCH_SIZE)

    if not domains:
        print("\n❌ 没有找到需要检查的店铺")
        print("\n使用方法：")
        print("  python3 batch_check_new_starters.py [CSV文件路径]")
        print("\n示例：")
        print("  python3 batch_check_new_starters.py ../data/selected_stores.csv")
        checker.generate_report()
        return

    print(f"找到 {len(domains)} 个需要检查的店铺")

    # 步骤2：生成检查列表
    print("\n步骤2：生成检查列表...")
    check_list_file = checker.generate_check_list(domains)

    print("\n" + "="*100)
    print("下一步操作指南")
    print("="*100)
    print(f"""
1. 打开生成的检查列表：{check_list_file}

2. 使用 MCP Playwright 工具逐个检查：
   - 访问每个店铺的 Google Ads Transparency 页面
   - 设置日期范围筛选器（最近30天）
   - 记录是否有广告、广告数量
   - 点击第一个广告查看"最后展示时间"

3. 检查完成后，使用以下代码添加结果：

   from batch_check_new_starters import NewStarterChecker

   checker = NewStarterChecker(DB_CONFIG)
   checker.add_check_result('example.com', {{
       'has_ads_in_last_30_days': True,
       'ad_count_last_30_days': 50,
       'first_ad_date': '2025-11-20',
       'last_seen_date': '2025-12-18',
       'checked_at': datetime.now().isoformat()
   }})

4. 生成豆豆的客户报告：

   checker.generate_report()
""")


if __name__ == '__main__':
    main()
