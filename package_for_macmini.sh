#!/bin/bash

# 打包 Customily 检测系统到 Mac mini

echo "=================================="
echo "📦 打包 Customily 检测系统"
echo "=================================="

# 创建临时目录
TEMP_DIR="customily_detector_package"
rm -rf $TEMP_DIR
mkdir -p $TEMP_DIR

echo ""
echo "📋 复制文件..."

# 复制核心脚本
cp check_customily_test100.py $TEMP_DIR/
cp check_customily_test50.py $TEMP_DIR/
cp check_customily_test10_auto.py $TEMP_DIR/
cp check_customily_app.py $TEMP_DIR/
cp check_customily_high_traffic.py $TEMP_DIR/
cp check_customily_selenium.py $TEMP_DIR/
cp test_customily_detection.py $TEMP_DIR/

# 复制文档
cp CUSTOMILY_README.md $TEMP_DIR/
cp CUSTOMILY_DETECTION_GUIDE.md $TEMP_DIR/
cp CUSTOMILY_SUMMARY.md $TEMP_DIR/
cp MAC_MINI_SETUP.md $TEMP_DIR/

# 复制环境变量文件
if [ -f .env ]; then
    cp .env $TEMP_DIR/
    echo "✅ .env 文件已复制"
else
    echo "⚠️  .env 文件不存在，请手动创建"
    cat > $TEMP_DIR/.env << 'EOF'
# 数据库连接配置
# 请填写你的 Neon 数据库连接信息

DATABASE_URL="postgresql://user:password@host/database"
# 或
POSTGRES_URL_NON_POOLING="postgresql://user:password@host/database"
EOF
fi

# 创建快速启动脚本
cat > $TEMP_DIR/quick_start.sh << 'EOF'
#!/bin/bash

echo "=================================="
echo "🚀 Customily 检测快速启动"
echo "=================================="

# 检查环境变量
if [ -z "$DATABASE_URL" ] && [ -z "$POSTGRES_URL_NON_POOLING" ]; then
    echo ""
    echo "⚠️  环境变量未设置"
    echo "运行: source .env"
    echo ""
    exit 1
fi

echo ""
echo "选择运行模式:"
echo "1) 快速测试 - 10个店铺 (1分钟)"
echo "2) 小批量测试 - 50个店铺 (4分钟)"
echo "3) 中批量测试 - 100个店铺 (8分钟)"
echo "4) 高流量店铺 - 51,411个 (3天) ⭐推荐"
echo "5) 全部店铺 - 207,712个 (12天)"
echo "6) 后台运行 - 高流量店铺"
echo ""
read -p "请选择 (1-6): " choice

case $choice in
    1)
        echo ""
        echo "🧪 启动快速测试..."
        python3 check_customily_test10_auto.py
        ;;
    2)
        echo ""
        echo "🧪 启动小批量测试..."
        python3 check_customily_test50.py
        ;;
    3)
        echo ""
        echo "🧪 启动中批量测试..."
        python3 check_customily_test100.py
        ;;
    4)
        echo ""
        echo "🎯 启动高流量店铺检测..."
        python3 check_customily_high_traffic.py
        ;;
    5)
        echo ""
        echo "🚀 启动全部店铺检测..."
        python3 check_customily_app.py
        ;;
    6)
        echo ""
        echo "🚀 后台运行高流量店铺检测..."
        nohup python3 check_customily_high_traffic.py > customily_check.log 2>&1 &
        echo $! > customily_check.pid
        echo "✅ 已在后台启动"
        echo "查看日志: tail -f customily_check.log"
        echo "进程 ID: $(cat customily_check.pid)"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac
EOF

chmod +x $TEMP_DIR/quick_start.sh

# 创建统计脚本
cat > $TEMP_DIR/check_stats.py << 'EOF'
#!/usr/bin/env python3
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL_NON_POOLING')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found")
    exit(1)

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

result = cur.fetchone()
if result[0] == 0:
    print("⚠️  还没有检测数据")
    exit(0)

total, with_c, without_c, last_check = result

print("="*60)
print("📊 Customily 检测统计")
print("="*60)
print(f"总检测数: {total:,}")
print(f"安装 Customily: {with_c:,} ({with_c/total*100:.1f}%)")
print(f"未安装: {without_c:,} ({without_c/total*100:.1f}%)")
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
    LIMIT 10
''')

print("\n按国家统计:")
for country, total, with_c in cur.fetchall():
    print(f"  {country}: {total:,} 个 (Customily: {with_c:,})")

cur.close()
conn.close()
EOF

chmod +x $TEMP_DIR/check_stats.py

# 创建 README
cat > $TEMP_DIR/README.txt << 'EOF'
Customily 检测系统 - Mac mini 版本

快速开始：
1. source .env
2. ./quick_start.sh

详细说明请查看：MAC_MINI_SETUP.md
EOF

echo "✅ 文件复制完成"

# 打包
echo ""
echo "📦 打包中..."
tar -czf customily_detector.tar.gz $TEMP_DIR/

echo "✅ 打包完成: customily_detector.tar.gz"

# 显示文件列表
echo ""
echo "📋 包含的文件:"
tar -tzf customily_detector.tar.gz | sed 's/^/  /'

# 清理临时目录
rm -rf $TEMP_DIR

echo ""
echo "=================================="
echo "✅ 打包完成！"
echo "=================================="
echo ""
echo "📤 传输到 Mac mini:"
echo "  scp customily_detector.tar.gz user@macmini.local:~/"
echo ""
echo "📥 在 Mac mini 上解压:"
echo "  tar -xzf customily_detector.tar.gz"
echo "  cd customily_detector_package"
echo "  source .env"
echo "  ./quick_start.sh"
echo ""
echo "📖 详细说明: MAC_MINI_SETUP.md"
echo "=================================="
