# LSnuts 云端平台

一个基于 Vue 3 + Flask 的全栈云端平台，提供网盘存储、轻量论坛和实时聊天功能。

## 🎯 功能特性

### 🌐 主要功能
- **轻量论坛** - 支持帖子发布、评论、点赞、收藏、置顶管理
- **安全网盘** - 文件上传、下载、删除管理
- **实时聊天** - 支持私聊和群聊功能
- **用户系统** - 注册、登录、个人资料管理
- **管理员面板** - 用户管理、帖子管理、权限控制

### ✨ 技术亮点
- 响应式设计，支持 PC 和移动端
- 深色/浅色模式切换
- Markdown 富文本编辑
- 通知系统（评论回复、@提及）
- 一键启动/关停脚本
- 统一响应格式（ok/fail 封装）
- 管理员权限装饰器
- 前端并行请求优化

## 🛠️ 技术栈

| 分类 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue | 3.x |
| 构建工具 | Vite | 5.x |
| UI组件库 | Element Plus | 2.x |
| CSS框架 | Tailwind CSS | 3.x |
| 状态管理 | Pinia | 2.x |
| 路由管理 | Vue Router | 4.x |
| 后端框架 | Flask | 3.x |
| 数据库 | SQLite | - |
| 实时通信 | Flask-SocketIO | - |

## 📁 项目结构

```
lsnuts2/
├── backend/                 # 后端 Flask 应用
│   ├── app.py               # 主应用入口
│   ├── models.py            # 数据库模型
│   ├── utils.py             # 工具函数（密码加密等）
│   └── static/uploads/      # 上传文件存储
├── frontend/                # 前端 Vue 应用
│   ├── src/
│   │   ├── views/           # 页面视图
│   │   ├── components/      # 公共组件
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── utils/           # 工具函数
│   │   ├── App.vue          # 根组件
│   │   ├── main.js          # 入口文件
│   │   └── router.js        # 路由配置
│   ├── .env.development     # 开发环境配置
│   └── .env.production      # 生产环境配置
├── start.bat                # Windows 一键启动脚本
├── start.ps1                # PowerShell 启动脚本
├── stop.bat                 # 一键关停脚本
└── README.md                # 项目说明文档
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 18+
- npm 或 yarn

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
python create_admin.py admin mypassword  # 自定义用户名和密码
```

若管理员已存在，脚本会询问是否重置密码。

> **安全提示**：`create_admin.py` 为 CLI 脚本，直接在服务器上运行，不对外开放任何管理员创建接口。

## 🔧 配置说明

### 环境变量

**前端配置** (`frontend/.env.production`)
```env
VITE_API_BASE=https://your-domain.com
```

**后端配置**
- SECRET_KEY：从环境变量读取，或自动生成随机密钥

### 跨域配置

后端已配置允许以下域名跨域访问：
- http://localhost:5173
- http://127.0.0.1:5173

## 🌊 API 接口

### 用户认证
- `POST /api/login` - 用户登录
- `POST /api/register` - 用户注册
- `GET /api/logout` - 退出登录
- `GET /api/user/info` - 获取用户信息

### 论坛
- `GET /api/forum/list` - 获取帖子列表
- `POST /api/forum/post` - 发布帖子
- `GET /api/forum/detail/:id` - 获取帖子详情
- `POST /api/forum/comment/:id` - 发表评论
- `POST /api/forum/like/:id` - 点赞/取消点赞
- `POST /api/forum/bookmark/:id` - 收藏/取消收藏

### 网盘
- `GET /api/drive/list` - 获取文件列表
- `POST /api/drive/upload` - 上传文件
- `GET /api/drive/download/:id` - 下载文件
- `DELETE /api/drive/delete/:id` - 删除文件

### 管理员
- `GET /api/admin/users` - 获取用户列表
- `DELETE /api/admin/delete/:id` - 删除用户
- `GET /api/admin/posts` - 获取帖子管理列表
- `DELETE /api/admin/delete_post/:id` - 删除帖子
- `POST /api/admin/toggle_pin/:id` - 置顶/取消置顶

## 📱 页面路由

| 路径 | 页面 | 描述 |
|------|------|------|
| `/` | 首页 | 平台介绍 |
| `/login` | 登录 | 用户登录 |
| `/register` | 注册 | 用户注册 |
| `/profile` | 个人中心 | 用户资料 |
| `/profile/posts` | 我的帖子 | 个人帖子管理 |
| `/profile/bookmarks` | 我的收藏 | 收藏列表 |
| `/profile/notifications` | 通知 | 消息通知 |
| `/settings` | 设置 | 账户设置 |
| `/drive` | 网盘 | 文件管理 |
| `/forum` | 论坛 | 帖子列表 |
| `/forum/post` | 发帖 | 发布新帖 |
| `/forum/detail/:id` | 帖子详情 | 查看帖子 |
| `/admin` | 管理后台 | 管理员面板 |
| `/about` | 关于本站 | 网站介绍 |

## 🔒 安全特性

- 密码使用 Werkzeug 安全哈希存储
- JWT Token 身份验证
- CSRF 防护
- SQLAlchemy ORM 防 SQL 注入
- 文件上传安全校验
- 权限控制中间件

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请通过 GitHub Issues 联系。
