#!/usr/bin/env python3
"""
Identify NEW Google Ads customers for Doudou
识别 Google 广告新客户（适合 Google 直客经理拓展）

判断标准：
1. 最近30-90天开始投放广告（新客户）
2. 广告数量 > 50（有一定规模，值得跟进）
3. 多个广告账号 = 可能是代理商客户
4. 单个广告账号 = 可能是自运营，更适合直客

使用 MCP Playwright 工具手动检查每个域名的日期范围
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path

# 缓存文件
CACHE_FILE = 'new_customers_cache.json'


class NewCustomerIdentifier:
    def __init__(self, cache_file=CACHE_FILE):
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self):
        if Path(self.cache_file).exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def add_store_data(self, domain, data):
        """
        添加店铺的 Google Ads 数据

        data = {
            'ad_count': 2000,  # 广告总数
            'advertiser_count': 2,  # 广告主数量
            'advertisers': ['Emma Liu', '深圳市茵格瑞科技有限公司'],
            'start_date': '2018-05-31',  # 最早广告日期
            'end_date': '2025-12-18',  # 最新广告日期
            'has_ads': True
        }
        """
        self.cache[domain] = {
            **data,
            'checked_at': datetime.now().isoformat()
        }
        self._save_cache()

    def is_new_customer(self, domain, days_threshold=90):
        """
        判断是否为新客户（最近N天开始投放广告）
        """
        if domain not in self.cache:
            return None  # 未检查

        data = self.cache[domain]

        if not data.get('has_ads'):
            return False

        start_date_str = data.get('start_date')
        if not start_date_str:
            return None

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            days_ago = (datetime.now() - start_date).days

            return days_ago <= days_threshold
        except:
            return None

    def get_customer_profile(self, domain):
        """获取客户画像"""
        if domain not in self.cache:
            return None

        data = self.cache[domain]

        if not data.get('has_ads'):
            return {
                'domain': domain,
                'status': '无广告',
                'priority': 0
            }

        # 计算投放天数
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        today = datetime.now()

        # 判断是否还在投放（结束日期是今天或最近几天）
        days_since_last_ad = (today - end_date).days
        is_still_running = days_since_last_ad <= 7  # 7天内有广告 = 还在投放

        # 实际投放天数（从开始到结束）
        actual_running_days = (end_date - start_date).days

        # 用开始日期计算（判断新老客户）
        days_running = (datetime.now() - start_date).days

        # 豆豆的客户分类逻辑
        ad_count = data.get('ad_count', 0)
        advertiser_count = data.get('advertiser_count', 1)

        # 🔴 关键判断：如果已经停止投放，直接标记为"已停止"
        if not is_still_running:
            priority = 0  # 已停止投放，优先级最低
            status = '🛑 已停止投放'
            category = 'STOPPED'

            # 计算停止了多久
            stopped_days = days_since_last_ad
            stopped_reason = f"最后广告：{data['end_date']}（{stopped_days}天前停止）"
        else:
            # 还在投放的客户，按正常逻辑分类
            is_super_new = days_running <= 30  # 超新客户（0-30天）
            is_cooling = 30 < days_running <= 180  # 冷却期（31-180天）- 不要碰
            is_old = days_running > 180  # 老客户（180天+）- 可以挖

            # 计算优先级评分
            priority = 0

            if is_super_new:
                priority += 100  # 超新客户 - 最高优先级！
                status = '🔥 超新客户'
                category = 'TARGET'  # 目标客户
            elif is_cooling:
                priority = 0  # 冷却期 - 不要碰！
                status = '❄️ 冷却期'
                category = 'AVOID'  # 避免打扰
            elif is_old:
                priority += 40  # 老客户 - 可以挖
                status = '♻️ 再营销客户'
                category = 'REMARKETING'  # 再营销
            else:
                priority = 0
                status = '⚠️ 未知'
                category = 'UNKNOWN'

            stopped_reason = None

        # 广告规模加分（只对TARGET和REMARKETING客户加分）
        if category in ['TARGET', 'REMARKETING']:
            if ad_count > 1000:
                priority += 30
                scale = '大规模'
            elif ad_count > 200:
                priority += 20
                scale = '中规模'
            elif ad_count > 50:
                priority += 10
                scale = '小规模'
            else:
                priority += 5
                scale = '测试中'
        else:
            # 冷却期客户不管规模多大都不加分
            if ad_count > 1000:
                scale = '大规模'
            elif ad_count > 200:
                scale = '中规模'
            elif ad_count > 50:
                scale = '小规模'
            else:
                scale = '测试中'

        # 账号类型
        if advertiser_count == 1:
            account_type = '自运营（直客潜力⭐）'
            if category in ['TARGET', 'REMARKETING']:
                priority += 15  # 自运营更有价值
        else:
            account_type = f'代理商运营（{advertiser_count}个账号）'
            if category in ['TARGET', 'REMARKETING']:
                priority += 5

        result = {
            'domain': domain,
            'status': status,
            'category': category,
            'days_running': days_running,
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'is_still_running': is_still_running,
            'days_since_last_ad': days_since_last_ad,
            'actual_running_days': actual_running_days,
            'ad_count': ad_count,
            'scale': scale,
            'advertiser_count': advertiser_count,
            'advertisers': data.get('advertisers', []),
            'account_type': account_type,
            'priority': priority,
        }

        # 添加建议
        if category == 'STOPPED':
            # 🎯 关键修改：已停止180天+的客户其实是金矿！
            if days_since_last_ad >= 180:
                result['recommendation'] = f"🎯 可重新激活！已停止{days_since_last_ad}天，之前投过广告，可能想重新开始"
                result['stopped_reason'] = stopped_reason
                result['priority'] = 80  # 重新激活客户也有高优先级
            else:
                result['recommendation'] = f"⏸️ 暂时不适合：刚停止{days_since_last_ad}天，可能在调整策略"
                result['stopped_reason'] = stopped_reason
        else:
            result['recommendation'] = self._get_recommendation(
                category == 'TARGET',
                category == 'AVOID',
                category == 'REMARKETING',
                ad_count,
                advertiser_count
            )

        return result

    def _get_recommendation(self, is_super_new, is_cooling, is_old, ad_count, advertiser_count):
        """生成销售建议（豆豆版本）"""
        if is_super_new:
            if ad_count > 200:
                return '🎯🎯🎯 顶级目标！超新客户+大规模投放，立即联系！'
            elif ad_count > 50:
                return '🎯 高优先级！超新客户，正在起步阶段，快速跟进！'
            else:
                return '✅ 值得跟进：超新客户刚开始测试，可以引导扩大投放'
        elif is_cooling:
            return '❌ 不要打扰！冷却期客户（31-180天），可能刚签了服务商，等180天后再联系'
        elif is_old:
            if ad_count > 1000:
                return '💰 大客户再营销：投放超过半年+大规模，可能对现有服务不满，值得挖掘'
            elif ad_count > 200:
                return '♻️ 可以尝试：老客户，合同可能到期，可以推荐更优服务'
            elif ad_count < 50:
                return '⚠️ 优先级低：老客户但投放规模小，可能预算有限'
            else:
                return '📊 老客户，可作为参考案例'
        else:
            return '⚠️ 数据异常，需要人工检查'

    def generate_report(self):
        """生成客户报告"""
        profiles = []

        for domain in self.cache:
            profile = self.get_customer_profile(domain)
            if profile:
                profiles.append(profile)

        # 按优先级排序
        profiles.sort(key=lambda x: x['priority'], reverse=True)

        return profiles


def main():
    """主函数 - 演示如何使用"""
    print("="*100)
    print("🎯 Google Ads 新客户识别工具 - 适用于 Google 直客经理")
    print("="*100)

    identifier = NewCustomerIdentifier()

    # 示例1：添加 geckocustom.com 的数据（还在投放）
    print("\n示例1：添加 geckocustom.com 的分析数据...")
    identifier.add_store_data('geckocustom.com', {
        'ad_count': 2000,
        'advertiser_count': 2,
        'advertisers': ['Emma Liu', '深圳市茵格瑞科技有限公司'],
        'start_date': '2018-05-31',
        'end_date': '2025-12-18',  # 最后展示时间：今天
        'has_ads': True
    })

    # 示例2：添加 multicustomize.com 的数据（已停止263天）
    print("示例2：添加 multicustomize.com 的分析数据...")
    identifier.add_store_data('multicustomize.com', {
        'ad_count': 3,
        'advertiser_count': 1,
        'advertisers': ['Doggie Doggie E-Commerce LTD'],
        'start_date': '2018-05-31',  # 可能的开始日期
        'end_date': '2025-03-30',  # 最后展示时间：2025年3月30日（关键！）
        'has_ads': True
    })

    # 获取两个客户画像并对比
    profile1 = identifier.get_customer_profile('geckocustom.com')
    profile2 = identifier.get_customer_profile('multicustomize.com')

    print(f"\n{'='*100}")
    print(f"案例1: geckocustom.com - 还在投放的老客户")
    print(f"{'='*100}")
    print(f"域名: {profile1['domain']}")
    print(f"状态: {profile1['status']}")
    print(f"客户类型: {profile1['category']}")
    print(f"投放时长: {profile1['days_running']} 天")
    print(f"开始日期: {profile1['start_date']}")
    print(f"结束日期: {profile1['end_date']}")
    print(f"还在投放: {'✅ 是' if profile1['is_still_running'] else '❌ 否'}")
    print(f"距离最后广告: {profile1['days_since_last_ad']} 天")
    print(f"广告数量: {profile1['ad_count']} 个")
    print(f"投放规模: {profile1['scale']}")
    print(f"广告主数量: {profile1['advertiser_count']}")
    print(f"账号类型: {profile1['account_type']}")
    print(f"优先级评分: {profile1['priority']}/150")
    print(f"\n💡 豆豆的行动建议: {profile1['recommendation']}")

    print(f"\n{'='*100}")
    print(f"案例2: multicustomize.com - 已停止投放263天")
    print(f"{'='*100}")
    print(f"域名: {profile2['domain']}")
    print(f"状态: {profile2['status']}")
    print(f"客户类型: {profile2['category']}")
    print(f"投放时长: {profile2['days_running']} 天")
    print(f"开始日期: {profile2['start_date']}")
    print(f"结束日期: {profile2['end_date']}")
    print(f"还在投放: {'✅ 是' if profile2['is_still_running'] else '❌ 否'}")
    print(f"距离最后广告: {profile2['days_since_last_ad']} 天")
    print(f"实际投放天数: {profile2['actual_running_days']} 天")
    print(f"广告数量: {profile2['ad_count']} 个")
    print(f"投放规模: {profile2['scale']}")
    print(f"广告主数量: {profile2['advertiser_count']}")
    print(f"账号类型: {profile2['account_type']}")
    print(f"优先级评分: {profile2['priority']}/150")
    print(f"\n💡 豆豆的行动建议: {profile2['recommendation']}")
    if 'stopped_reason' in profile2:
        print(f"停止原因: {profile2['stopped_reason']}")

    # 对比总结
    print(f"\n{'='*100}")
    print(f"对比总结")
    print(f"{'='*100}")
    print(f"geckocustom.com: {profile1['category']} - 优先级 {profile1['priority']}")
    print(f"multicustomize.com: {profile2['category']} - 优先级 {profile2['priority']}")
    print()
    print("关键区别：")
    print(f"- geckocustom.com 还在投放（最后广告：{profile1['days_since_last_ad']}天前）")
    print(f"- multicustomize.com 已停止（最后广告：{profile2['days_since_last_ad']}天前）")
    print()
    print("豆豆的策略：")
    print("✅ multicustomize.com 是金矿！之前投过广告，停止180天+，可以重新激活")
    print("✅ geckocustom.com 是老客户，投放7年+，可以挖掘但优先级较低")

    print(f"\n{'='*100}")
    print(f"使用说明")
    print(f"{'='*100}")
    print("""
