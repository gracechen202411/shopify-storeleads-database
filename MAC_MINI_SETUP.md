# Mac mini 部署指南 - Customily 检测系统

## 📋 准备工作

### 1. 文件传输到 Mac mini

```bash
# 在当前 Mac 上，打包需要的文件
tar -czf customily_detector.tar.gz \
  check_customily_test100.py \
  check_customily_app.py \
  check_customily_selenium.py \
  test_customily_detection.py \
  .env \
  CUSTOMILY_*.md

# 传输到 Mac mini（替换为你的 Mac mini IP 或主机名）
scp customily_detector.tar.gz user@macmini.local:~/

# 或者使用 AirDrop / 共享文件夹
```

### 2. 在 Mac mini 上解压

```bash
# SSH 登录到 Mac mini
ssh user@macmini.local

# 创建工作目录
mkdir -p ~/customily_detector
cd ~/customily_detector

# 解压文件
tar -xzf ~/customily_detector.tar.gz

# 或者直接 git clone（如果代码在 git 仓库）
# git clone <your-repo-url>
# cd <repo-name>
```

## 🔧 环境配置

### 1. 检查 Python 版本

```bash
python3 --version
# 需要 Python 3.7+
```

### 2. 安装依赖

```bash
# 安装 Python 包
pip3 install psycopg2-binary requests beautifulsoup4

# 如果需要 Selenium（可选）
pip3 install selenium
brew install chromedriver
```

### 3. 配置环境变量

```bash
# 编辑 .env 文件
nano .env

# 确保包含数据库连接信息：
# DATABASE_URL="postgresql://user:password@host/database"
# 或
# POSTGRES_URL_NON_POOLING="postgresql://user:password@host/database"

# 加载环境变量
source .env

# 验证
echo $DATABASE_URL
```

## 🧪 测试运行（方案1）

### 步骤 1：测试连接

```bash
# 测试数据库连接
python3 -c "
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL_NON_POOLING')

if not DATABASE_URL:
    print('❌ DATABASE_URL not found')
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

### 步骤 2：运行测试版（100个店铺，4分钟）

```bash
# 运行测试版
python3 check_customily_test100.py

# 输出示例：
# 🧪 Customily 检测 - 测试版（前100个店铺）
# ✅ Database connected
# ✅ Found 100 stores to check
# ⏱️  Estimated time: ~4 minutes
# ▶️  Start checking? (y/n): y
```

### 步骤 3：查看结果

```bash
# 在数据库中查询结果
python3 -c "
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL_NON_POOLING')
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute('''
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN has_customily THEN 1 ELSE 0 END) as with_customily,
        SUM(CASE WHEN has_customily = false THEN 1 ELSE 0 END) as without_customily
    FROM stores
    WHERE customily_check_date IS NOT NULL
''')

total, with_c, without_c = cur.fetchone()
print(f'总检测: {total}')
print(f'安装 Customily: {with_c} ({with_c/total*100:.1f}%)')
print(f'未安装: {without_c} ({without_c/total*100:.1f}%)')

cur.close()
conn.close()
"
```

## 🚀 全量运行

### 如果测试结果正常，运行全量检测

#### 方法 1：前台运行（可以看到实时进度）

```bash
# 直接运行
python3 check_customily_app.py

# 预计时间：4-5 小时
# 可以随时按 Ctrl+C 中断，下次会继续
```

#### 方法 2：后台运行（推荐）

```bash
# 后台运行，输出到日志文件
nohup python3 check_customily_app.py > customily_check.log 2>&1 &

# 记录进程 ID
echo $! > customily_check.pid

# 查看实时日志
tail -f customily_check.log

# 查看进度（另开一个终端）
grep "Progress:" customily_check.log | tail -5

# 检查是否还在运行
ps aux | grep check_customily_app.py
```

#### 方法 3：使用 screen（可以断开 SSH）

```bash
# 安装 screen（如果没有）
brew install screen

# 创建新 screen 会话
screen -S customily

# 在 screen 中运行
source .env
python3 check_customily_app.py

# 断开 screen：按 Ctrl+A 然后按 D

# 重新连接
screen -r customily

# 查看所有 screen 会话
screen -ls
```

## 📊 监控进度

### 实时查看进度

```bash
# 方法 1：查看日志文件
tail -f customily_check.log

