# 🚀 Mac mini 快速部署指南

## ✅ 已准备好的文件

`customily_detector.tar.gz` - 包含所有检测脚本和配置

## 📤 步骤 1：传输到 Mac mini

```bash
# 方法 A：使用 SCP（推荐）
scp customily_detector.tar.gz user@macmini.local:~/

# 方法 B：使用 AirDrop
# 在 Finder 中找到文件 -> 右键 -> 共享 -> AirDrop
```

## 🖥️ 步骤 2：在 Mac mini 上运行

### 2.1 SSH 登录

```bash
ssh user@macmini.local
```

### 2.2 解压和配置

```bash
# 解压
tar -xzf customily_detector.tar.gz
cd customily_detector_package

# 安装依赖
pip3 install psycopg2-binary requests beautifulsoup4

# 加载环境变量
source .env
```

### 2.3 运行快速启动脚本

```bash
./quick_start.sh
```

会看到菜单：

```
选择运行模式:
1) 快速测试 - 10个店铺 (1分钟)
2) 小批量测试 - 50个店铺 (4分钟)
3) 中批量测试 - 100个店铺 (8分钟)
4) 高流量店铺 - 51,411个 (3天) ⭐推荐
5) 全部店铺 - 207,712个 (12天)
6) 后台运行 - 高流量店铺

请选择 (1-6):
```

## 🎯 推荐选择

### 首次运行：选择 1 或 2（测试）

验证系统工作正常

### 正式运行：选择 6（后台运行高流量店铺）⭐

```
检测范围：美国 + 中国 + 香港
筛选条件：月访问量 > 10,000
店铺数量：51,411 个
预计时间：3 天
```

## 📊 监控进度

### 查看实时日志

```bash
tail -f customily_check.log
```

### 查看统计

```bash
source .env
python3 check_stats.py
```

### 检查进程

```bash
# 查看进程 ID
cat customily_check.pid

# 检查是否运行
ps aux | grep check_customily
```

## 🛑 停止运行

```bash
# 找到进程 ID
cat customily_check.pid

# 停止进程
kill <PID>
```

## 📈 各版本对比

| 版本 | 店铺数 | 时间 | 说明 |
|------|--------|------|------|
| 快速测试 | 10 | 1分钟 | 验证功能 |
| 小批量 | 50 | 4分钟 | 初步测试 |
| 中批量 | 100 | 8分钟 | 更多样本 |
| **高流量** ⭐ | **51,411** | **3天** | **推荐** |
| 全部 | 207,712 | 12天 | 完整覆盖 |

## 💡 高流量版本优势

- ✅ 覆盖美国、中国、香港三大市场
- ✅ 只检测月访问量 > 10,000 的店铺
- ✅ 时间可控（3天）
- ✅ 覆盖最有价值的客户群
- ✅ 预计找到 1,000+ 个安装 Customily 的店铺

## 🎯 完整命令

```bash
# 1. 传输文件
scp customily_detector.tar.gz user@macmini.local:~/

# 2. SSH 登录
ssh user@macmini.local

# 3. 解压配置
tar -xzf customily_detector.tar.gz
cd customily_detector_package
pip3 install psycopg2-binary requests beautifulsoup4
source .env

# 4. 后台运行（推荐）
./quick_start.sh
# 选择 6

# 5. 断开 SSH（进程继续运行）
exit

# 6. 稍后查看进度
ssh user@macmini.local
cd customily_detector_package
tail -f customily_check.log
```

## 📞 需要帮助？

查看详细文档：
- `MAC_MINI_SETUP.md` - 完整部署指南
- `CUSTOMILY_DETECTION_GUIDE.md` - 使用指南

---

**准备好了！现在就部署到 Mac mini 吧！** 🚀