1. 使用 MCP Playwright 工具访问 Google Ads Transparency
2. 对每个店铺，记录以下信息：
   - 广告数量（页面上显示的 "~2000 个广告"）
   - 广告主数量（查看有几个不同的广告主）
   - 日期范围（点击"日期范围"筛选器查看最早和最新日期）

3. 使用此脚本添加数据：

   from identify_new_google_ads_customers import NewCustomerIdentifier

   identifier = NewCustomerIdentifier()
   identifier.add_store_data('example.com', {
       'ad_count': 500,
       'advertiser_count': 1,
       'advertisers': ['Company Name'],
       'start_date': '2024-10-01',  # 重要！检查日期筛选器
       'end_date': '2025-12-18',
       'has_ads': True
   })

   # 查看是否为新客户
   is_new = identifier.is_new_customer('example.com', days_threshold=90)
   print(f"是否为新客户（90天内）: {is_new}")

   # 获取完整画像
   profile = identifier.get_customer_profile('example.com')
   print(profile)

4. 生成批量报告：

   profiles = identifier.generate_report()

   # 筛选新客户
   new_customers = [p for p in profiles if p['days_running'] <= 90]
   print(f"找到 {len(new_customers)} 个新客户")
""")

    print(f"\n✅ 数据已保存到: {identifier.cache_file}")


if __name__ == '__main__':
    main()
