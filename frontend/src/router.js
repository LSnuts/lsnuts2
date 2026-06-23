import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from './stores/user'

const routes = [
  { path: '/', component: () => import('./views/Index.vue'), meta: { title: '首页' } },
  { path: '/about', component: () => import('./views/About.vue'), meta: { title: '关于本站' } },
  { path: '/login', component: () => import('./views/Login.vue'), meta: { title: '登录' } },
  { path: '/register', component: () => import('./views/Register.vue'), meta: { title: '注册' } },
  { path: '/profile', component: () => import('./views/Profile.vue'), meta: { title: '个人中心' } },
  { path: '/profile/posts', component: () => import('./views/ProfilePosts.vue'), meta: { title: '我的帖子' } },
  { path: '/profile/bookmarks', component: () => import('./views/ProfileBookmarks.vue'), meta: { title: '我的收藏' } },
  { path: '/profile/notifications', component: () => import('./views/ProfileNotifications.vue'), meta: { title: '我的消息' } },
  { path: '/settings', component: () => import('./views/Settings.vue'), meta: { title: '设置' } },
  { path: '/drive', component: () => import('./views/Drive.vue'), meta: { title: '我的网盘' } },
  { path: '/forum', component: () => import('./views/Forum.vue'), meta: { title: '论坛' } },
  { path: '/forum/detail/:id', component: () => import('./views/ForumDetail.vue'), meta: { title: '帖子详情' } },
  { path: '/forum/post', component: () => import('./views/ForumPost.vue'), meta: { title: '发布帖子' } },
  { path: '/admin', component: () => import('./views/Admin.vue'), meta: { title: '管理后台' } },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('./views/NotFound.vue'), meta: { title: '页面未找到' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 动态设置页面标题
router.afterEach((to) => {
  const baseTitle = 'lsnuts 云端平台'
  const pageTitle = to.meta?.title
  if (pageTitle) {
    document.title = `${baseTitle} - ${pageTitle}`
  } else {
    document.title = baseTitle
  }
})

router.beforeEach(async (to, from) => {
  const publicPages = ['/login', '/register', '/', '/about']
  const authRequired = !publicPages.includes(to.path)
  const token = localStorage.getItem('lsnuts_token')

  if (authRequired && !token) {
    return '/login'
  }

  if (to.path === '/admin') {
    // 使用 store 缓存，避免每次路由切换都请求
    const store = useUserStore()
    if (!store.userInfo || store.userInfo.is_admin === undefined) {
      await store.fetchUserInfo()
    }
    if (store.userInfo.is_admin === 1) {
      return true
    } else {
      return '/'
    }
  }

  return true
})

export default router
