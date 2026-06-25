<template>
  <div class="tieba-forum">
    <!-- 面包屑导航 -->
    <div class="breadcrumb-bar">
      <span class="breadcrumb-item" @click="$router.push('/')">首页</span>
      <span class="breadcrumb-sep">›</span>
      <span class="breadcrumb-item current">论坛</span>
    </div>

    <!-- 顶部工具栏 -->
    <div class="forum-toolbar">
      <div class="toolbar-left">
        <el-button type="primary" size="small" @click="$router.push('/forum/post')">
          ✍️ 发新帖
        </el-button>
        <el-button size="small" @click="refreshPosts()">🔄 刷新</el-button>
      </div>
      <div class="toolbar-right">
        <el-input
          v-model="searchText"
          placeholder="搜索帖子标题..."
          size="small"
          class="search-input"
          clearable
          @input="onSearch"
        >
          <template #prefix><span class="text-gray-400">🔍</span></template>
        </el-input>
      </div>
    </div>

    <!-- 分类标签栏 -->
    <div class="tag-bar">
      <span
        v-for="t in tagOptions"
        :key="t.value"
        class="tag-item"
        :class="{ active: activeTag === t.value }"
        @click="filterTag(t.value)"
      >
        {{ t.label }}
      </span>
    </div>

    <!-- 帖子列表表格 -->
    <div class="post-table">
      <!-- 表头 -->
      <div class="table-header">
        <span class="col-status">状态</span>
        <span class="col-title">标题</span>
        <span class="col-author">作者</span>
        <span class="col-reply">回复</span>
        <span class="col-last">最后回复</span>
      </div>

      <!-- 置顶帖 -->
      <div
        v-for="post in pinnedPosts"
        :key="'pin-' + post.id"
        class="table-row pinned-row"
        @click="$router.push(`/forum/detail/${post.id}`)"
      >
        <span class="col-status">
          <span class="status-icon pinned-icon">📌</span>
        </span>
        <span class="col-title">
          <span class="post-title">
            <span class="tag-badge tag-pinned">置顶</span>
            <span v-if="post.tag" class="tag-badge" :class="'tag-' + post.tag">{{ tagLabel(post.tag) }}</span>
            <span class="title-text">{{ post.title }}</span>
          </span>
        </span>
        <span class="col-author">
          <span class="author-name">{{ post.user }}</span>
        </span>
        <span class="col-reply">{{ post.comment_count || 0 }}</span>
        <span class="col-last">{{ formatTime(post) }}</span>
      </div>

      <!-- 分割线（置顶和普通帖之间） -->
      <div v-if="pinnedPosts.length > 0 && normalPosts.length > 0" class="table-divider"></div>

      <!-- 普通帖子 -->
      <div v-infinite-scroll="loadMore" :infinite-scroll-disabled="loading || noMore" infinite-scroll-distance="100">
        <div
          v-for="(post, index) in normalPosts"
          :key="post.id"
          class="table-row"
          :class="{ 'row-zebra': index % 2 === 1 }"
          @click="$router.push(`/forum/detail/${post.id}`)"
        >
          <span class="col-status">
            <span class="status-icon" :class="statusClass(post)">●</span>
          </span>
          <span class="col-title">
            <span class="post-title">
              <span v-if="post.tag" class="tag-badge" :class="'tag-' + post.tag">{{ tagLabel(post.tag) }}</span>
              <span v-if="post.is_admin === 1" class="tag-badge tag-admin">管理</span>
              <span class="title-text">{{ post.title }}</span>
            </span>
          </span>
          <span class="col-author">
            <span class="author-name">{{ post.user }}</span>
          </span>
          <span class="col-reply">{{ post.comment_count || 0 }}</span>
          <span class="col-last">{{ formatTime(post) }}</span>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading && posts.length > 0" class="loading-bar">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>

      <div v-if="noMore && posts.length > 0" class="loading-bar">
        —— 没有更多帖子了 ——
      </div>

      <!-- 空状态 -->
      <div v-if="posts.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-text">暂无帖子</div>
        <el-button type="primary" size="small" @click="$router.push('/forum/post')">
          ✍️ 发第一个帖子
        </el-button>
      </div>
    </div>

    <!-- 统计信息 -->
    <div v-if="posts.length > 0" class="forum-stats">
      共 {{ total }} 个帖子
    </div>
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
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)
const noMore = ref(false)
let searchTimer = null

