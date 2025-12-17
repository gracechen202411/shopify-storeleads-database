# 🚀 部署选项 - Neon免费版解决方案

由于Neon免费版有500MB存储限制，而我们有1.5GB数据，这里提供两种解决方案：

## 📊 数据概览

- **原始数据**: 1.5GB, 2,391,857 条记录
- **Neon免费限制**: 500MB存储
- **需求**: 需要特殊处理

---

## ✅ 方案1：精选数据库（推荐用于演示）

### 优点
- ✅ 只需1个免费Neon项目
- ✅ 包含55万+最优质店铺
- ✅ 部署简单
- ✅ 查询速度快
- ✅ 适合演示和个人使用

### 数据特点
- **记录数**: 551,996 个店铺（原数据的23%）
- **文件大小**: 450MB（符合500MB限制）
- **质量**: 所有店铺都是活跃状态，都有访问数据
- **排序**: 按月访问量排序，优先保留高流量店铺

### 部署步骤

#### 1. 创建Neon数据库
```bash
# 访问 https://neon.tech 创建免费项目
# 复制连接字符串
```

#### 2. 创建表结构
```bash
cd /Users/grace/Downloads/ALL/下载ALLLL/shopify-storeleads-app
psql "你的Neon连接字符串" -f schema.sql
```

#### 3. 导入精选数据
```bash
# 设置环境变量
export DATABASE_URL="你的Neon连接字符串"

# 导入单个精选文件
python3 import-to-neon.py /Users/grace/Downloads/ALL/下载ALLLL/shopify-storeleads-filtered.csv
```

预计导入时间：15-20分钟

#### 4. 部署应用
```bash
# 不需要修改代码，使用标准的 lib/db.ts

# 在Vercel添加环境变量：
POSTGRES_URL=你的Neon连接字符串
POSTGRES_PRISMA_URL=你的Neon连接字符串?pgbouncer=true
POSTGRES_URL_NON_POOLING=你的Neon连接字符串
```

---

## 🔄 方案2：多数据库架构（完整数据）

### 优点
- ✅ 包含所有2.4M条记录
- ✅ 数据完整
- ✅ 仍然使用免费资源

### 缺点
- ⚠️ 需要3-4个Neon免费账户/项目
- ⚠️ 配置复杂
- ⚠️ 查询速度较慢（需要合并多个数据库结果）
- ⚠️ 部署和维护成本高

### 部署步骤

#### 1. 创建多个Neon项目
```bash
# 需要创建3-4个Neon账户或在同一账户下创建多个项目
# 每个项目获取一个连接字符串

# 项目1: 存储 part1.csv (400MB)
# 项目2: 存储 part2.csv (400MB)
# 项目3: 存储 part3.csv (400MB)
# 项目4: 存储 part4.csv (290MB)
```

#### 2. 在每个数据库创建表
```bash
# 对每个Neon项目运行
psql "Neon连接字符串1" -f schema.sql
psql "Neon连接字符串2" -f schema.sql
psql "Neon连接字符串3" -f schema.sql
psql "Neon连接字符串4" -f schema.sql
```

#### 3. 分别导入数据
```bash
# 为每个数据库设置环境变量并导入对应的CSV

export DATABASE_URL="Neon连接字符串1"
python3 import-to-neon.py ../chunks/shopify-storeleads-part1.csv

export DATABASE_URL="Neon连接字符串2"
python3 import-to-neon.py ../chunks/shopify-storeleads-part2.csv

export DATABASE_URL="Neon连接字符串3"
python3 import-to-neon.py ../chunks/shopify-storeleads-part3.csv

export DATABASE_URL="Neon连接字符串4"
python3 import-to-neon.py ../chunks/shopify-storeleads-part4.csv
```

#### 4. 修改应用代码使用多数据库

**修改 `lib/db.ts`**:
```typescript
// 替换为：
export * from './db-multi';
```

或直接修改 API 路由导入：
```typescript
// app/api/stores/route.ts
import { searchStoresMultiDB as searchStores } from '@/lib/db-multi';

// app/api/stats/route.ts
import { getStatsMultiDB as getStats } from '@/lib/db-multi';
```

