# LSNuts 综合平台

一个包含用户认证、网盘、论坛和实时聊天功能的全栈应用。

## 项目结构

```
lsnuts2/
├── backend/          # Flask 后端
│   ├── app.py       # 主应用文件
│   ├── models.py    # 数据模型
│   └── utils.py     # 工具函数
└── frontend/        # Vue 3 前端
    ├── src/
    │   ├── views/  # 页面组件
    │   ├── router/ # 路由配置
    │   └── api/    # API 接口
    └── package.json
```

## 后端启动

1. 安装依赖：
   ```bash
   cd backend
   py -m pip install Flask Flask-SQLAlchemy Flask-Login Flask-CORS Flask-SocketIO
   ```

2. 启动服务：
   ```bash
   py app.py
   ```

后端将运行在 http://localhost:5000

## 前端启动

### 前置要求

需要安装 Node.js（建议版本 18+），下载地址：https://nodejs.org/

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

前端将运行在 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

## 功能说明

### 用户认证
- 注册新账号
- 用户登录/退出
- 获取当前用户信息

### 网盘
- 上传文件
- 下载文件
- 删除文件
- 文件列表

### 论坛
- 查看帖子列表
- 发布新帖子
- 查看帖子详情
- 发表评论

### 实时聊天
- WebSocket 实时通信
- 群聊功能

### 管理功能
- 创建管理员账号（访问 /api/admin/create）
- 用户列表
- 删除用户（管理员权限）

默认管理员账号：admin / admin123

## 技术栈

### 后端
- Flask - Web 框架
- Flask-SQLAlchemy - ORM
- Flask-Login - 用户认证
- Flask-CORS - 跨域支持
- Flask-SocketIO - WebSocket

### 前端
- Vue 3 - 前端框架
- Vite - 构建工具
- Vue Router - 路由
- Element Plus - UI 组件库
- Axios - HTTP 客户端
- Socket.IO-Client - WebSocket 客户端
