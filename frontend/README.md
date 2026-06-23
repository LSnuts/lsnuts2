# LSnuts Frontend

前端 Vue 3 应用，为 LSnuts 云端平台提供用户界面。

## 🛠️ 技术栈

- Vue 3 (Composition API)
- Vite 5
- Element Plus 2.x
- Tailwind CSS 3.x
- Pinia (状态管理)
- Vue Router 4.x
- Axios (HTTP 客户端)

## 📁 项目结构

```
src/
├── views/           # 页面视图组件
├── components/      # 公共组件
├── stores/          # Pinia 状态管理
├── utils/           # 工具函数和常量
├── App.vue          # 根组件
├── main.js          # 入口文件
├── router.js        # 路由配置
├── axios.js         # Axios 配置
└── style.css        # 全局样式
```

## 🚀 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:5173/

### 生产构建

```bash
npm run build
```

### 预览构建结果

```bash
npm run preview
```

## 🔧 配置

### 环境变量

创建 `.env.development` 和 `.env.production` 文件：

```env
VITE_API_BASE=http://127.0.0.1:5000
```

### 路由配置

路由定义在 `src/router.js`，包含：
- 公共页面：首页、关于、登录、注册
- 用户页面：个人中心、设置、网盘、论坛
- 管理员页面：管理后台

## 📱 页面说明

| 路径 | 组件 | 说明 |
|------|------|------|
| `/` | Index.vue | 首页 |
| `/login` | Login.vue | 登录页 |
| `/register` | Register.vue | 注册页 |
| `/profile` | Profile.vue | 个人中心 |
| `/settings` | Settings.vue | 设置页 |
| `/drive` | Drive.vue | 网盘 |
| `/forum` | Forum.vue | 论坛首页 |
| `/forum/post` | ForumPost.vue | 发帖页 |
| `/forum/detail/:id` | ForumDetail.vue | 帖子详情 |
| `/admin` | Admin.vue | 管理后台 |
| `/about` | About.vue | 关于本站 |

## 🎨 主题

支持深色/浅色模式切换，使用 Element Plus 官方深色模式。

## 📡 API 交互

通过 Axios 与后端 Flask API 通信，配置在 `src/axios.js`。