#### 5. 配置环境变量
```bash
# 在Vercel添加所有数据库连接
POSTGRES_URL_1=Neon连接字符串1
POSTGRES_URL_2=Neon连接字符串2
POSTGRES_URL_3=Neon连接字符串3
POSTGRES_URL_4=Neon连接字符串4
```

---

## 🎯 方案3：升级付费计划

### Neon Pro计划
- **价格**: $19/月起
- **存储**: 10GB
- **优点**: 简单，性能好，单数据库
- **适合**: 生产环境

### 部署步骤
1. 访问 https://neon.tech/pricing
2. 升级到Pro计划
3. 使用标准导入流程（方案1的步骤）
4. 可以导入全部4个CSV文件

---

## 🎯 方案对比

| 特性 | 方案1 精选数据 | 方案2 多数据库 | 方案3 付费 |
|------|---------------|---------------|-----------|
| 成本 | 免费 | 免费 | $19/月 |
| 数据量 | 55万店铺 | 240万店铺 | 240万店铺 |
| 部署难度 | ⭐ 简单 | ⭐⭐⭐ 复杂 | ⭐ 简单 |
| 查询速度 | ⚡⚡⚡ 快 | ⚡ 慢 | ⚡⚡⚡ 快 |
| 维护成本 | 低 | 高 | 低 |
| 推荐场景 | 演示/个人 | DIY爱好者 | 生产环境 |

---

## 💡 推荐方案

### 对于大多数用户
**→ 使用方案1（精选数据）**

理由：
1. ✅ 55万条记录足够展示功能
2. ✅ 包含最有价值的店铺（高流量、活跃状态）
3. ✅ 部署简单，一个命令完成
4. ✅ 查询快速
5. ✅ 完全免费

### 如果你需要完整数据
- **短期/学习**: 方案2（多数据库）
- **长期/生产**: 方案3（付费）

---

## 📝 快速开始（方案1）

```bash
# 1. 精选数据已生成
ls -lh /Users/grace/Downloads/ALL/下载ALLLL/shopify-storeleads-filtered.csv

# 2. 创建Neon项目
# 访问 https://neon.tech

# 3. 创建表
psql "你的连接字符串" -f schema.sql

# 4. 导入数据
export DATABASE_URL="你的连接字符串"
python3 import-to-neon.py /Users/grace/Downloads/ALL/下载ALLLL/shopify-storeleads-filtered.csv

# 5. 本地测试
npm install
cp .env.example .env
# 编辑 .env 填入数据库URL
npm run dev

# 6. 部署到Vercel
# 点击 README.md 中的 "Deploy with Vercel" 按钮
```

---

## 🔍 数据质量对比

### 精选数据库 (方案1)
```
✓ 551,996 条记录
✓ 100% 活跃店铺
✓ 100% 有访问数据
✓ 按访问量排序
✓ 包含最热门店铺

示例：
- 第1名: The New York Times (248M 月访问)
- 第10名: 高流量电商网站
- 第1000名: 中型活跃店铺
- ...
```

### 完整数据库 (方案2/3)
```
✓ 2,391,857 条记录
✓ 包含所有历史店铺
✓ 包含非活跃店铺
✓ 完整的商业智能数据
```

---

## ❓ FAQ

**Q: 精选数据是否足够？**
A: 对于大多数用途（演示、学习、个人项目）完全足够。包含所有顶级店铺和主要市场数据。

**Q: 如何选择更多数据？**
A: 编辑 `filter-data.py` 中的 `TARGET_SIZE_MB` 变量（如改为380MB可以获得更多记录）

**Q: 方案2的查询速度有多慢？**
A: 每次查询需要访问3-4个数据库并合并结果，响应时间约2-5秒（vs 方案1的0.1-0.5秒）

**Q: 可以混合使用吗？**
A: 可以！先用方案1快速上线，后期需要时升级到方案3

---

## 🎊 总结

**立即可用的文件**:
- ✅ `shopify-storeleads-filtered.csv` (450MB, 551K+ 记录) - 已生成
- ✅ `import-to-neon.py` - 导入脚本
- ✅ `schema.sql` - 数据库表结构
- ✅ Next.js 应用代码 - 完整应用

**推荐行动**:
1. 🚀 使用方案1快速部署
2. 📊 验证功能和性能
3. 💰 根据需要决定是否升级

祝部署顺利！🎉
