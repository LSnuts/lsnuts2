<template>
  <div class="p-3 md:p-5">
    <el-card>
      <template #header>
        <span class="font-bold text-lg">轻量论坛</span>
      </template>

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

      <div class="mb-4 flex gap-2 flex-wrap">
        <el-button :type="activeTag === '' ? 'primary' : 'default'" size="default" @click="filterTag('')">全部</el-button>
        <el-button :type="activeTag === 'tech' ? 'primary' : 'default'" size="default" @click="filterTag('tech')">💻 技术分享</el-button>
        <el-button :type="activeTag === 'help' ? 'primary' : 'default'" size="default" @click="filterTag('help')">❓ 提问求助</el-button>
        <el-button :type="activeTag === 'chat' ? 'primary' : 'default'" size="default" @click="filterTag('chat')">💬 闲聊灌水</el-button>
        <el-button :type="activeTag === 'other' ? 'primary' : 'default'" size="default" @click="filterTag('other')">📂 其他</el-button>
      </div>

      <div v-if="pinnedPosts.length > 0" class="mb-4">
        <div class="flex items-center gap-1 mb-3">
          <span class="inline-block w-1 h-4 bg-orange-400 rounded"></span>
          <span class="text-sm font-semibold text-orange-500">置顶</span>
        </div>
        <div class="space-y-2">
          <div v-for="post in pinnedPosts" :key="post.id" 
               class="post-card pinned-card" @click="$router.push(`/forum/detail/${post.id}`)">
            <div class="post-left-border pinned-border"></div>
            <div class="post-content">
              <div class="flex items-start gap-3">
                <div class="avatar-wrapper flex-shrink-0">
                      <img :src="post.avatar ? API_BASE + post.avatar : DEFAULT_AVATAR_SVG" :alt="post.user" class="post-avatar" />
                    </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 flex-wrap">
                    <span class="font-bold text-gray-800 dark:text-gray-200 truncate">{{ post.title }}</span>
                    <el-tag type="danger" size="small" class="flex-shrink-0">📌 置顶</el-tag>
                    <el-tag v-if="post.tag" size="small" class="flex-shrink-0" :type="tagType(post.tag)">{{ tagLabel(post.tag) }}</el-tag>
                    <el-tag v-if="post.is_admin === 1" type="danger" size="small" class="flex-shrink-0">管理员</el-tag>
                  </div>
                  <div class="flex items-center gap-3 mt-2 text-xs text-gray-500 dark:text-gray-400">
                    <span>{{ post.user }}</span>
                    <span>{{ post.create_time }}</span>
                    <span class="flex items-center gap-1">
                      <span>💬</span>
                      <span>{{ post.comment_count }}</span>
                    </span>
                    <span class="like-count flex items-center gap-1">
                      <span>👍</span>
                      <span class="font-semibold">{{ post.like_count }}</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-infinite-scroll="loadMore" :infinite-scroll-disabled="loading || noMore || posts.length === 0" infinite-scroll-distance="100">
        <template v-if="normalPosts.length > 0">
          <div class="space-y-3">
            <div v-for="post in normalPosts" :key="post.id" 
                 class="post-card" @click="$router.push(`/forum/detail/${post.id}`)">
              <div class="post-left-border" :class="borderColor(post.tag)"></div>
              <div class="post-content">
                <div class="flex items-start gap-3">
                  <div class="avatar-wrapper flex-shrink-0">
                    <img :src="post.avatar || '/static/default_avatar.png'" :alt="post.user" class="post-avatar" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 flex-wrap">
                      <span class="font-medium text-gray-800 dark:text-gray-200 truncate">{{ post.title }}</span>
                      <el-tag v-if="post.tag" size="small" class="flex-shrink-0" :type="tagType(post.tag)">{{ tagLabel(post.tag) }}</el-tag>
                      <el-tag v-if="post.is_admin === 1" type="danger" size="small" class="flex-shrink-0">管理员</el-tag>
                    </div>
                    <div class="flex items-center gap-3 mt-2 text-xs text-gray-500 dark:text-gray-400">
                      <span>{{ post.user }}</span>
                      <span>{{ post.create_time }}</span>
                      <span class="flex items-center gap-1">
                        <span>💬</span>
                        <span>{{ post.comment_count }}</span>
                      </span>
                      <span class="like-count flex items-center gap-1">
                        <span>👍</span>
                        <span class="font-semibold">{{ post.like_count }}</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <div v-if="loading && posts.length > 0" class="text-center py-4">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span class="text-gray-400 text-sm ml-1">加载中...</span>
        </div>

        <div v-if="noMore && posts.length > 0" class="text-center py-4 text-gray-400 text-sm">
          没有更多帖子了
        </div>
      </div>

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
import { API_BASE, DEFAULT_AVATAR_SVG } from '../utils/constants'

const posts = ref([])
const searchText = ref('')
const activeTag = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const noMore = ref(false)
let searchTimer = null

const pinnedPosts = computed(() => posts.value.filter(p => p.is_pinned === 1))
const normalPosts = computed(() => posts.value.filter(p => p.is_pinned !== 1))

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

const borderColor = (tag) => {
  const map = { tech: 'border-blue', help: 'border-orange', chat: 'border-green' }
  return map[tag] || 'border-gray'
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
  loadPosts(false)
})

onUnmounted(() => {
  clearTimeout(searchTimer)
})
</script>

<style scoped>
.post-card {
  position: relative;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  display: flex;
}

.post-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-1px);
}

.post-left-border {
  width: 4px;
  flex-shrink: 0;
  border-radius: 8px 0 0 8px;
}

.post-left-border.border-blue { background: #3b82f6; }
.post-left-border.border-orange { background: #f97316; }
.post-left-border.border-green { background: #22c55e; }
.post-left-border.border-gray { background: #6b7280; }
.post-left-border.pinned-border { background: linear-gradient(180deg, #f97316 0%, #fb923c 100%); }

.post-content {
  flex: 1;
  padding: 16px;
}

.post-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  background: #e5e7eb;
}

.like-count {
  color: #ef4444;
}

.like-count span:last-child {
  font-weight: 600;
}

.pinned-card {
  background: linear-gradient(90deg, rgba(251, 146, 60, 0.05) 0%, white 20%);
}

.dark .post-card {
  background: #1f2937;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.dark .post-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.dark .pinned-card {
  background: linear-gradient(90deg, rgba(251, 146, 60, 0.1) 0%, #1f2937 20%);
}

.dark .like-count {
  color: #f87171;
}
</style>
