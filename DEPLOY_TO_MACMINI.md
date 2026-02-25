# 🚀 部署到 Mac mini - 3步完成

## 📦 步骤 1：打包（当前 Mac）

```bash
# 已完成！文件已打包为：
customily_detector.tar.gz
```

## 📤 步骤 2：传输到 Mac mini

### 方法 A：使用 SCP（推荐）

```bash
# 替换 user 和 macmini.local 为你的实际信息
scp customily_detector.tar.gz user@macmini.local:~/
```

### 方法 B：使用 AirDrop

1. 在 Finder 中找到 `customily_detector.tar.gz`
2. 右键 -> 共享 -> AirDrop
3. 选择你的 Mac mini

### 方法 C：使用共享文件夹

1. 将文件复制到共享文件夹
2. 在 Mac mini 上访问共享文件夹

## 🖥️ 步骤 3：在 Mac mini 上运行

### 3.1 SSH 登录到 Mac mini

```bash
ssh user@macmini.local
# 或使用 IP 地址
ssh user@192.168.1.xxx
```

### 3.2 解压和配置

```bash
# 解压文件
tar -xzf customily_detector.tar.gz
cd customily_detector_package

# 查看文件
ls -la

# 加载环境变量
source .env

# 验证数据库连接
python3 -c "import os; print('✅ DATABASE_URL:', os.environ.get('DATABASE_URL')[:50])"
```

### 3.3 运行测试版（方案1）

```bash
# 方法 1：使用快速启动脚本
./quick_start.sh
# 选择 1 (测试版 - 100个店铺)

# 方法 2：直接运行
python3 check_customily_test100.py
```

## ⏱️ 预期结果

### 测试版（100个店铺）

```
🧪 Customily 检测 - 测试版（前100个店铺）
✅ Database connected
✅ Found 100 stores to check

📋 First 5 stores:
  1. nothing.tech (HK) - 1,508,985 visits/month
  2. lingsmoment.com (HK) - 912,710 visits/month
  ...

⏱️  Estimated time: ~4 minutes
▶️  Start checking? (y/n): y

[1/100] nothing.tech (HK, 1,508,985 visits)... ⭕ No Customily
[2/100] lingsmoment.com (HK, 912,710 visits)... ⭕ No Customily
...

✅ 检测完成！
📊 统计结果:
  • 总检测数: 100
  • 安装 Customily: 5 (5.0%)
  • 未安装: 95 (95.0%)
⏱️  总耗时: 4分 12秒
```

## 📊 查看结果

```bash
# 查看统计
python3 check_stats.py

# 输出：
# 📊 Customily 检测统计
# 总检测数: 100
# 安装 Customily: 5 (5.0%)
# 未安装: 95 (95.0%)
```

## 🚀 如果测试正常，运行全量检测

### 方法 1：后台运行（推荐）

```bash
# 后台运行
nohup python3 check_customily_app.py > customily_check.log 2>&1 &

# 记录进程 ID
echo $! > customily_check.pid

# 查看日志
tail -f customily_check.log

# 断开 SSH（进程继续运行）
exit
```

### 方法 2：使用 screen

```bash
# 创建 screen 会话
screen -S customily

# 运行检测
source .env
python3 check_customily_app.py

# 断开 screen：Ctrl+A 然后 D

# 稍后重新连接
screen -r customily
```

## 📱 监控进度

### 重新连接查看

```bash
# SSH 登录
ssh user@macmini.local

# 进入目录
cd customily_detector_package

# 查看日志
tail -f customily_check.log

# 查看统计
source .env
python3 check_stats.py
```

## ✅ 完整命令总结

```bash
# === 在当前 Mac 上 ===
# 1. 传输文件
scp customily_detector.tar.gz user@macmini.local:~/

# === 在 Mac mini 上 ===
# 2. 解压
tar -xzf customily_detector.tar.gz
cd customily_detector_package

# 3. 测试运行
source .env
./quick_start.sh
# 选择 1

# 4. 如果正常，后台运行全量
nohup python3 check_customily_app.py > customily_check.log 2>&1 &
echo $! > customily_check.pid

# 5. 断开 SSH
exit

# 6. 稍后查看进度
ssh user@macmini.local
cd customily_detector_package
tail -f customily_check.log
```

## 🎯 时间线

| 时间 | 操作 |
|------|------|
| 0:00 | 传输文件到 Mac mini (1分钟) |
| 0:01 | 解压和配置 (1分钟) |
| 0:02 | 运行测试版 (4分钟) |
| 0:06 | 查看结果，确认正常 (1分钟) |
| 0:07 | 启动全量检测 (1分钟) |
| 0:08 | 断开 SSH，让它跑 |
| 4:00 | 4小时后检查进度 |
| 5:00 | 完成！查看最终结果 |

## 📞 需要帮助？

查看详细文档：
- `MAC_MINI_SETUP.md` - 完整部署指南
- `CUSTOMILY_DETECTION_GUIDE.md` - 使用指南
- `CUSTOMILY_README.md` - 项目说明

---

**准备好了吗？开始部署！** 🚀
