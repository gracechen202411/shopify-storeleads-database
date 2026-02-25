#!/bin/bash

# Customily 检测快速启动脚本

echo "=================================="
echo "Customily Detection Quick Start"
echo "=================================="
echo ""

# 检查环境变量
if [ -z "$DATABASE_URL" ] && [ -z "$POSTGRES_URL_NON_POOLING" ]; then
    echo "❌ Database URL not found!"
    echo ""
    echo "Please run: source .env"
    echo ""
    exit 1
fi

echo "✅ Database URL found"
echo ""

# 检查 Python 依赖
echo "Checking Python dependencies..."

if ! python3 -c "import psycopg2" 2>/dev/null; then
    echo "❌ psycopg2 not installed"
    echo "Run: pip3 install psycopg2-binary"
    exit 1
fi

if ! python3 -c "import requests" 2>/dev/null; then
    echo "❌ requests not installed"
    echo "Run: pip3 install requests"
    exit 1
fi

echo "✅ Dependencies OK"
echo ""

# 选择检测模式
echo "Select detection mode:"
echo "1) Quick mode (requests) - Fast, ~85% accuracy"
echo "2) Selenium mode - Slower, ~95% accuracy"
echo "3) Test mode - Test with 3 sample stores"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Starting quick mode..."
        python3 check_customily_app.py
        ;;
    2)
        # 检查 Selenium
        if ! python3 -c "import selenium" 2>/dev/null; then
            echo "❌ selenium not installed"
            echo "Run: pip3 install selenium"
            exit 1
        fi
        
        if ! command -v chromedriver &> /dev/null; then
            echo "❌ chromedriver not found"
            echo "Run: brew install chromedriver"
            exit 1
        fi
        
        echo ""
        echo "Starting Selenium mode..."
        python3 check_customily_selenium.py
        ;;
    3)
        echo ""
        echo "Starting test mode..."
        python3 test_customily_detection.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=================================="
echo "Done!"
echo "=================================="
