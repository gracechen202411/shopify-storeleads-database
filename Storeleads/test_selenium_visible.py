#!/usr/bin/env python3
"""
Test Selenium with visible browser
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Test domain
test_domain = "buydecided.com"

print("=" * 80)
print(f"🧪 Testing Selenium with visible browser")
print(f"Domain: {test_domain}")
print("=" * 80)
print()

# Setup Chrome with visible window
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')

print("Starting Chrome browser (visible mode)...")
driver = webdriver.Chrome(options=chrome_options)
print("✅ Browser started - you should see a Chrome window!")
print()

# Navigate to Google Ads Transparency
url = f"https://adstransparency.google.com/?region=anywhere&domain={test_domain}"
print(f"Navigating to: {url}")
driver.get(url)

print("Waiting 5 seconds for page to load...")
time.sleep(5)

# Get page text
page_text = driver.find_element(By.TAG_NAME, 'body').text

print()
print("=" * 80)
print("Page content (first 500 characters):")
print("=" * 80)
print(page_text[:500])
print()

# Check for ads count
import re
if '0 个广告' in page_text or '未找到任何广告' in page_text:
    print("✅ Result: 0 ads (never advertised)")
else:
    match = re.search(r'(\d+)\s*个广告', page_text)
    if match:
        ads_count = int(match.group(1))
        print(f"✅ Result: {ads_count} ads found")
    else:
        print("❓ Could not determine ads count")

print()
print("Keeping browser open for 10 seconds so you can see it...")
time.sleep(10)

print("Closing browser...")
driver.quit()
print("✅ Done!")
