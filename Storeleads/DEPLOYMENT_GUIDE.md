# Google Ads Checker 部署运行指南

**适用场景：**在其他电脑上运行此脚本，加速数据检查（多台电脑并行）

---

## 📋 系统要求

### 硬件要求
- **内存**：至少 2GB 可用内存
- **磁盘**：至少 1GB 可用空间
- **网络**：稳定的互联网连接

### 支持的操作系统
- ✅ macOS (已测试)
- ✅ Windows 10/11
- ✅ Linux (Ubuntu/Debian/CentOS)

---

## 🚀 快速开始（5分钟部署）

### 步骤 1: 克隆代码仓库

```bash
# 克隆 GitHub 仓库
git clone https://github.com/gracechen202411/shopify-storeleads-database.git
cd shopify-storeleads-database/Storeleads
```

### 步骤 2: 安装 Python 3

**macOS:**
```bash
# 检查是否已安装
python3 --version

# 如果未安装，使用 Homebrew
brew install python3
```

**Windows:**
1. 下载 Python 3.12+ 安装包：https://www.python.org/downloads/
2. 安装时勾选 "Add Python to PATH"
3. 打开命令提示符，运行 `python --version` 验证

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 步骤 3: 安装依赖

```bash
# 安装 Python 依赖
pip3 install psycopg2-binary selenium

# 安装 Chrome 浏览器（如果未安装）
# macOS: 已有 Chrome 即可
# Windows: 下载安装 https://www.google.com/chrome/
# Linux:
sudo apt install google-chrome-stable

# 安装 ChromeDriver（Selenium 会自动管理，无需手动）
```

### 步骤 4: 验证安装

```bash
# 验证 Python
python3 --version  # 应显示 3.8+

# 验证依赖
python3 -c "import psycopg2; import selenium; print('✅ 依赖安装成功')"

# 验证 Chrome
google-chrome --version  # 或在 macOS/Windows 打开 Chrome 查看版本
```

### 步骤 5: 运行测试

```bash
# 测试 10 条记录（约 1 分钟）
python3 production_optimized.py --limit=10
```

如果看到类似输出，说明配置成功：
```
✅ [1/10] example.com | 无广告 | 3.2s
✅ [2/10] shop.com    | -1 ads | 2.8s
...
✅ 检查完成！
```

---

## 📖 详细使用说明

### 运行模式

#### 1. 正常模式（检查未检查的店铺）
```bash
# 检查所有未检查的店铺（默认模式）
python3 production_optimized.py

# 限制检查数量（测试用）
python3 production_optimized.py --limit=100
```

#### 2. 重新检查模式（重新检查已检查的店铺）
```bash
# 重新检查所有已检查的店铺
python3 production_optimized.py --recheck

# 重新检查指定数量
python3 production_optimized.py --recheck --limit=500
```

### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--limit=N` | 限制检查数量 | `--limit=1000` |
| `--recheck` | 重新检查已检查的记录 | `--recheck` |

---

## 🔧 数据库配置说明

**重要：** 所有电脑使用同一个 Neon 数据库，自动去重！

### 数据库信息（已在代码中配置）
```python
DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}
```

**无需修改配置** - 代码已包含数据库连接信息

### 去重机制
- ✅ **自动去重**：多台电脑运行时，已检查的域名自动跳过
- ✅ **实时同步**：每 20 条记录提交一次到数据库
- ✅ **进度保存**：本地保存进度，断点续传

---

## 💻 多台电脑并行运行

### 推荐配置

**场景 1: 2 台电脑**
- **电脑 A**: 运行 `python3 production_optimized.py`
- **电脑 B**: 运行 `python3 production_optimized.py`
- **预计耗时**: 9.6天 ÷ 2 = **4.8天**

**场景 2: 3 台电脑**
- **电脑 A**: 运行 `python3 production_optimized.py`
- **电脑 B**: 运行 `python3 production_optimized.py`
- **电脑 C**: 运行 `python3 production_optimized.py`
- **预计耗时**: 9.6天 ÷ 3 = **3.2天**

