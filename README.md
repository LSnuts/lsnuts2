# LSnuts 云端平台

一个基于 Vue 3 + Flask 的全栈云端平台，提供网盘存储、轻量论坛和实时聊天功能。

## 🎯 功能特性

### 🌐 主要功能
- **轻量论坛** - 支持帖子发布、评论、楼中楼回复、点赞、收藏、置顶管理
- **安全网盘** - 文件上传、下载、删除管理、文件夹分类、文件分享链接
- **用户系统** - 注册、登录、个人资料管理、个人主页、密码找回
- **管理员面板** - 用户管理、帖子管理、权限控制、数据统计、公告系统
- **公告系统** - 管理员发布公告，支持优先级和置顶

### ✨ 技术亮点
- 响应式设计，支持 PC 和移动端
- 深色/浅色模式切换
- Markdown 富文本编辑
- 通知系统（评论回复、@提及）
- 一键启动/关停脚本
- 统一响应格式（ok/fail 封装）
- 管理员权限装饰器
- 前端并行请求优化
- 头像裁剪上传
- 图片压缩处理
- Flask-Migrate 数据库迁移

## 🛠️ 技术栈

| 分类 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue | 3.x |
| 构建工具 | Vite | 5.x |
| UI组件库 | Element Plus | 2.x |
| CSS框架 | Tailwind CSS | 3.x |
| 状态管理 | Pinia | 2.x |
| 路由管理 | Vue Router | 4.x |
| HTTP客户端 | Axios | - |
| 后端框架 | Flask | 3.x |
| 数据库 | PostgreSQL | 15+ |
| ORM | SQLAlchemy | 2.x |
| 数据库迁移 | Flask-Migrate | 4.x |
| 实时通信 | Flask-SocketIO | - |
| 限流 | Flask-Limiter | - |
| 用户认证 | Flask-Login | - |

## 📁 项目结构

```
lsnuts2/
├── backend/                 # 后端 Flask 应用
│   ├── app.py               # 主应用入口
│   ├── models.py            # 数据库模型
│   ├── utils.py             # 工具函数（密码加密等）
│   ├── utils/secure_logger.py # 安全日志记录
│   ├── blueprints/          # Blueprint 模块化
│   │   ├── auth.py          # 用户认证路由
│   │   ├── forum.py         # 论坛路由
│   │   ├── drive.py         # 网盘路由
│   │   ├── admin.py         # 管理员路由
│   │   └── chat.py          # 聊天路由
│   ├── migrations/          # 数据库迁移文件
│   ├── static/uploads/      # 上传文件存储
│   ├── .env                 # 环境变量配置
│   ├── manage.py            # 数据库迁移管理脚本
│   ├── create_admin.py      # 管理员账号创建脚本
│   └── requirements.txt     # 后端依赖
├── frontend/                # 前端 Vue 应用
│   ├── src/
│   │   ├── views/           # 页面视图
│   │   │   ├── Index.vue    # 首页（含公告展示）
│   │   │   ├── Login.vue    # 登录页
│   │   │   ├── Register.vue # 注册页
│   │   │   ├── ForgotPassword.vue # 忘记密码
│   │   │   ├── ResetPassword.vue  # 重置密码
│   │   │   ├── Profile.vue  # 个人中心
│   │   │   ├── UserProfile.vue # 用户个人主页
│   │   │   ├── Drive.vue    # 网盘页面
│   │   │   ├── Forum.vue    # 论坛列表
│   │   │   ├── ForumDetail.vue # 帖子详情
│   │   │   ├── ForumPost.vue # 发帖页面
│   │   │   ├── Admin.vue    # 管理后台
│   │   │   └── About.vue    # 关于本站
│   │   ├── components/      # 公共组件
│   │   │   ├── CommentTree.vue # 评论树形组件
│   │   │   └── ImageCropper.vue # 头像裁剪组件
│   │   ├── stores/          # Pinia 状态管理
│   │   │   ├── user.js      # 用户状态
│   │   │   ├── forum.js     # 论坛状态
│   │   │   ├── drive.js     # 网盘状态
│   │   │   └── notification.js # 通知状态
│   │   ├── axios.js         # Axios 配置（拦截器）
│   │   ├── App.vue          # 根组件
│   │   ├── main.js          # 入口文件
│   │   └── router.js        # 路由配置
│   ├── .env.development     # 开发环境配置
│   └── package.json         # 前端依赖
├── start.bat                # Windows 一键启动脚本
├── start.ps1                # PowerShell 启动脚本
├── stop.bat                 # 一键关停脚本
└── README.md                # 项目说明文档
```

## 快速开始

### 环境要求
- Python 3.8+ (推荐使用 Miniconda)
- Node.js 18+
- npm 或 yarn
- PostgreSQL 15+

### 数据库配置

创建 PostgreSQL 数据库并配置环境变量：

```bash
# 创建数据库（以 PostgreSQL 为例）
createdb -U lsnuts garden1
```

编辑 `backend/.env` 文件：

```env
# 数据库配置
DATABASE_URL=postgresql://lsnuts:123456@localhost:5432/garden1

# 密钥配置
SECRET_KEY=your-secret-key-here-generate-a-random-24-byte-hex

# Flask 配置
FLASK_ENV=development
FLASK_DEBUG=false
```

### 安装依赖

**后端依赖**
```bash
cd backend
pip install -r requirements.txt
```

**前端依赖**
```bash
cd frontend
npm install
```

### 数据库迁移

首次运行需要初始化数据库迁移：

```bash
cd backend
python manage.py init      # 初始化迁移目录
python manage.py migrate "initial migration"  # 创建迁移文件
python manage.py upgrade   # 执行迁移
```

后续模型变更时：

