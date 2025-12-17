# 快速开始指南 (Quick Start Guide)

## 📋 项目概述

这是一个Shopify店铺数据库浏览器，包含约240万条店铺记录。

## 🗂️ 文件说明

### 数据文件
- `../chunks/` 目录包含4个CSV文件（每个约400MB）：
  - `shopify-storeleads-part1.csv` (478,315 条记录)
  - `shopify-storeleads-part2.csv` (586,289 条记录)
  - `shopify-storeleads-part3.csv` (774,480 条记录)
  - `shopify-storeleads-part4.csv` (552,773 条记录)

### 应用文件
- `schema.sql` - 数据库表结构
- `import-to-neon.py` - 单个文件导入脚本
- `import-all.sh` - 批量导入脚本
- `app/` - Next.js 应用代码
- `components/` - React 组件

## 🚀 部署步骤

### 第一步：创建 Neon 数据库

1. 访问 [https://neon.tech](https://neon.tech)
2. 注册免费账户
3. 创建新项目
4. 复制数据库连接字符串（类似：`postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb`）

### 第二步：创建数据库表

在终端运行：

```bash
# 方法1：使用 psql 命令
psql "你的数据库连接字符串" -f schema.sql

# 方法2：在 Neon Console 的 SQL Editor 中复制粘贴 schema.sql 的内容并执行
```

### 第三步：导入数据

```bash
# 1. 安装 Python 依赖
pip install psycopg2-binary

# 2. 设置数据库连接
export DATABASE_URL="你的数据库连接字符串"

# 3. 运行导入脚本（自动导入所有4个文件）
./import-all.sh
```

**注意**：导入过程可能需要1-2小时，请保持终端运行。

如果想单独导入某个文件：
```bash
python3 import-to-neon.py ../chunks/shopify-storeleads-part1.csv
```

### 第四步：配置 Next.js 应用

```bash
# 1. 安装依赖
npm install

# 2. 创建环境变量文件
cp .env.example .env

# 3. 编辑 .env 文件，填入你的 Neon 数据库连接字符串
# 使用文本编辑器打开 .env 并修改：
POSTGRES_URL="你的数据库连接字符串"
POSTGRES_PRISMA_URL="你的数据库连接字符串?pgbouncer=true"
POSTGRES_URL_NON_POOLING="你的数据库连接字符串"
```

### 第五步：本地测试

```bash
# 启动开发服务器
npm run dev

# 在浏览器打开 http://localhost:3000
```

### 第六步：部署到 Vercel

#### 方法1：通过 GitHub（推荐）

1. 将代码推送到 GitHub：
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/你的用户名/你的仓库名.git
   git push -u origin main
   ```

2. 访问 [vercel.com](https://vercel.com)
3. 点击 "Import Project"
4. 选择你的 GitHub 仓库
5. 添加环境变量：
   - `POSTGRES_URL`
   - `POSTGRES_PRISMA_URL`
   - `POSTGRES_URL_NON_POOLING`
6. 点击 "Deploy"

#### 方法2：使用 Vercel CLI

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录
vercel login

# 部署
vercel

# 添加环境变量
vercel env add POSTGRES_URL
vercel env add POSTGRES_PRISMA_URL
vercel env add POSTGRES_URL_NON_POOLING

# 重新部署
vercel --prod
```

## 📊 功能特性

- ✅ 搜索店铺名称、域名、描述
- ✅ 按国家筛选
- ✅ 按月访问量筛选
- ✅ 显示社交媒体链接
- ✅ 显示业务统计数据
- ✅ 响应式设计
- ✅ 深色模式支持
- ✅ 分页浏览

## 🔧 常见问题

### Q: 导入数据时出错？
A: 检查：
- 数据库连接字符串是否正确
- Neon 项目是否激活
- 是否已运行 schema.sql

### Q: Vercel 部署后无法连接数据库？
A: 确认：
- 环境变量已在 Vercel 项目设置中添加
- 使用的是正确的 Neon 连接字符串
- Neon 项目允许外部连接

### Q: 如何修改每页显示的记录数？
A: 编辑 `app/page.tsx`，修改第29行的 `limit: '20'` 为你想要的数量。

### Q: 数据库查询太慢？
A: 检查：
- 索引是否正确创建（查看 schema.sql）
- 是否启用了 Neon 的连接池
- 考虑升级 Neon 计划以获得更好性能

## 📝 数据库信息

- **总记录数**: 2,391,857
- **数据库大小**: 约 1.5GB
- **字段数**: 44 个
- **主要字段**:
  - 店铺基本信息（域名、名称、描述）
  - 位置信息（国家、州、城市）
  - 业务指标（访问量、销售额、员工数）
  - 社交媒体账号（Instagram、Facebook、Twitter、TikTok等）

## 💡 下一步优化建议

1. **添加缓存**: 使用 Redis 缓存热门查询
2. **添加分析**: 集成 Google Analytics
3. **添加导出**: 允许用户导出搜索结果
4. **添加收藏**: 让用户可以收藏感兴趣的店铺
5. **添加比较**: 对比多个店铺的数据
6. **API 限流**: 添加请求频率限制
7. **用户认证**: 添加登录功能以保护数据

## 📧 需要帮助？

如有问题，请查看：
- README.md - 详细文档
- Neon 文档: https://neon.tech/docs
- Next.js 文档: https://nextjs.org/docs
- Vercel 文档: https://vercel.com/docs

---

祝你使用愉快！🎉
