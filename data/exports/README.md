# 店铺数据导出文件

## 📁 文件说明

### stores_us_cn_hk_gt10000_20260225_150644.csv

- **店铺数量**: 51,411 个
- **国家**: 美国 + 中国 + 香港
- **筛选条件**: 月访问量 > 10,000
- **文件大小**: 8.7 MB
- **导出时间**: 2026-02-25

## 🎯 使用方法

### 在另一台电脑上运行检测（离线模式）

```bash
# 1. 克隆或拉取最新代码
git pull

# 2. 安装依赖
pip3 install requests beautifulsoup4

# 3. 运行检测
python3 check_customily_from_csv.py data/exports/stores_us_cn_hk_gt10000_20260225_150644.csv
```

### 优势

- ✅ 不需要数据库连接
- ✅ 适合数据库连接慢的情况
- ✅ 可以在任何电脑上运行
- ✅ 结果保存为 JSON 文件

## 📊 CSV 文件字段

| 字段 | 说明 |
|------|------|
| domain | 店铺域名 |
| country_code | 国家代码 (US/CN/HK) |
| estimated_monthly_visits | 月访问量 |
| city | 城市 |
| state | 州/省 |
| merchant_name | 商家名称 |
| categories | 分类 |
| emails | 邮箱 |
| instagram | Instagram 账号 |
| facebook | Facebook 账号 |
| phones | 电话 |

## 🔄 重新导出数据

如果需要导出最新数据：

```bash
# 连接数据库
source .env

# 运行导出脚本
python3 export_database_to_csv.py

# 选择导出方案
# 1) 高流量店铺 (US+CN+HK, >10k visits) - 推荐
```

## ⏱️ 检测时间估算

- **51,411 个店铺**
- **预计时间**: 3 天（71 小时）
- **平均速度**: 5 秒/店铺
- **预计找到**: 1,000+ 个安装 Customily 的店铺

## 📝 检测结果

检测完成后会生成：

1. `customily_results_final_YYYYMMDD_HHMMSS.json` - 所有结果
2. `customily_stores_YYYYMMDD_HHMMSS.json` - 只包含安装 Customily 的店铺

## 🎯 后续步骤

检测完成后，可以：

1. 将结果 JSON 文件导入回数据库
2. 在 Vercel 网站上查看结果
3. 导出目标客户列表

---

**最后更新**: 2026-02-25
