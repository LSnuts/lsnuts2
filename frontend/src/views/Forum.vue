<template>
  <div class="p-3 md:p-5">
    <el-card title="轻量论坛">
      <div class="mb-4 flex flex-col md:flex-row gap-2">
        <el-button type="primary" @click="$router.push('/forum/post')" size="small">✍️ 发新帖</el-button>
        <el-button class="md:ml-2" @click="loadPosts()" size="small">🔄 刷新</el-button>
        <div class="flex-1" />
        <el-input v-model="searchText" placeholder="搜索帖子标题..." size="small" class="!w-full md:!w-[220px]" clearable @input="onSearch">
          <template #prefix><span class="text-gray-400">🔍</span></template>
        </el-input>
      </div>

      <!-- 分类标签 -->
      <div class="mb-4 flex gap-2 flex-wrap">
        <el-button :type="activeTag === '' ? 'primary' : 'default'" size="small" @click="filterTag('')">全部</el-button>
        <el-button :type="activeTag === 'tech' ? 'primary' : 'default'" size="small" @click="filterTag('tech')">💻 技术分享</el-button>
        <el-button :type="activeTag === 'help' ? 'primary' : 'default'" size="small" @click="filterTag('help')">❓ 提问求助</el-button>
        <el-button :type="activeTag === 'chat' ? 'primary' : 'default'" size="small" @click="filterTag('chat')">💬 闲聊灌水</el-button>
        <el-button :type="activeTag === 'other' ? 'primary' : 'default'" size="small" @click="filterTag('other')">📂 其他</el-button>
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

      <!-- 普通帖子列表表格 -->
      <el-table :data="normalPosts" class="w-full">
        <el-table-column label="序号" width="55" type="index" />
        <el-table-column label="标题">
          <template #default="{ row }">
            <span class="forum-title-link" @click="$router.push(`/forum/detail/${row.id}`)">{{ row.title }}</span>
            <el-tag v-if="row.tag" size="small" class="ml-1" :type="tagType(row.tag)">{{ tagLabel(row.tag) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="作者" width="120">
          <template #default="{ row }">
            <span class="dark:text-gray-300">{{ row.user }}</span>
            <el-tag v-if="row.is_admin === 1" type="danger" size="small" class="ml-1">管理员</el-tag>
            <el-tag v-else type="info" size="small" class="ml-1">用户</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="发布时间" width="140" />
        <el-table-column prop="comment_count" label="评论" width="60" />
        <el-table-column label="点赞" width="60">
          <template #default="{ row }">
            <span class="text-red-400">👍 {{ row.like_count }}</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态插图 -->
      <div v-if="posts.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">📭</div>
        <div class="text-gray-400 dark:text-gray-500 text-lg mb-2">暂无帖子</div>
        <el-button type="primary" size="small" @click="$router.push('/forum/post')">✍️ 发第一个帖子</el-button>
      </div>

      <!-- 分页 -->
      <div v-if="total > pageSize" class="flex justify-center mt-4">
        <el-pagination v-model:current-page="currentPage" :page-size="pageSize" :total="total" layout="prev, pager, next" small @current-change="loadPosts" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from '../axios'

const posts = ref([])
const searchText = ref('')
const activeTag = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
let searchTimer = null

const pinnedPosts = computed(() => posts.value.filter(p => p.is_pinned === 1))
const normalPosts = computed(() => posts.value.filter(p => p.is_pinned !== 1))

const filterTag = (tag) => {
  activeTag.value = tag
  currentPage.value = 1
  loadPosts()
}

const tagType = (tag) => {
  const map = { tech: '', help: 'warning', chat: 'success' }
  return map[tag] || 'info'
}

const tagLabel = (tag) => {
  const map = { tech: '技术分享', help: '提问求助', chat: '闲聊灌水' }
  return map[tag] || tag
}

const loadPosts = async () => {
  try {
    const res = await axios.get('/api/forum/list', {
      params: { search: searchText.value, page: currentPage.value, per_page: pageSize.value, tag: activeTag.value }
    })
    posts.value = res.data.data
    total.value = res.data.total || 0
  } catch (e) {}
}

const onSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { currentPage.value = 1; loadPosts() }, 300)
}

onMounted(loadPosts)
</script>

<style scoped>
.forum-title-link {
  color: #2563eb; font-weight: 500; cursor: pointer;
  transition: all 0.15s ease;
}
.forum-title-link:hover { color: #1d4ed8; text-decoration: underline; text-underline-offset: 2px; }
.dark .forum-title-link { color: #60a5fa; }
.dark .forum-title-link:hover { color: #93bbfd; }
</style>
