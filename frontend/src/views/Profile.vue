<template>
  <div class="p-3 md:p-5 max-w-[650px] mx-auto">
    <div class="flex flex-col items-center mb-5">
      <img :src="displayAvatar" :alt="userInfo.username"
        class="w-[16vw] h-[16vw] max-w-[150px] max-h-[150px] min-w-[80px] min-h-[80px] object-cover rounded-full shadow-lg mb-3 border-4 border-blue-100 dark:border-blue-900" />
      <h1 class="text-2xl font-bold text-gray-800 dark:text-gray-200">{{ userInfo.username }}</h1>
    </div>

    <div class="flex-row-wrapper">
      <button class="module-btn" @click="$router.push('/profile/posts')">
        <span class="btn-icon">📝</span>
        <span class="btn-text">我的帖子</span>
        <span class="btn-count">({{ formatCount(postsTotal) }})</span>
      </button>
      <button class="module-btn" @click="$router.push('/profile/bookmarks')">
        <span class="btn-icon">⭐</span>
        <span class="btn-text">我的收藏</span>
        <span class="btn-count">({{ formatCount(bookmarksTotal) }})</span>
      </button>
      <button class="module-btn" @click="$router.push('/profile/notifications')">
        <span class="btn-icon">🔔</span>
        <span class="btn-text">我的消息</span>
        <span class="btn-count">({{ formatCount(notifications.length) }})</span>
      </button>
    </div>

    <el-card class="mb-5 dark:!bg-gray-800 dark:!border-gray-700 dark:!text-gray-200">
      <template #header>
        <span class="font-semibold text-gray-800 dark:text-gray-200">账号信息</span>
      </template>
      <div class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
        <div class="flex justify-between py-1.5 border-b dark:border-gray-700"><span>账号码</span><span class="text-gray-800 dark:text-gray-200 font-mono">{{ userInfo.account_code }}</span></div>
        <div class="flex justify-between py-1.5 border-b dark:border-gray-700"><span>注册时间</span><span>{{ userInfo.create_time }}</span></div>
        <div class="flex justify-between py-1.5"><span>权限</span><el-tag :type="userInfo.is_admin === 1 ? 'danger' : 'success'" size="small">{{ userInfo.is_admin === 1 ? '管理员' : '普通用户' }}</el-tag></div>
      </div>
      <div class="mt-4 flex gap-2">
        <el-button size="small" @click="$router.push('/settings')">⚙️ 设置</el-button>
        <el-button v-if="userInfo.is_admin === 1" size="small" type="danger" @click="$router.push('/admin')">管理后台</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from '../axios'
import { DEFAULT_AVATAR_SVG } from '../utils/constants'
import { formatCount, getAvatarUrl } from '../utils/helpers'

const userInfo = ref({ username: '用户', account_code: '------', create_time: '----', is_admin: 0 })
const postsTotal = ref(0)
const bookmarksTotal = ref(0)
const notifications = ref([])

const mockUserInfo = { username: '用户', account_code: 'LS20240001', create_time: '2024-01-01', is_admin: 0, avatar: '' }
const mockPostsData = [
  { id: 1, title: 'Vue3 组合式API入门', tag: 'tech', create_time: '2024-01-15', comment_count: 12, like_count: 45 },
  { id: 2, title: '前端性能优化指南', tag: 'tech', create_time: '2024-01-14', comment_count: 8, like_count: 23 },
  { id: 3, title: '周末去哪儿玩？', tag: 'chat', create_time: '2024-01-13', comment_count: 25, like_count: 67 },
  { id: 4, title: 'Python异步编程问题', tag: 'help', create_time: '2024-01-12', comment_count: 5, like_count: 8 },
  { id: 5, title: '我的学习笔记分享', tag: 'tech', create_time: '2024-01-11', comment_count: 15, like_count: 34 },
]
const mockBookmarksData = [
  { id: 1, title: 'Python异步编程详解', user: '张三', create_time: '2024-01-10', comment_count: 18, like_count: 56 },
  { id: 2, title: 'Docker容器化部署实践', user: '李四', create_time: '2024-01-08', comment_count: 32, like_count: 89 },
  { id: 3, title: '前端工程化最佳实践', user: '王五', create_time: '2024-01-05', comment_count: 24, like_count: 72 },
]
const mockNotificationsData = [
  { id: 1, replier: '张三', type: 'post_reply', comment_content: '非常好！', post_title: 'Vue3入门', create_time: '2024-01-15', is_read: false },
  { id: 2, replier: '李四', type: 'mention', comment_content: '@你 提到了你', post_title: '性能优化', create_time: '2024-01-14', is_read: false },
  { id: 3, replier: '王五', type: 'comment_reply', comment_content: '试试这个方法', post_title: 'Python问题', create_time: '2024-01-13', is_read: true },
]

const displayAvatar = computed(() => {
  return getAvatarUrl(userInfo.value.avatar) || DEFAULT_AVATAR_SVG
})

const loadUserInfo = async () => {
  try {
    const res = await axios.get('/api/user/info')
    userInfo.value = res.data.data
  } catch (e) {
    userInfo.value = mockUserInfo
  }
}

const loadPosts = async () => {
  try {
    const res = await axios.get('/api/user/posts', { params: { page: 1, per_page: 10 } })
    postsTotal.value = res.data.total
  } catch (e) {
    postsTotal.value = mockPostsData.length
  }
}

const loadBookmarks = async () => {
  try {
    const res = await axios.get('/api/user/bookmarks', { params: { page: 1, per_page: 10 } })
    bookmarksTotal.value = res.data.total
  } catch (e) {
    bookmarksTotal.value = mockBookmarksData.length
  }
}

const loadNotifications = async () => {
  try {
    const res = await axios.get('/api/notifications')
    notifications.value = res.data.data
  } catch (e) {
    notifications.value = mockNotificationsData
  }
}

onMounted(() => {
  loadUserInfo(); loadPosts(); loadBookmarks(); loadNotifications()
})
</script>

<style scoped>
.flex-row-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
  width: 100%;
}

.module-btn {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-width: 80px;
  padding: 12px 8px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.module-btn:hover {
  border-color: #409eff;
  background: #f0f7ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.btn-icon {
  font-size: 18px;
  line-height: 1;
  margin-bottom: 4px;
}

.btn-text {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  line-height: 1.2;
}

.btn-count {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.2;
}

:deep(.dark) .module-btn {
  background: #1f2937;
  border-color: #374151;
}

:deep(.dark) .module-btn:hover {
  border-color: #60a5fa;
  background: #1e3a5f;
}

:deep(.dark) .btn-text {
  color: #d1d5db;
}

:deep(.dark) .btn-count {
  color: #6b7280;
}
</style>
