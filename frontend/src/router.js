import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from './stores/user'

const routes = [
  { path: '/', component: () => import('./views/Index.vue') },
  { path: '/about', component: () => import('./views/About.vue') },
  { path: '/login', component: () => import('./views/Login.vue') },
  { path: '/register', component: () => import('./views/Register.vue') },
  { path: '/profile', component: () => import('./views/Profile.vue') },
  { path: '/profile/posts', component: () => import('./views/ProfilePosts.vue') },
  { path: '/profile/bookmarks', component: () => import('./views/ProfileBookmarks.vue') },
  { path: '/profile/notifications', component: () => import('./views/ProfileNotifications.vue') },
  { path: '/settings', component: () => import('./views/Settings.vue') },
  { path: '/drive', component: () => import('./views/Drive.vue') },
  { path: '/forum', component: () => import('./views/Forum.vue') },
  { path: '/forum/detail/:id', component: () => import('./views/ForumDetail.vue') },
  { path: '/forum/post', component: () => import('./views/ForumPost.vue') },
  { path: '/admin', component: () => import('./views/Admin.vue') },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('./views/NotFound.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
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
