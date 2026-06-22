import { createRouter, createWebHistory } from 'vue-router'
import axios from './axios'

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
    try {
      const res = await axios.get('/api/user/info')
      if (res.data.data.is_admin === 1) {
        return true
      } else {
        return '/'
      }
    } catch (e) {
      if (e.response?.status === 401) {
        return '/login'
      }
      return '/'
    }
  }

  return true
})

export default router
