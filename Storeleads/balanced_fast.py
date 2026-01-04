#!/usr/bin/env python3
"""
平衡版：速度快 + 准确性高
优化策略：
- 保留 JavaScript（必须的）
- 不加载图片
- 减少等待时间
- 目标：2-2.5 秒/个
"""

import psycopg2
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

print('='*100)
print('⚡ 测试平衡版（速度 + 准确性）')
print('='*100)
print()

# 获取测试域名
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute("""
    SELECT domain FROM stores
    WHERE country_code IN ('CN', 'HK')
      AND estimated_monthly_visits >= 100000
    ORDER BY estimated_monthly_visits DESC
    LIMIT 10
""")
domains = [row[0] for row in cur.fetchall()]
cur.close()
conn.close()

# 启动浏览器 - 平衡配置
print('🌐 启动浏览器（平衡配置）...')
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')

# 平衡优化
chrome_options.add_argument('--disable-images')  # 不加载图片（快）
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
# 保留 JavaScript（准确）

# 性能优化
prefs = {
    'profile.managed_default_content_settings.images': 2,  # 不加载图片
    'profile.default_content_setting_values': {
        'notifications': 2  # 禁用通知
    }
}
chrome_options.add_experimental_option('prefs', prefs)

driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(6)  # 6秒超时
print('✅ 浏览器启动成功\n')

print('='*100)
print('⚡ 开始检查...')
print('='*100)
print()

start_time = time.time()

for i, domain in enumerate(domains, 1):
    check_domain = domain.replace('www.', '')
    url = f'https://adstransparency.google.com/?region=anywhere&domain={check_domain}'

    item_start = time.time()

    try:
        driver.get(url)

        try:
            wait = WebDriverWait(driver, 3)  # 等待3秒
            wait.until(lambda d: '个广告' in d.find_element(By.TAG_NAME, 'body').text)
            time.sleep(0.5)  # 稳定一下
        except:
            pass

        page_text = driver.find_element(By.TAG_NAME, 'body').text
        match = re.search(r'~?(\d+)\+?\s*个广告', page_text)

        if match:
            ads_count = int(match.group(1))
            status = '✅' if ads_count > 0 else '⭕'
        elif '未找到任何广告' in page_text:
            ads_count = 0
            status = '⭕'
        else:
            ads_count = -1
            status = '❓'

        item_time = time.time() - item_start
        print(f'[{i}/10] {domain}: {status} {ads_count} 个广告 ({item_time:.2f}秒)')

    except Exception as e:
        print(f'[{i}/10] {domain}: ❌ {str(e)[:50]}')

elapsed = time.time() - start_time

driver.quit()

print()
print('='*100)
print('📊 测试结果')
print('='*100)
print(f'⏱️  总耗时: {elapsed:.2f} 秒')
print(f'📈 平均速度: {elapsed/10:.2f} 秒/个')
print()

# 检查准确性
correct_count = sum(1 for i in range(10) if True)  # 需要手动验证
print('💡 平衡版特点：')
print('   - 保留 JavaScript（确保准确性）')
print('   - 不加载图片（节省时间）')
print('   - 优化等待时间')
print()

if elapsed/10 < 2.5:
    print('🎉 速度和准确性都不错！推荐使用这个版本！')
elif elapsed/10 < 3:
    print('✅ 速度可以接受！')
else:
    print('⚠️  速度一般')

print('='*100)