### 工作原理
1. 每台电脑从数据库读取**未检查**的店铺
2. 由于读取顺序是 `ORDER BY estimated_monthly_visits DESC`，每台电脑会拿到不同的店铺
3. 每 20 条记录提交一次，其他电脑会跳过已提交的
4. **自动去重**，无需手动协调

### 注意事项
⚠️ **不要在同一台电脑开多个进程** - 会重复检查，浪费资源

---

## 📊 进度监控

### 查看实时进度

**macOS/Linux:**
```bash
# 实时查看输出
tail -f nohup.out

# 或者直接运行（不使用后台）
python3 production_optimized.py
```

**Windows:**
```cmd
# 直接运行查看进度
python production_optimized.py
```

### 查看数据库进度

```bash
# 登录数据库查看进度
python3 << 'EOF'
import psycopg2

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# 总数统计
cur.execute("SELECT COUNT(*) FROM stores")
total = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM stores WHERE customer_type IS NOT NULL AND customer_type != ''")
checked = cur.fetchone()[0]

print(f"总店铺数: {total:,}")
print(f"已检查: {checked:,}")
print(f"未检查: {total - checked:,}")
print(f"进度: {checked/total*100:.2f}%")

cur.close()
conn.close()
EOF
```

---

## 🔄 后台运行（推荐）

### macOS/Linux

```bash
# 后台运行，输出到 nohup.out
nohup python3 production_optimized.py > checker.log 2>&1 &

# 查看进程
ps aux | grep production_optimized

# 查看日志
tail -f checker.log

# 停止运行
pkill -f production_optimized.py
```

### Windows

**方法 1: 使用 PowerShell**
```powershell
Start-Process python -ArgumentList "production_optimized.py" -RedirectStandardOutput "checker.log" -WindowStyle Hidden
```

**方法 2: 使用任务计划程序**
1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器选择"启动时"
4. 操作选择运行 Python 脚本

---

## ⚡ 性能优化建议

### 1. 使用高性能网络
- ✅ 有线网络优于 Wi-Fi
- ✅ 稳定网络比快速网络更重要

### 2. 保持电脑运行
- ✅ 禁用睡眠模式
- ✅ 关闭屏幕保护程序
- ✅ 连接电源适配器

**macOS:**
```bash
# 禁用睡眠（运行期间）
caffeinate -i python3 production_optimized.py
```

**Windows:**
系统设置 → 电源 → 从不进入睡眠

### 3. 监控资源使用

**内存使用：** 约 500MB-1GB
**CPU 使用：** 约 10-30%
**网络：** 约 1-5 Mbps

---

## 🛠️ 故障排除

### 问题 1: 数据库连接失败
```
psycopg2.OperationalError: could not connect to server
```

**解决方案:**
1. 检查网络连接
2. 确认防火墙没有阻止 PostgreSQL (端口 5432)
3. 验证数据库凭据

### 问题 2: ChromeDriver 错误
```
selenium.common.exceptions.WebDriverException
```

**解决方案:**
```bash
# 重新安装 Selenium
pip3 uninstall selenium
pip3 install selenium

# 确认 Chrome 已安装
google-chrome --version
```

### 问题 3: 速度太慢
```
平均速度: 10s/域名
```

**解决方案:**
1. 检查网络速度：https://fast.com
2. 重启脚本
3. 更换网络环境

### 问题 4: 进程意外停止

**解决方案:**
- ✅ 脚本有**断点续传**功能
- ✅ 直接重新运行即可：`python3 production_optimized.py`
- ✅ 会自动跳过已检查的店铺

---

## 📈 预期结果

### 单台电脑
- **总店铺**: 207,712
- **平均速度**: 4.0s/domain
- **总耗时**: 9.6天
- **每小时检查**: ~900 店铺

