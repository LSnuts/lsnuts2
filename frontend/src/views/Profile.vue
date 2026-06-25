<template>
  <div class="p-3 md:p-5 max-w-[650px] mx-auto">
    <div class="flex flex-col items-center mb-5">
      <img :src="displayAvatar" :alt="userInfo.username"
        class="w-[16vw] h-[16vw] max-w-[150px] max-h-[150px] min-w-[80px] min-h-[80px] object-cover rounded-full shadow-lg mb-3 border-4 border-blue-100 dark:border-blue-900" />
      <h1 class="text-2xl font-bold text-gray-800 dark:text-gray-200">{{ userInfo.username }}</h1>
      <div class="flex items-center gap-2 mt-2">
        <el-tag :type="userInfo.is_admin === 1 ? 'danger' : 'success'" size="small">
          {{ userInfo.is_admin === 1 ? '管理员' : '普通用户' }}
        </el-tag>
        <el-tag type="primary" size="small">Lv.{{ getLevel(userInfo.post_count || 0) }}</el-tag>
      </div>
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
        <div class="flex justify-between py-1.5 border-b dark:border-gray-700"><span>发帖数</span><span class="text-gray-800 dark:text-gray-200 font-semibold">{{ userInfo.post_count || 0 }} 帖</span></div>
        <div class="flex justify-between py-1.5 border-b dark:border-gray-700"><span>用户等级</span><span class="text-blue-600 dark:text-blue-400 font-semibold">{{ getLevel(userInfo.post_count || 0) }}级</span></div>
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
import { ElMessage } from 'element-plus'

const userInfo = ref({ username: '用户', account_code: '------', create_time: '----', is_admin: 0, post_count: 0 })
const postsTotal = ref(0)
const bookmarksTotal = ref(0)
const notifications = ref([])

const displayAvatar = computed(() => {
  return getAvatarUrl(userInfo.value.avatar) || DEFAULT_AVATAR_SVG
})

const getLevel = (postCount) => {
  if (postCount >= 500) return 18
  if (postCount >= 300) return 16
  if (postCount >= 150) return 14
  if (postCount >= 80) return 12
  if (postCount >= 40) return 10
  if (postCount >= 20) return 8
  if (postCount >= 10) return 6
  if (postCount >= 5) return 4
  if (postCount >= 2) return 2
  return 1
}

const loadUserInfo = async () => {
  try {
    const res = await axios.get('/api/user/info')
    userInfo.value = res.data.data
  } catch (e) {
    ElMessage.error('加载失败，请刷新重试')
  }
}

const loadPosts = async () => {
  try {
    const res = await axios.get('/api/user/posts', { params: { page: 1, per_page: 10 } })
    postsTotal.value = res.data.total
  } catch (e) {
    ElMessage.error('加载失败，请刷新重试')
  }
}

const loadBookmarks = async () => {
  try {
    const res = await axios.get('/api/user/bookmarks', { params: { page: 1, per_page: 10 } })
    bookmarksTotal.value = res.data.total
  } catch (e) {
    ElMessage.error('加载失败，请刷新重试')
  }
}

const loadNotifications = async () => {
  try {
    const res = await axios.get('/api/notifications')
    notifications.value = res.data.data
  } catch (e) {
    ElMessage.error('加载失败，请刷新重试')
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
