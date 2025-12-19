#!/bin/bash

echo "🚀 设置 Vercel 环境变量..."
echo ""

# 从 .env 文件读取数据库 URL
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with POSTGRES_URL"
    exit 1
fi

source .env

if [ -z "$POSTGRES_URL" ]; then
    echo "❌ Error: POSTGRES_URL not set in .env"
    exit 1
fi

echo "📊 设置 POSTGRES_URL..."
echo "$POSTGRES_URL" | vercel env add POSTGRES_URL production

echo "📊 设置 POSTGRES_PRISMA_URL..."
echo "${POSTGRES_URL}&pgbouncer=true" | vercel env add POSTGRES_PRISMA_URL production

echo "📊 设置 POSTGRES_URL_NON_POOLING..."
echo "$POSTGRES_URL" | vercel env add POSTGRES_URL_NON_POOLING production

echo ""
echo "✅ 环境变量设置完成！"
echo "🔄 重新部署..."
echo ""

vercel --prod

echo ""
echo "🎉 部署完成！访问 https://topsales.ecomgrace.com 查看"