### 多台电脑（推荐）
| 电脑数量 | 总耗时 | 每日检查量 |
|---------|--------|-----------|
| 1台 | 9.6天 | 21,636 |
| 2台 | 4.8天 | 43,272 |
| 3台 | 3.2天 | 64,908 |
| 5台 | 1.9天 | 108,180 |

---

## 📝 示例：完整运行流程

### 第一台电脑（macOS）
```bash
# 1. 克隆代码
git clone https://github.com/gracechen202411/shopify-storeleads-database.git
cd shopify-storeleads-database/Storeleads

# 2. 安装依赖
pip3 install psycopg2-binary selenium

# 3. 测试运行
python3 production_optimized.py --limit=10

# 4. 后台运行全量检查
nohup python3 production_optimized.py > checker_mac.log 2>&1 &

# 5. 查看进度
tail -f checker_mac.log
```

### 第二台电脑（Windows）
```cmd
# 1. 克隆代码
git clone https://github.com/gracechen202411/shopify-storeleads-database.git
cd shopify-storeleads-database\Storeleads

# 2. 安装依赖
pip install psycopg2-binary selenium

# 3. 测试运行
python production_optimized.py --limit=10

# 4. 直接运行（或使用任务计划程序）
python production_optimized.py
```

---

## 🎯 最佳实践

### ✅ 推荐做法
1. **先测试小批量**：`--limit=100` 确认配置正确
2. **后台运行**：使用 `nohup` 或任务计划程序
3. **定期检查进度**：每天查看一次数据库统计
4. **保持电脑运行**：禁用睡眠，连接电源

### ❌ 不推荐做法
1. ❌ 同一台电脑开多个进程
2. ❌ 频繁停止/启动（影响效率）
3. ❌ 修改数据库配置
4. ❌ 使用不稳定的网络（如移动热点）

---

## 🆘 需要帮助？

### 快速检查清单
- [ ] Python 3.8+ 已安装
- [ ] 依赖包已安装（psycopg2-binary, selenium）
- [ ] Chrome 浏览器已安装
- [ ] 网络连接正常
- [ ] 测试运行成功（`--limit=10`）

### 常见问题速查

| 错误信息 | 解决方案 |
|---------|---------|
| `ModuleNotFoundError: No module named 'psycopg2'` | `pip3 install psycopg2-binary` |
| `ModuleNotFoundError: No module named 'selenium'` | `pip3 install selenium` |
| `chrome not reachable` | 安装 Chrome 浏览器 |
| `Connection refused` | 检查网络和防火墙 |
| `value too long for type character varying(20)` | 使用最新代码（已修复）|

---

## 📊 监控仪表板

运行后，可以通过 SQL 查看实时统计：

```sql
-- 总体进度
SELECT
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE customer_type IS NOT NULL) as checked,
    COUNT(*) FILTER (WHERE customer_type = 'has_ads') as has_ads,
    COUNT(*) FILTER (WHERE customer_type = 'never_advertised') as never_advertised
FROM stores;

-- 今天的检查量
SELECT COUNT(*)
FROM stores
WHERE ads_last_checked::date = CURRENT_DATE;

-- 不同电脑的检查量（通过 ads_check_level）
SELECT ads_check_level, COUNT(*)
FROM stores
WHERE ads_last_checked IS NOT NULL
GROUP BY ads_check_level;
```

---

## 🎉 完成后

检查完成后，你可以：
1. 在前端使用筛选功能：**有广告** vs **无广告（潜在客户）**
2. 导出 CSV 进行深度分析
3. 查看 Google Ads Transparency Center 链接

**前端地址：** https://你的-vercel-域名.vercel.app

**筛选功能：**
- 📊 有广告：正在投放 Google 广告的店铺
- 💎 无广告（潜在客户）：从未投放广告，可以开发的新客户

---

**祝运行顺利！有问题随时问我 🚀**
