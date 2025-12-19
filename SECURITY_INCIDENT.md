# 数据库密码泄露事件处理指南

## 🚨 事件概要

**发现时间**: 2025-12-19
**问题**: PostgreSQL 连接字符串被硬编码在 3 个文件中并推送到公开的 GitHub 仓库
**影响范围**: Neon 数据库凭证完全暴露

---

## ✅ 已完成的修复（代码层面）

### 1. 移除硬编码密码
- ✅ [fast-import.py](fast-import.py#L12-17) - 已改为从环境变量读取
- ✅ [import-selected-stores.py](import-selected-stores.py#L15-20) - 已改为从环境变量读取
- ✅ [setup-env.sh](setup-env.sh#L6-18) - 已改为从 .env 文件读取

### 2. 验证 .gitignore
- ✅ `.env` 文件已经在 .gitignore 中（第27行）
- ✅ 本地 `.env` 文件从未被提交到 git

---

## 🔴 **必须立即执行的操作**（最重要！）

### 步骤 1: 轮换 Neon 数据库密码

登录 Neon 控制台：https://console.neon.tech

#### 选项 A：重置密码（推荐）
```
1. 进入你的项目
2. Settings → Database User → neondb_owner
3. 点击 "Reset Password"
4. 复制新的连接字符串
```

#### 选项 B：创建新用户（更安全）
```
1. 创建新的 Database User（例如：neondb_admin_2）
2. 授予相同权限
3. 删除旧用户 neondb_owner
```

### 步骤 2: 更新本地 .env 文件

替换为新的数据库 URL：
```bash
# 编辑 .env 文件
nano .env

# 将所有旧的 URI 替换为新的
POSTGRES_URL="postgresql://NEW_USER:NEW_PASSWORD@..."
```

### 步骤 3: 更新 Vercel 环境变量

```bash
# 使用更新后的 .env 运行
./setup-env.sh

# 或手动在 Vercel Dashboard 更新：
# https://vercel.com/dashboard → Settings → Environment Variables
```

### 步骤 4: 提交代码修复并推送

```bash
git add fast-import.py import-selected-stores.py setup-env.sh SECURITY_INCIDENT.md
git commit -m "Security: Remove hardcoded database credentials

- Move DATABASE_URL to environment variables
- Add validation for missing credentials
- Update setup-env.sh to read from .env file
- Add security incident documentation"

git push
```

---

## 📊 泄露的具体信息

**泄露的连接字符串格式**:
```
postgresql://neondb_owner:npg_7kil2gsDbcIf@ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech/neondb
```

**包含的信息**:
- 用户名: `neondb_owner`
- 密码: `npg_7kil2gsDbcIf`
- 主机: `ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech`
- 数据库名: `neondb`

---

## 🔍 风险评估

### 高风险
- ✅ 仓库是公开的（已确认）
- ✅ 密码在 GitHub 公开历史中可见
- ✅ 完整的数据库连接信息泄露

### 潜在影响
- 未授权访问数据库
- 数据泄露
- 数据篡改或删除
- 服务拒绝攻击

---

## 🛡️ 预防措施（未来）

### 1. 使用环境变量
```python
# ✅ 正确做法
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set")

# ❌ 错误做法
DATABASE_URL = "postgresql://user:pass@host/db"
```

### 2. 使用 .env.example 模板
```bash
# .env.example (可以提交)
POSTGRES_URL="postgresql://YOUR_USER:YOUR_PASSWORD@YOUR_HOST/YOUR_DB"

# .env (绝对不能提交)
POSTGRES_URL="postgresql://real_user:real_pass@real_host/real_db"
```

### 3. Git Hooks（推荐）
安装 pre-commit 防止提交敏感信息：
```bash
pip install pre-commit
pre-commit install
```

### 4. 使用密钥管理工具
- GitHub Secrets（用于 CI/CD）
- Vercel Environment Variables（用于部署）
- AWS Secrets Manager / HashiCorp Vault（生产环境）

---

## 📝 检查清单

完成修复后请确认：

- [ ] 已在 Neon 控制台重置数据库密码
- [ ] 已更新本地 .env 文件
- [ ] 已更新 Vercel 环境变量
- [ ] 已提交代码修复
- [ ] 已推送到 GitHub
- [ ] 已测试应用是否能正常连接数据库
- [ ] 已确认 .gitignore 包含 .env
- [ ] 已通知团队成员不要使用旧凭证

---

## 🆘 需要帮助？

如果遇到问题：
1. 检查 Neon Dashboard 的连接信息
2. 确保 .env 文件格式正确
3. 运行 `source .env` 后再运行脚本
4. 检查 Vercel 部署日志

---

**最后更新**: 2025-12-19
**状态**: 🟡 代码已修复，等待密码轮换
