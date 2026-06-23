<template>
  <div class="p-3 md:p-5 max-w-[650px] mx-auto">
    <div class="flex items-center justify-between mb-5">
      <el-button class="back-btn-sm" @click="$router.push('/profile')">← 返回个人中心</el-button>
      <div class="font-semibold text-gray-800 dark:text-gray-200">📝 我的帖子</div>
      <div class="w-24"></div>
    </div>

    <div v-if="posts.length === 0" class="bg-white dark:bg-gray-800 rounded-xl p-8 text-center border dark:border-gray-700">
      <div class="text-4xl mb-3">📭</div>
      <div class="text-gray-500 dark:text-gray-400">暂无帖子</div>
      <div class="text-sm text-gray-400 dark:text-gray-500 mt-1">快来发布你的第一个帖子吧！</div>
    </div>

    <div v-else class="space-y-4">
      <div v-for="p in posts" :key="p.id" class="post-card">
        <div class="flex items-start gap-3">
          <div class="flex-1 min-w-0 cursor-pointer" @click="$router.push(`/forum/detail/${p.id}`)">
            <div class="flex items-center gap-2 mb-2">
              <span class="font-medium text-gray-800 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 transition-colors truncate">{{ p.title }}</span>
              <el-tag v-if="p.tag" size="small" :type="tagType(p.tag)">{{ tagLabel(p.tag) }}</el-tag>
            </div>
            <div class="text-sm text-gray-500 dark:text-gray-400">{{ p.create_time }}</div>
          </div>
          <div class="flex items-center gap-3 flex-shrink-0">
            <div class="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
              <span>💬{{ p.comment_count }}</span>
              <span>👍{{ p.like_count }}</span>
            </div>
            <el-button size="small" type="danger" @click.stop="deletePost(p.id)" class="delete-btn">🗑</el-button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="postsTotal > posts.length" class="text-center mt-5">
      <el-button size="small" @click="loadPosts(postsPage + 1)" :loading="loadingPosts">加载更多</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { tagType, tagLabel } from '../utils/helpers'

const posts = ref([])
const postsTotal = ref(0)
const postsPage = ref(1)
const loadingPosts = ref(false)

const loadPosts = async (page = 1) => {
  loadingPosts.value = true
  try {
    const res = await axios.get('/api/user/posts', { params: { page, per_page: 10 } })
    if (page === 1) { posts.value = res.data.data } else { posts.value.push(...res.data.data) }
    postsTotal.value = res.data.total; postsPage.value = page
  } catch (e) {
    ElMessage.error('加载失败，请刷新重试')
  } finally { loadingPosts.value = false }
}

const deletePost = async (postId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个帖子吗？', '确认删除', { type: 'warning' })
    await axios.delete(`/api/forum/post/${postId}`)
    ElMessage.success('已删除')
    loadPosts(postsPage.value)
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => { loadPosts() })
</script>

<style scoped>
.post-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s ease;
}

.post-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.1);
  transform: translateY(-1px);
}

.dark .post-card {
  background: #1f2937;
  border-color: #374151;
}

.dark .post-card:hover {
  border-color: #60a5fa;
}

.delete-btn {
  padding: 4px 8px;
  opacity: 0.6;
}

.delete-btn:hover {
  opacity: 1;
}
</style>
