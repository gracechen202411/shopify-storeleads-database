# 谷歌广告客户识别系统

自动识别浙江省 Shopify 店铺中从未打广告或30天内新打广告的潜在客户。

## 🎯 最终结果

- **120个目标客户**（浙江省 + 月访问量 ≥1000）
- **总访问量**：1,771,567/月
- **分类**：118个从未打广告 + 2个30天新广告主

## 📂 文件说明

### 生产环境（使用这些）

```
stage1_fast_check_selenium.py    # Stage 1：快速筛选（有/无广告）
stage2_date_check_selenium.py    # Stage 2：日期验证（30天新/老）
verify_local_parallel.py         # 并行验证（10进程）
sync_to_local.py                 # 同步 Neon → SQLite
sync_to_neon.py                  # 同步 SQLite → Neon
local_stores.db                  # 本地SQLite数据库
```

### 归档目录

```
archive/                         # 旧代码（已废弃）
```

## 🚀 快速开始

### 1. 同步数据到本地

```bash
python3 sync_to_local.py
```

### 2. 验证店铺（可选）

```bash
python3 verify_local_parallel.py
```

### 3. 同步回 Neon

```bash
python3 sync_to_neon.py
```

## 📋 详细文档

完整流程和技术细节请查看：[谷歌广告客户识别系统文档.md](谷歌广告客户识别系统文档.md)

## 🔑 关键技术

- **并行处理**：10个进程同时验证
- **本地缓存**：SQLite避免Neon连接限制
- **智能检测**：
  - 自动去除www前缀
  - 动态内容等待（WebDriverWait）
  - 日期范围查询（累计而非单日）

## 📊 客户类型

| 类型 | 说明 | 数量 |
|-----|------|------|
| `never_advertised` | ✅ 从未打广告 | 118个 |
| `new_advertiser_30d` | ✅ 30天新广告主 | 2个 |
| `old_advertiser` | 老广告主 | 79个 |
| `has_ads` | 有广告但未验证日期 | 29个 |

## 🛠️ 环境要求

```bash
pip3 install psycopg2 selenium
```

---

**最后更新**：2025-12-20