const tagOptions = [
  { label: '全部', value: '' },
  { label: '💻 技术分享', value: 'tech' },
  { label: '❓ 提问求助', value: 'help' },
  { label: '💬 闲聊灌水', value: 'chat' },
  { label: '📂 其他', value: 'other' },
]

const pinnedPosts = computed(() => posts.value.filter(p => p.is_pinned === 1))
const normalPosts = computed(() => posts.value.filter(p => p.is_pinned !== 1))

const filterTag = (tag) => {
  activeTag.value = tag
  refreshPosts()
}

const tagLabel = (tag) => {
  const map = { tech: '技术', help: '求助', chat: '灌水', other: '其他' }
  return map[tag] || tag
}

const statusClass = (post) => {
  if (post.is_pinned === 1) return 'status-pinned'
  if (post.comment_count >= 10) return 'status-hot'
  return 'status-normal'
}

const formatTime = (post) => {
  const t = post.last_comment_time || post.create_time
  if (!t) return '-'
  const now = new Date()
  const d = new Date(t.replace(' ', 'T'))
  if (d.toDateString() === now.toDateString()) {
    return t.split(' ')[1]?.substring(0, 5) || t
  }
  const parts = t.split(' ')[0]?.split('-')
  if (parts && parts.length >= 3) {
    return `${parts[1]}-${parts[2]}`
  }
  return t
}

const loadPosts = async (append = false) => {
  if (loading.value) return
  loading.value = true
  try {
    const res = await axios.get('/api/forum/list', {
      params: {
        search: searchText.value,
        page: currentPage.value,
        per_page: pageSize.value,
        tag: activeTag.value,
      },
    })
    const newPosts = res.data.data || []
    total.value = res.data.total || 0
    if (append) {
      posts.value.push(...newPosts)
    } else {
      posts.value = newPosts
    }
    noMore.value = posts.value.length >= total.value
  } catch (e) {
    // ignore
  }
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
  searchTimer = setTimeout(() => {
    refreshPosts()
  }, 300)
}

onMounted(() => {
  loadPosts(false)
})

onUnmounted(() => {
  clearTimeout(searchTimer)
})
</script>

<style scoped>
.tieba-forum {
}

/* ---- 面包屑 ---- */
.breadcrumb-bar {
  font-size: 13px;
  color: var(--tieba-text-muted);
  padding: 8px 0;
  margin-bottom: 4px;
}

.breadcrumb-item {
  cursor: pointer;
  color: var(--tieba-link);
}

.breadcrumb-item:hover {
  text-decoration: underline;
}

.breadcrumb-item.current {
  color: var(--tieba-text);
  cursor: default;
}

.breadcrumb-item.current:hover {
  text-decoration: none;
}

.breadcrumb-sep {
  margin: 0 6px;
  color: #ccc;
}

/* ---- 工具栏 ---- */
.forum-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 12px;
  background: var(--tieba-bg-white);
  border: 1px solid var(--tieba-border);
  border-bottom: none;
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  gap: 6px;
}

.toolbar-right {
  display: flex;
  gap: 6px;
}

.search-input {
  width: 200px;
}

.dark .forum-toolbar {
  background: var(--tieba-bg-white);
  border-color: var(--tieba-border);
}

/* ---- 分类标签栏 ---- */
.tag-bar {
  display: flex;
  gap: 0;
  background: #fafafa;
  border: 1px solid var(--tieba-border);
  border-bottom: 2px solid var(--tieba-blue);
  padding: 0;
}

.tag-item {
  padding: 6px 16px;
  font-size: 13px;
  color: var(--tieba-text-light);
  cursor: pointer;
  border-right: 1px solid var(--tieba-border);
  transition: none;
}

.tag-item:hover {
  background: #f0f5ff;
  color: var(--tieba-blue);
}

.tag-item.active {
  background: var(--tieba-blue);
  color: #fff;
}

.tag-item:first-child {
  border-left: none;
}

.dark .tag-bar {
  background: #2a2a2a;
  border-color: var(--tieba-border);
}

.dark .tag-item {
  border-color: var(--tieba-border);
}

.dark .tag-item:hover {
  background: #333;
}

.dark .tag-item.active {
  background: var(--tieba-blue);
  color: #fff;
}

/* ---- 帖子表格 ---- */
.post-table {
  background: var(--tieba-bg-white);
  border: 1px solid var(--tieba-border);
  border-top: none;
}

.dark .post-table {
  background: var(--tieba-bg-white);
  border-color: var(--tieba-border);
}

