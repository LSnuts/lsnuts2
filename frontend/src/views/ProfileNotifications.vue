<template>
  <div class="p-3 md:p-5 max-w-[650px] mx-auto">
    <div class="flex items-center justify-between mb-5">
      <el-button class="back-btn-sm" @click="$router.push('/profile')">← 返回个人中心</el-button>
      <div class="font-semibold text-gray-800 dark:text-gray-200">🔔 我的消息</div>
      <div class="w-24"></div>
    </div>

    <el-card class="dark:!bg-gray-800 dark:!border-gray-700 dark:!text-gray-200">
      <div v-if="notifications.length === 0" class="text-center py-8 text-gray-400 dark:text-gray-500">暂无消息</div>
      <div v-else class="space-y-3">
        <div v-for="n in notifications" :key="n.id" class="p-3 rounded-lg border dark:border-gray-700" :class="n.is_read ? '' : 'bg-blue-50/50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'">
          <div class="text-sm text-gray-800 dark:text-gray-200">
            <span class="font-medium">{{ n.replier }}</span>
            <span class="text-blue-600 dark:text-blue-400 ml-1">{{ n.type === 'post_reply' ? '回复了你的帖子' : n.type === 'mention' ? '在评论中@了你' : '回复了你的评论' }}</span>
          </div>
          <div class="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">{{ n.comment_content }}</div>
          <div class="flex items-center justify-between mt-2">
            <span class="text-xs text-gray-400 dark:text-gray-500">{{ n.post_title }} · {{ n.create_time }}</span>
            <div class="flex gap-1">
              <el-button size="small" @click="goToPost(n)" :disabled="n.post_deleted">{{ n.post_deleted ? '已删除' : '查看' }}</el-button>
              <el-button size="small" type="danger" text @click="deleteNotif(n.id)">🗑</el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const notifications = ref([])

const loadNotifications = async () => {
  try {
    const res = await axios.get('/api/notifications')
    notifications.value = res.data.data
  } catch (e) {
    ElMessage.error('加载失败，请刷新重试')
  }
}

const deleteNotif = async (id) => {
  try {
    await axios.delete(`/api/notifications/${id}`)
  } catch (e) {
    ElMessage.error('删除失败')
  }
  notifications.value = notifications.value.filter(n => n.id !== id)
}

const goToPost = (n) => {
  if (n.post_deleted) return
  router.push(`/forum/detail/${n.post_id}${n.comment_id ? '#comment-' + n.comment_id : ''}`)
}

onMounted(() => { loadNotifications() })
</script>
