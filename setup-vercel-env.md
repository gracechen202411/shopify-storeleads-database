# Vercel 环境变量设置指南

## 🔧 需要在 Vercel 设置的环境变量

访问 Vercel Dashboard: https://vercel.com/gracechen202411/shopify-storeleads-database/settings/environment-variables

### 1. 数据库环境变量

```bash
# 变量名: POSTGRES_URL
# 值:
postgresql://neondb_owner:npg_7kil2gsDbcIf@ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require

# 变量名: POSTGRES_PRISMA_URL
# 值:
postgresql://neondb_owner:npg_7kil2gsDbcIf@ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&pgbouncer=true

# 变量名: POSTGRES_URL_NON_POOLING
# 值:
postgresql://neondb_owner:npg_7kil2gsDbcIf@ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### 2. 使用 Vercel CLI 自动设置

```bash
# 安装 Vercel CLI（如果还没有）
npm i -g vercel

# 登录
vercel login

# 链接项目
vercel link

# 设置环境变量
vercel env add POSTGRES_URL production
# 粘贴上面的 POSTGRES_URL 值

vercel env add POSTGRES_PRISMA_URL production
# 粘贴上面的 POSTGRES_PRISMA_URL 值

vercel env add POSTGRES_URL_NON_POOLING production
# 粘贴上面的 POSTGRES_URL_NON_POOLING 值

# 重新部署
vercel --prod
```

## ✅ 验证步骤

1. 访问 https://topsales.ecomgrace.com
2. 应该看到登录页面
3. 登录后可以看到店铺列表
4. 筛选功能应该正常工作

## 🐛 常见问题

### 问题1: "Application error"
**原因**: 环境变量没有设置
**解决**: 按照上面的步骤设置环境变量后重新部署

### 问题2: "Database connection failed"
**原因**: 数据库 URL 不正确
**解决**: 检查环境变量中的数据库连接字符串

### 问题3: 页面加载慢
**原因**: 数据库查询需要优化
**解决**: 已经添加了索引，应该会快一些

## 📞 需要帮助？

如果遇到问题，请：
1. 检查 Vercel 部署日志
2. 检查浏览器控制台错误
3. 确认环境变量已正确设置
