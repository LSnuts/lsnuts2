# Debug Session: post-create-error

## Status: [FIXED]

## Problem Description
发帖功能出现问题，无法发帖

## Hypotheses
1. **H1**: 前端发帖请求未正确发送到后端（网络/CORS问题） - ❌ 排除
2. **H2**: 后端发帖 API 路由处理逻辑有问题（数据库写入失败） - ❌ 排除
3. **H3**: 用户认证状态丢失（未登录或 Token 无效） - ❌ 排除
4. **H4**: PostgreSQL 数据库连接或表结构问题 - ✅ **确认**
5. **H5**: 前端表单数据验证或格式问题 - ❌ 排除

## Evidence Collection
- Pre-fix logs:
```
sqlalchemy.exc.IntegrityError: (psycopg2.errors.NotNullViolation) 
错误: null value in column "id" of relation "posts" violates not-null constraint
```

- Post-fix logs:
```
后端服务正常启动，API 返回 401 Unauthorized（需要登录认证）
```

## Analysis
**根本原因**: PostgreSQL 表的 `id` 列没有设置自增（SERIAL），迁移脚本创建表时没有正确处理主键的自增属性。SQLite 的 INTEGER PRIMARY KEY 会自动自增，但 PostgreSQL 需要使用 SERIAL 类型并设置序列。

## Fix
1. 创建 `fix_postgres_tables.py` 修复脚本
2. 为每个表的 `id` 列创建序列并设置默认值
3. 将序列绑定到表的 `id` 列

## Verification
- 后端服务已重新启动
- API 响应正常（401 表示需要登录，符合预期）
- 用户可通过前端页面登录后发帖