```bash
cd backend
python manage.py migrate "description of changes"
python manage.py upgrade
```

### 启动项目

**方式一：一键启动（推荐）**

双击运行 `start.bat`，将自动启动：
- 后端服务：http://127.0.0.1:5000/
- 前端服务：http://localhost:5173/

**方式二：手动启动**

```bash
# 启动后端
cd backend
python app.py

# 启动前端（新终端）
cd frontend
npm run dev
```

### 停止服务

双击运行 `stop.bat` 或直接关闭命令行窗口。

### 初始账号

管理员账号通过后端脚本创建，不暴露 HTTP 接口：

```bash
cd backend
python create_admin.py          # 使用默认账号 admin / admin123
python create_admin.py admin 123456  # 自定义用户名和密码
python create_admin.py admin 123456 -f  # 强制重置密码
```

若管理员已存在，脚本会询问是否重置密码。

> **安全提示**：`create_admin.py` 为 CLI 脚本，直接在服务器上运行，不对外开放任何管理员创建接口。

## 🔧 配置说明

### 环境变量

**后端配置** (`backend/.env`)
```env
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
SECRET_KEY=your-secret-key
FLASK_ENV=development
FLASK_DEBUG=false
```

**前端配置** (`frontend/.env.development`)
```env
VITE_API_BASE=http://localhost:5000
```

### 跨域配置

后端已配置允许以下域名跨域访问：
- http://localhost:5173
- http://127.0.0.1:5173
- http://localhost:5174
- http://127.0.0.1:5174
- http://localhost:5175
- http://127.0.0.1:5175

## 🌊 API 接口

### 用户认证
- `POST /api/login` - 用户登录
- `POST /api/register` - 用户注册
- `GET /api/logout` - 退出登录
- `GET /api/user/info` - 获取用户信息
- `POST /api/user/avatar` - 上传头像
- `PUT /api/user/username` - 修改用户名
- `PUT /api/user/password` - 修改密码
- `GET /api/user/profile/:id` - 获取用户个人主页
- `GET /api/user/profile/:id/posts` - 获取用户帖子
- `POST /api/auth/forgot-password` - 忘记密码（验证身份）
- `GET /api/auth/verify-token` - 验证重置密码token
- `POST /api/auth/reset-password` - 重置密码

### 论坛
- `GET /api/forum/list` - 获取帖子列表
- `POST /api/forum/post` - 发布帖子
- `GET /api/forum/detail/:id` - 获取帖子详情
- `POST /api/forum/comment/:id` - 发表评论
- `POST /api/forum/reply/:id` - 楼中楼回复
- `POST /api/forum/like/:id` - 点赞/取消点赞
- `POST /api/forum/bookmark/:id` - 收藏/取消收藏

### 网盘
- `GET /api/drive/list` - 获取文件列表
- `POST /api/drive/upload` - 上传文件
- `GET /api/drive/download/:id` - 下载文件
- `DELETE /api/drive/delete/:id` - 删除文件
- `PUT /api/drive/category/:id` - 修改文件分类
- `POST /api/drive/share/:id` - 生成分享链接
- `GET /api/drive/share/:token` - 获取分享文件
- `GET /api/drive/storage` - 获取存储空间统计

### 管理员
- `GET /api/admin/users` - 获取用户列表
- `DELETE /api/admin/delete/:id` - 删除用户
- `GET /api/admin/posts` - 获取帖子管理列表
- `DELETE /api/admin/delete_post/:id` - 删除帖子
- `POST /api/admin/toggle_pin/:id` - 置顶/取消置顶
- `GET /api/admin/statistics` - 获取数据统计
- `GET /api/admin/announcements` - 获取公告列表
- `POST /api/admin/announcement` - 发布公告
- `PUT /api/admin/announcement/:id` - 更新公告
- `DELETE /api/admin/announcement/:id` - 删除公告

### 公告（公开）
- `GET /api/announcements/public` - 获取公开公告列表

## 📱 页面路由

| 路径 | 页面 | 描述 |
|------|------|------|
| `/` | 首页 | 平台介绍、公告展示 |
| `/login` | 登录 | 用户登录 |
| `/register` | 注册 | 用户注册 |
| `/forgot-password` | 忘记密码 | 身份验证 |
| `/reset-password` | 重置密码 | 设置新密码 |
| `/profile` | 个人中心 | 用户资料 |
| `/profile/posts` | 我的帖子 | 个人帖子管理 |
| `/profile/bookmarks` | 我的收藏 | 收藏列表 |
| `/profile/notifications` | 通知 | 消息通知 |
| `/settings` | 设置 | 账户设置 |
| `/user/:id` | 用户主页 | 查看其他用户信息 |
| `/drive` | 网盘 | 文件管理 |
| `/forum` | 论坛 | 帖子列表 |
| `/forum/post` | 发帖 | 发布新帖 |
| `/forum/detail/:id` | 帖子详情 | 查看帖子、评论 |
| `/admin` | 管理后台 | 管理员面板 |
| `/about` | 关于本站 | 网站介绍 |

## 🔒 安全特性

- 密码使用 Werkzeug 安全哈希存储
- Flask-Login 会话管理（HTTP-only Cookie）
- CSRF 防护（SESSION_COOKIE_SAMESITE）
- SQLAlchemy ORM 防 SQL 注入
- 文件上传安全校验（secure_filename）
- 路径遍历防护（realpath 检查）
- 权限控制中间件
- 管理员权限装饰器
- Flask-Limiter 限流保护

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请通过 GitHub Issues 联系。
111111111111111考试，停更6天
考试第一天，停更。
考试第二天，停更。
考试第三天，停更。
考试第四天，停更。
第五天忘了，7/11正式完工
7/13打工
打工ing.....
打工ing.....