/* 表头 */
.table-header {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #f5f5f5;
  border-bottom: 1px solid var(--tieba-border);
  font-size: 12px;
  font-weight: bold;
  color: var(--tieba-text-light);
}

.dark .table-header {
  background: #2a2a2a;
  border-color: var(--tieba-border);
}

/* 行 */
.table-row {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: none;
  font-size: 13px;
}

.table-row:hover {
  background: #f0f5ff;
}

.table-row:last-child {
  border-bottom: none;
}

.row-zebra {
  background: #fafafa;
}

.row-zebra:hover {
  background: #f0f5ff;
}

.dark .table-row {
  border-bottom-color: var(--tieba-border);
}

.dark .table-row:hover {
  background: #2a3a4a;
}

.dark .row-zebra {
  background: #262626;
}

/* 置顶行 */
.pinned-row {
  background: var(--tieba-pinned-bg) !important;
}

.pinned-row:hover {
  background: #fff3cd !important;
}

.dark .pinned-row {
  background: #332a1a !important;
}

/* 分割线 */
.table-divider {
  height: 2px;
  background: var(--tieba-border);
}

/* 列宽 */
.col-status {
  width: 36px;
  text-align: center;
  flex-shrink: 0;
}

.col-title {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.col-author {
  width: 90px;
  text-align: center;
  flex-shrink: 0;
  color: var(--tieba-text-light);
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.col-reply {
  width: 50px;
  text-align: center;
  flex-shrink: 0;
  color: var(--tieba-text-muted);
  font-size: 12px;
}

.col-last {
  width: 80px;
  text-align: right;
  flex-shrink: 0;
  color: var(--tieba-text-muted);
  font-size: 12px;
}

/* 状态图标 */
.status-icon {
  font-size: 10px;
}

.status-normal {
  color: #ccc;
}

.status-hot {
  color: #f97316;
}

.status-pinned {
  color: #ef4444;
}

.pinned-icon {
  font-size: 14px;
}

/* 帖子标题 */
.post-title {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  max-width: 100%;
}

.title-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--tieba-text);
}

.title-text:hover {
  color: var(--tieba-blue);
}

/* 标签徽章 */
.tag-badge {
  display: inline-block;
  padding: 0 4px;
  font-size: 11px;
  line-height: 18px;
  border-radius: 2px;
  flex-shrink: 0;
}

.tag-tech {
  background: #e0f0ff;
  color: #2563eb;
}

.tag-help {
  background: #fff3e0;
  color: #e65100;
}

.tag-chat {
  background: #e8f5e9;
  color: #2e7d32;
}

.tag-other {
  background: #f3f3f3;
  color: #666;
}

.tag-pinned {
  background: #fee2e2;
  color: #dc2626;
}

.tag-admin {
  background: #fce4ec;
  color: #c62828;
}

.dark .tag-tech {
  background: #1e3a5f;
  color: #60a5fa;
}

.dark .tag-help {
  background: #4a2c00;
  color: #fb923c;
}

.dark .tag-chat {
  background: #1a3a1a;
  color: #4ade80;
}

.dark .tag-other {
  background: #333;
  color: #aaa;
}

.dark .tag-pinned {
  background: #4a1a1a;
  color: #f87171;
}

.dark .tag-admin {
  background: #4a1a1a;
  color: #ef9a9a;
}

/* 作者名 */
.author-name {
  color: var(--tieba-link);
  font-size: 12px;
}

.author-name:hover {
  text-decoration: underline;
}

/* 加载状态 */
.loading-bar {
  text-align: center;
  padding: 16px;
  font-size: 13px;
  color: var(--tieba-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 48px 16px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-text {
  color: var(--tieba-text-muted);
  font-size: 15px;
  margin-bottom: 16px;
}

/* 统计信息 */
.forum-stats {
  text-align: right;
  padding: 8px 12px;
  font-size: 12px;
  color: var(--tieba-text-muted);
}

/* ---- 移动端适配 ---- */
@media (max-width: 768px) {
  .forum-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-right {
    width: 100%;
  }

  .search-input {
    width: 100% !important;
  }

  .col-author {
    width: 60px;
    font-size: 11px;
  }

  .col-reply {
    width: 36px;
  }

  .col-last {
    width: 60px;
    font-size: 11px;
  }

  .tag-item {
    padding: 6px 10px;
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .col-status {
    display: none;
  }

  .col-author {
    display: none;
  }
}
</style>