# 方法 2：查看数据库
watch -n 10 'python3 -c "
import os, psycopg2
conn = psycopg2.connect(os.environ.get(\"DATABASE_URL\"))
cur = conn.cursor()
cur.execute(\"SELECT COUNT(*) FROM stores WHERE customily_check_date IS NOT NULL\")
print(f\"已检测: {cur.fetchone()[0]} 个店铺\")
cur.close()
conn.close()
"'
```

### 查看统计

```bash
# 创建查询脚本
cat > check_stats.py << 'EOF'
#!/usr/bin/env python3
import os
import psycopg2
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL_NON_POOLING')
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# 总体统计
cur.execute('''
    SELECT 
        COUNT(*) as total_checked,
        SUM(CASE WHEN has_customily THEN 1 ELSE 0 END) as with_customily,
        SUM(CASE WHEN has_customily = false THEN 1 ELSE 0 END) as without_customily,
        MAX(customily_check_date) as last_check
    FROM stores
    WHERE customily_check_date IS NOT NULL
''')

total, with_c, without_c, last_check = cur.fetchone()

print("="*60)
print("Customily 检测统计")
print("="*60)
print(f"总检测数: {total}")
print(f"安装 Customily: {with_c} ({with_c/total*100:.1f}%)")
print(f"未安装: {without_c} ({without_c/total*100:.1f}%)")
print(f"最后检测: {last_check}")
print("="*60)

# 按国家统计
cur.execute('''
    SELECT 
        country_code,
        COUNT(*) as total,
        SUM(CASE WHEN has_customily THEN 1 ELSE 0 END) as with_customily
    FROM stores
    WHERE customily_check_date IS NOT NULL
    GROUP BY country_code
    ORDER BY total DESC
''')

print("\n按国家统计:")
for country, total, with_c in cur.fetchall():
    print(f"  {country}: {total} 个 (Customily: {with_c})")

cur.close()
conn.close()
EOF

chmod +x check_stats.py

# 运行统计
python3 check_stats.py
```

## 🛑 停止和恢复

### 停止检测

```bash
# 如果是前台运行：按 Ctrl+C

# 如果是后台运行：
# 1. 找到进程 ID
cat customily_check.pid
# 或
ps aux | grep check_customily_app.py

# 2. 终止进程
kill <PID>

# 进度会自动保存，下次运行会继续
```

### 恢复检测

```bash
# 直接再次运行，会自动跳过已检测的店铺
python3 check_customily_app.py
```

## 📁 文件说明

```
~/customily_detector/
├── check_customily_test100.py    # 测试版（100个店铺）
├── check_customily_app.py        # 完整版（全部店铺）
├── check_customily_selenium.py   # Selenium 版（更精确）
├── test_customily_detection.py   # 功能测试
├── check_stats.py                # 统计脚本
├── .env                          # 环境变量
├── customily_check.log           # 运行日志
└── customily_check.pid           # 进程 ID
```

## ⚠️ 注意事项

1. **网络稳定性**：确保 Mac mini 网络稳定
2. **不要休眠**：设置 Mac mini 不要自动休眠
   ```bash
   # 防止休眠
   caffeinate -i python3 check_customily_app.py
   ```
3. **定期检查**：每小时检查一次进度
4. **备份日志**：保存日志文件以便排查问题

## 🎯 完整工作流程

```bash
# 1. 传输文件到 Mac mini
scp customily_detector.tar.gz user@macmini.local:~/

# 2. SSH 登录
ssh user@macmini.local

# 3. 解压和配置
cd ~/customily_detector
tar -xzf ~/customily_detector.tar.gz
source .env

# 4. 测试运行（100个店铺，4分钟）
python3 check_customily_test100.py

# 5. 查看测试结果
python3 check_stats.py

# 6. 如果正常，后台运行全量检测
nohup python3 check_customily_app.py > customily_check.log 2>&1 &
echo $! > customily_check.pid

# 7. 断开 SSH，让它继续运行
exit

# 8. 稍后重新连接查看进度
ssh user@macmini.local
cd ~/customily_detector
tail -f customily_check.log
```

## 📞 故障排除

### 问题 1：数据库连接失败

```bash
# 检查环境变量
echo $DATABASE_URL

# 测试连接
python3 -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

### 问题 2：进程意外停止

```bash
# 查看日志
tail -100 customily_check.log

# 重新运行（会自动继续）
python3 check_customily_app.py
```

### 问题 3：Mac mini 休眠

```bash
# 使用 caffeinate 防止休眠
caffeinate -i python3 check_customily_app.py
```

---

**准备好了吗？开始部署！** 🚀
