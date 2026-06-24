<template>
  <div class="p-3 md:p-5 max-w-[650px] mx-auto">
    <div class="flex items-center justify-between mb-5">
      <el-button class="back-btn-sm" @click="$router.push('/profile')">← 返回个人中心</el-button>
      <div class="font-semibold text-gray-800 dark:text-gray-200">⭐ 我的收藏</div>
      <div class="w-24"></div>
    </div>

    <el-card class="dark:!bg-gray-800 dark:!border-gray-700 dark:!text-gray-200">
      <div v-if="bookmarks.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">⭐</div>
        <div class="text-gray-400 dark:text-gray-500 text-lg mb-2">暂无收藏</div>
        <div class="text-sm text-gray-400 dark:text-gray-500 mb-4">看到喜欢的帖子，点击收藏按钮即可保存到这里</div>
        <el-button type="primary" size="small" @click="$router.push('/forum')">去论坛逛逛</el-button>
      </div>
      <div v-else class="space-y-3">
        <div v-for="b in bookmarks" :key="b.id" class="p-3 rounded-lg border dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer" @click="$router.push(`/forum/detail/${b.id}`)">
          <div class="text-sm font-medium text-gray-800 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 transition-colors truncate">{{ b.title }}</div>
          <div class="flex items-center gap-3 mt-1 text-xs text-gray-500 dark:text-gray-400">
            <span>作者：{{ b.user }}</span>
            <span>{{ b.create_time }}</span>
            <span>💬{{ b.comment_count }}</span>
            <span>👍{{ b.like_count }}</span>
          </div>
        </div>
      </div>
      <div v-if="bookmarksTotal > bookmarks.length" class="text-center mt-4">
        <el-button size="small" @click="loadBookmarks(bookmarksPage + 1)" :loading="loadingBookmarks">加载更多</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../axios'
import { ElMessage } from 'element-plus'

const bookmarks = ref([])
const bookmarksTotal = ref(0)
const bookmarksPage = ref(1)
const loadingBookmarks = ref(false)

const loadBookmarks = async (page = 1) => {
  loadingBookmarks.value = true
  try {
    const res = await axios.get('/api/user/bookmarks', { params: { page, per_page: 10 } })
    if (page === 1) { bookmarks.value = res.data.data } else { bookmarks.value.push(...res.data.data) }
    bookmarksTotal.value = res.data.total; bookmarksPage.value = page
  } catch (e) {
    ElMessage.error('加载失败，请刷新重试')
  } finally { loadingBookmarks.value = false }
}

onMounted(() => { loadBookmarks() })
</script>
