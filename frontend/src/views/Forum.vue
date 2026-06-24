<template>
  <div class="p-3 md:p-5">
    <el-card>
      <template #header>
        <span class="font-bold text-lg">轻量论坛</span>
      </template>

      <!-- 操作栏 -->
      <div class="mb-4 flex flex-col sm:flex-row gap-2">
        <div class="flex gap-2">
          <el-button type="primary" @click="$router.push('/forum/post')" size="default">✍️ 发新帖</el-button>
          <el-button @click="refreshPosts()" size="default">🔄 刷新</el-button>
        </div>
        <div class="flex-1" />
        <el-input v-model="searchText" placeholder="搜索帖子标题..." size="default" class="!w-full sm:!w-[220px]" clearable @input="onSearch">
          <template #prefix><span class="text-gray-400">🔍</span></template>
        </el-input>
      </div>

      <!-- 分类标签 -->
      <div class="mb-4 flex gap-2 flex-wrap">
        <el-button :type="activeTag === '' ? 'primary' : 'default'" size="default" @click="filterTag('')">全部</el-button>
        <el-button :type="activeTag === 'tech' ? 'primary' : 'default'" size="default" @click="filterTag('tech')">💻 技术分享</el-button>
        <el-button :type="activeTag === 'help' ? 'primary' : 'default'" size="default" @click="filterTag('help')">❓ 提问求助</el-button>
        <el-button :type="activeTag === 'chat' ? 'primary' : 'default'" size="default" @click="filterTag('chat')">💬 闲聊灌水</el-button>
        <el-button :type="activeTag === 'other' ? 'primary' : 'default'" size="default" @click="filterTag('other')">📂 其他</el-button>
      </div>

      <!-- 置顶帖子区 -->
      <div v-if="pinnedPosts.length > 0" class="mb-4">
        <div class="flex items-center gap-1 mb-2">
          <span class="inline-block w-1 h-4 bg-orange-400 rounded"></span>
          <span class="text-sm font-semibold text-orange-500">置顶</span>
        </div>
        <div class="space-y-1">
          <div v-for="post in pinnedPosts" :key="post.id" class="flex items-center px-3 py-2 bg-orange-50 dark:bg-orange-900/20 rounded border border-orange-200 dark:border-orange-800 hover:bg-orange-100 dark:hover:bg-orange-900/30 cursor-pointer transition-colors" @click="$router.push(`/forum/detail/${post.id}`)">
            <span class="text-orange-500 mr-2 flex-shrink-0">📌</span>
            <span class="font-medium text-gray-800 dark:text-gray-200 truncate flex-1">{{ post.title }}</span>
            <span class="text-xs text-gray-400 dark:text-gray-500 flex-shrink-0 ml-3">{{ post.user }}</span>
            <span v-if="post.is_admin === 1" class="flex-shrink-0 ml-1"><el-tag type="danger" size="small">管理员</el-tag></span>
            <span class="text-xs text-gray-400 dark:text-gray-500 flex-shrink-0 ml-3">{{ post.create_time }}</span>
            <span class="text-xs text-gray-400 dark:text-gray-500 flex-shrink-0 ml-3">💬 {{ post.comment_count }}</span>
            <span class="text-xs text-red-400 dark:text-red-300 flex-shrink-0 ml-2">👍 {{ post.like_count }}</span>
          </div>
        </div>
      </div>

      <!-- 普通帖子列表（无限滚动） -->
      <div v-infinite-scroll="loadMore" :infinite-scroll-disabled="loading || noMore || posts.length === 0" infinite-scroll-distance="100">
        <template v-if="normalPosts.length > 0">
          <!-- PC端：表格列表 -->
          <el-table v-if="!isMobile" :data="normalPosts" class="w-full">
            <el-table-column label="标题" min-width="200">
              <template #default="{ row }">
                <span class="forum-title-link" @click="$router.push(`/forum/detail/${row.id}`)">{{ row.title }}</span>
                <el-tag v-if="row.tag" size="small" class="ml-1" :type="tagType(row.tag)">{{ tagLabel(row.tag) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="作者" width="140">
              <template #default="{ row }">
                <span class="dark:text-gray-300">{{ row.user }}</span>
                <el-tag v-if="row.is_admin === 1" type="danger" size="small" class="ml-1">管理员</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="发布时间" width="150" />
            <el-table-column prop="comment_count" label="评论" width="60" align="center" />
            <el-table-column label="点赞" width="70" align="center">
              <template #default="{ row }">
                <span class="text-red-400">👍 {{ row.like_count }}</span>
              </template>
            </el-table-column>
          </el-table>

          <!-- 手机端：卡片列表 -->
          <div v-else>
            <div v-for="post in normalPosts" :key="post.id" class="post-card mb-3 p-3 rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-800" @click="$router.push(`/forum/detail/${post.id}`)">
              <div class="flex items-start justify-between gap-2">
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-gray-800 dark:text-gray-200 truncate">{{ post.title }}</div>
                  <div class="flex items-center gap-1 mt-1 flex-wrap">
                    <el-tag v-if="post.tag" size="small" :type="tagType(post.tag)">{{ tagLabel(post.tag) }}</el-tag>
                    <span class="text-xs text-gray-500 dark:text-gray-400">{{ post.user }}</span>
                    <el-tag v-if="post.is_admin === 1" type="danger" size="small">管理员</el-tag>
                  </div>
                </div>
                <div class="flex-shrink-0 text-right">
                  <div class="text-xs text-gray-400 dark:text-gray-500">{{ post.create_time }}</div>
                  <div class="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    💬 {{ post.comment_count }} &nbsp; 👍 {{ post.like_count }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- 加载中 -->
        <div v-if="loading && posts.length > 0" class="text-center py-4">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span class="text-gray-400 text-sm ml-1">加载中...</span>
        </div>

        <!-- 没有更多 -->
        <div v-if="noMore && posts.length > 0" class="text-center py-4 text-gray-400 text-sm">
          没有更多帖子了
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="posts.length === 0 && !loading" class="text-center py-12">
        <div class="text-6xl mb-4">📭</div>
        <div class="text-gray-400 dark:text-gray-500 text-lg mb-2">暂无帖子</div>
        <el-button type="primary" size="default" @click="$router.push('/forum/post')">✍️ 发第一个帖子</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import axios from '../axios'

const posts = ref([])
const searchText = ref('')
const activeTag = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const noMore = ref(false)
const isMobile = ref(false)
let searchTimer = null

const pinnedPosts = computed(() => posts.value.filter(p => p.is_pinned === 1))
const normalPosts = computed(() => posts.value.filter(p => p.is_pinned !== 1))

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

const filterTag = (tag) => {
  activeTag.value = tag
  refreshPosts()
}

const tagType = (tag) => {
  const map = { tech: '', help: 'warning', chat: 'success' }
  return map[tag] || 'info'
}

const tagLabel = (tag) => {
  const map = { tech: '技术分享', help: '提问求助', chat: '闲聊灌水' }
  return map[tag] || tag
}

const loadPosts = async (append = false) => {
  if (loading.value) return
  loading.value = true
  try {
    const res = await axios.get('/api/forum/list', {
      params: { search: searchText.value, page: currentPage.value, per_page: pageSize.value, tag: activeTag.value }
    })
    const newPosts = res.data.data || []
    total.value = res.data.total || 0
    if (append) {
      posts.value.push(...newPosts)
    } else {
      posts.value = newPosts
    }
    noMore.value = posts.value.length >= total.value
  } catch (e) {}
  loading.value = false
}

const refreshPosts = () => {
  currentPage.value = 1
  noMore.value = false
  loadPosts(false)
}

const loadMore = () => {
  if (noMore.value || loading.value) return
  currentPage.value++
  loadPosts(true)
}

const onSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { refreshPosts() }, 300)
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  loadPosts(false)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.forum-title-link {
  color: #2563eb; font-weight: 500; cursor: pointer;
  transition: all 0.15s ease;
}
.forum-title-link:hover { color: #1d4ed8; text-decoration: underline; text-underline-offset: 2px; }
.dark .forum-title-link { color: #60a5fa; }
.dark .forum-title-link:hover { color: #93bbfd; }

.post-card {
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.post-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-1px);
}
.dark .post-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
</style>
