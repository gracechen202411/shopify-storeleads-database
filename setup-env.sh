#!/bin/bash

echo "🚀 设置 Vercel 环境变量..."
echo ""

# 数据库 URL
POSTGRES_URL="postgresql://neondb_owner:npg_7kil2gsDbcIf@ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

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
