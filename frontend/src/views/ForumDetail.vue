<template>
  <div class="tieba-detail" id="forum-detail">
    <!-- 返回按钮 -->
    <div class="detail-top-bar">
      <el-button class="back-btn-sm" @click="$router.back()">← 返回</el-button>
      <div class="breadcrumb-inline">
        <span @click="$router.push('/')">首页</span>
        <span class="bc-sep">›</span>
        <span @click="$router.push('/forum')">论坛</span>
        <span class="bc-sep">›</span>
        <span class="bc-current">帖子详情</span>
      </div>
    </div>

    <!-- 回到顶部 -->
    <transition name="fade">
      <div v-if="showBackTop" class="back-top-btn" @click="scrollToTop">↑</div>
    </transition>

    <!-- 帖子标题区 -->
    <div class="post-header">
      <h2 class="post-main-title">
        <span v-if="post.tag" class="tag-badge" :class="'tag-' + post.tag">{{ tagLabel(post.tag) }}</span>
        {{ post.title }}
      </h2>
      <div class="post-meta">
        <span>楼主：{{ post.user || '匿名用户' }}</span>
        <span class="meta-sep">|</span>
        <span>发布时间：{{ post.create_time }}</span>
        <span v-if="post.edit_count > 0" class="meta-sep">|</span>
        <span v-if="post.edit_count > 0">已编辑 {{ post.edit_count }} 次</span>
      </div>
    </div>

    <!-- ========== 楼层列表 ========== -->

    <!-- #1 楼主帖 -->
    <div class="floor-container" id="floor-1">
      <div class="floor-header">
        <span class="floor-number">#1</span>
        <span class="floor-label">楼主</span>
      </div>
      <div class="floor-body">
        <!-- 左侧用户面板 -->
        <div class="user-panel">
          <img
            :src="getAvatar(post.avatar)"
            :alt="post.user"
            class="user-avatar"
          />
          <div class="user-name">{{ post.user || '匿名用户' }}</div>
          <el-tag v-if="post.is_admin === 1" type="danger" size="small">管理员</el-tag>
        </div>
        <!-- 右侧内容区 -->
        <div class="floor-content">
          <div
            class="post-text markdown-body"
            v-html="renderMd(post.content)"
          ></div>

          <!-- 图片 -->
          <div v-if="post.image" class="post-image-wrap">
            <img :src="API_BASE + post.image" class="post-image" />
          </div>

          <!-- 附件 -->
          <div v-if="post.attachment_name" class="attachment-bar">
            <span class="attach-icon">📎</span>
            <span class="attach-name">{{ post.attachment_name }}</span>
            <a :href="API_BASE + '/api/forum/attachment/' + post.id" class="el-button el-button--primary el-button--small !no-underline">
              📥 下载
            </a>
          </div>

          <!-- 操作栏 -->
          <div class="floor-actions">
            <el-button
              size="small"
              :type="post.user_liked ? 'danger' : 'default'"
              @click="toggleLike"
            >
              {{ post.user_liked ? '已赞' : '👍 点赞' }} {{ post.like_count || 0 }}
            </el-button>
            <el-button
              size="small"
              :type="post.user_bookmarked ? 'warning' : 'default'"
              @click="toggleBookmark"
            >
              {{ post.user_bookmarked ? '⭐ 已收藏' : '☆ 收藏' }}
            </el-button>
            <el-button v-if="canEdit" size="small" type="warning" @click="startEdit">
              ✏️ 编辑
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editVisible" title="编辑帖子" width="90%" top="5vh">
      <el-input v-model="editTitle" placeholder="标题" class="mb-3" />
      <RichEditor v-model="editContent" :rows="8" />
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!editTitle.trim() || !editContent.trim()" @click="submitEdit">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- #2 ~ N 回复楼层 -->
    <div
      v-for="(comment, index) in flatComments"
      :key="comment.id"
      :id="'comment-' + comment.id"
      class="floor-container"
      :class="{ 'highlight-floor': highlightId === comment.id }"
    >
      <div class="floor-header">
        <span class="floor-number">#{{ index + 2 }}</span>
      </div>
      <div class="floor-body">
        <!-- 左侧用户面板 -->
        <div class="user-panel">
          <img
            :src="getAvatar(comment.avatar)"
            :alt="comment.user"
            class="user-avatar"
          />
          <div class="user-name">{{ comment.user || '匿名用户' }}</div>
          <el-tag v-if="comment.is_admin === 1" type="danger" size="small">管理员</el-tag>
        </div>
        <!-- 右侧内容区 -->
        <div class="floor-content">
          <!-- 回复引用（如果是子回复） -->
          <div v-if="comment._replyTo" class="reply-quote">
            回复 {{ comment._replyTo.floor }} 楼（{{ comment._replyTo.user }}）：
            <span class="quote-snippet">{{ comment._replyTo.snippet }}</span>
          </div>

          <div
            class="post-text markdown-body"
            v-html="renderMd(comment.content)"
          ></div>

          <!-- 操作栏 -->
          <div class="floor-actions">
            <el-button size="small" type="primary" @click="handleReply(comment)">
              💬 回复
            </el-button>
            <span class="action-time">{{ comment.create_time }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== 评论区结束 ========== -->

    <!-- 底部快速回复 -->
    <div class="quick-reply">
      <div class="reply-header">💬 发表回复</div>
      <div class="reply-body">
        <RichEditor v-model="replyContent" :rows="4" placeholder="写点什么..." />
        <div class="reply-footer">
          <el-button
            type="primary"
            :disabled="!replyContent.trim()"
            :loading="replying"
            @click="submitReply"
          >
            发表回复
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from '../axios'
import { API_BASE, DEFAULT_AVATAR_SVG } from '../utils/constants'
import { renderMarkdown } from '../markdown.js'
import RichEditor from '../components/RichEditor.vue'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const post = ref({})
const comments = ref([])
const replyContent = ref('')
const replying = ref(false)
const showBackTop = ref(false)
const highlightId = ref(null)
const replyingTo = ref(null)

const editVisible = ref(false)
const editTitle = ref('')
const editContent = ref('')

const canEdit = computed(() => {
  if (!userStore.isLoggedIn) return false
  if (userStore.userInfo.is_admin === 1) return true
  return post.value.user === userStore.userInfo.username
})

const handleReply = (comment) => {
  replyingTo.value = comment
  replyContent.value = `> 回复 @${comment.user}: ${(comment.content || '').substring(0, 50)}\n\n`
  nextTick(() => {
    document.querySelector('.quick-reply')?.scrollIntoView({ behavior: 'smooth' })
  })
}

const renderMd = (text) => renderMarkdown(text || '')

const defaultAvatar =
  'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"%3E%3Crect fill="%239CA3AF" width="48" height="48" rx="4"/%3E%3Ctext fill="white" font-family="sans-serif" font-size="20" font-weight="bold" x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle"%3EU%3C/text%3E%3C/svg%3E'

const getAvatar = (avatarPath) =>
  avatarPath ? API_BASE + avatarPath : defaultAvatar

const tagLabel = (tag) => {
  const map = { tech: '技术', help: '求助', chat: '灌水', other: '其他' }
  return map[tag] || tag
}

const flatComments = computed(() => {
  const result = []
  const flatten = (list, parentInfo = null) => {
    for (const c of list) {
      const item = { ...c }
      if (parentInfo) {
        item._replyTo = parentInfo
      }
      result.push(item)
      if (c.replies && c.replies.length > 0) {
        flatten(c.replies, {
          user: c.user,
          floor: getFloorNumber(c),
          snippet: (c.content || '').substring(0, 50),
        })
      }
    }
  }
  flatten(comments.value)
  return result
})

const getFloorNumber = (comment) => {
  const idx = flatComments.value.findIndex(c => c.id === comment.id)
  return idx !== -1 ? idx + 2 : '-'
}

const loadPost = async () => {
  try {
    const id = route.params.id
    const res = await axios.get(`/api/forum/detail/${id}`)
    post.value = res.data.data?.post || {}
    comments.value = res.data.data?.comments || []
  } catch (e) {
    ElMessage.error('加载帖子失败')
  }
}

const toggleLike = async () => {
  try {
    const res = await axios.post(`/api/forum/like/${post.value.id}`)
    post.value.user_liked = res.data.data?.liked
    post.value.like_count = res.data.data?.like_count
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const toggleBookmark = async () => {
  try {
    const res = await axios.post(`/api/forum/bookmark/${post.value.id}`)
    post.value.user_bookmarked = res.data.data?.bookmarked
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const startEdit = () => {
  editTitle.value = post.value.title
  editContent.value = post.value.content
  editVisible.value = true
}

const submitEdit = async () => {
  try {
    await axios.put(`/api/forum/edit/${post.value.id}`, {
      title: editTitle.value,
      content: editContent.value,
    })
    ElMessage.success('编辑成功')
    editVisible.value = false
    loadPost()
  } catch (e) {
    ElMessage.error('编辑失败')
  }
}

const submitReply = async () => {
  if (!replyContent.value.trim()) return
  replying.value = true
  try {
    await axios.post(`/api/forum/comment/${post.value.id}`, {
      content: replyContent.value,
    })
    ElMessage.success('回复成功')
    replyContent.value = ''
    await loadPost()
    nextTick(() => {
      const floors = document.querySelectorAll('.floor-container')
      if (floors.length > 0) {
        floors[floors.length - 1].scrollIntoView({ behavior: 'smooth' })
      }
    })
  } catch (e) {
    ElMessage.error('回复失败')
  }
  replying.value = false
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleScroll = () => {
  showBackTop.value = window.scrollY > 300
}

onMounted(() => {
  loadPost()
  window.addEventListener('scroll', handleScroll)

  nextTick(() => {
    if (route.hash) {
      const el = document.querySelector(route.hash)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' })
        highlightId.value = parseInt(route.hash.replace('#comment-', ''))
        setTimeout(() => {
          highlightId.value = null
        }, 3000)
      }
    }
  })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.tieba-detail {
  padding-bottom: 24px;
}

/* ---- 顶部工具栏 ---- */
.detail-top-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.breadcrumb-inline {
  font-size: 13px;
  color: var(--tieba-text-muted);
}

.breadcrumb-inline span:not(.bc-sep):not(.bc-current) {
  color: var(--tieba-link);
  cursor: pointer;
}

.breadcrumb-inline span:not(.bc-sep):not(.bc-current):hover {
  text-decoration: underline;
}

.bc-sep {
  margin: 0 4px;
  color: #ccc;
}

.bc-current {
  color: var(--tieba-text);
}

/* ---- 回到顶部 ---- */
.back-top-btn {
  position: fixed;
  bottom: 80px;
  right: 24px;
  width: 36px;
  height: 36px;
  line-height: 36px;
  text-align: center;
  background: var(--tieba-blue);
  color: #fff;
  cursor: pointer;
  font-size: 18px;
  z-index: 100;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

.back-top-btn:hover {
  background: var(--tieba-blue-dark);
}

/* ---- 帖子标题区 ---- */
.post-header {
  background: var(--tieba-bg-white);
  border: 1px solid var(--tieba-border);
  padding: 16px;
  margin-bottom: 0;
}

.post-main-title {
  font-size: 20px;
  font-weight: bold;
  color: var(--tieba-text);
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.post-meta {
  font-size: 12px;
  color: var(--tieba-text-muted);
}

.meta-sep {
  margin: 0 8px;
  color: #ddd;
}

.dark .meta-sep {
  color: #555;
}

/* ---- 标签 ---- */
.tag-badge {
  display: inline-block;
  padding: 0 4px;
  font-size: 11px;
  line-height: 18px;
  border-radius: 2px;
  vertical-align: middle;
  margin-right: 4px;
}

.tag-tech { background: #e0f0ff; color: #2563eb; }
.tag-help { background: #fff3e0; color: #e65100; }
.tag-chat { background: #e8f5e9; color: #2e7d32; }
.tag-other { background: #f3f3f3; color: #666; }

.dark .tag-tech { background: #1e3a5f; color: #60a5fa; }
.dark .tag-help { background: #4a2c00; color: #fb923c; }
.dark .tag-chat { background: #1a3a1a; color: #4ade80; }
.dark .tag-other { background: #333; color: #aaa; }

/* ============================================
   楼层容器 - 核心贴吧样式
   ============================================ */
.floor-container {
  border: 1px solid var(--tieba-border);
  border-top: none;
  background: var(--tieba-bg-white);
  position: relative;
}

.floor-container:first-of-type {
}

.floor-container.highlight-floor {
  background: #fffde7;
}

.dark .floor-container {
  background: var(--tieba-bg-white);
  border-color: var(--tieba-border);
}

.dark .floor-container.highlight-floor {
  background: #333020;
}

/* 楼层头 */
.floor-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #f8f8f8;
  border-bottom: 1px solid #eee;
  font-size: 12px;
  color: var(--tieba-text-muted);
}

.floor-number {
  font-weight: bold;
  color: var(--tieba-text-muted);
}

.floor-label {
  background: var(--tieba-blue);
  color: #fff;
  padding: 0 6px;
  font-size: 11px;
  line-height: 18px;
}

.dark .floor-header {
  background: #2a2a2a;
  border-bottom-color: var(--tieba-border);
}

/* 楼层主体 */
.floor-body {
  display: flex;
  min-height: 100px;
}

/* ---- 左侧用户面板 ---- */
.user-panel {
  width: 130px;
  flex-shrink: 0;
  padding: 16px 8px;
  text-align: center;
  border-right: 1px solid #eee;
  background: #fafafa;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border: 2px solid #e5e5e5;
}

.user-name {
  font-size: 13px;
  font-weight: bold;
  color: var(--tieba-link);
  word-break: break-all;
}

.dark .user-panel {
  background: #2a2a2a;
  border-right-color: var(--tieba-border);
}

.dark .user-avatar {
  border-color: var(--tieba-border);
}

/* ---- 右侧内容区 ---- */
.floor-content {
  flex: 1;
  padding: 16px;
  min-width: 0;
}

.post-text {
  font-size: 14px;
  line-height: 1.8;
  color: var(--tieba-text);
  word-wrap: break-word;
}

.post-image-wrap {
  margin-top: 12px;
}

.post-image {
  max-width: 100%;
  max-height: 400px;
  border: 1px solid var(--tieba-border);
}

/* 附件 */
.attachment-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 8px 12px;
  background: #f0f7ff;
  border: 1px solid #d0e3f7;
  font-size: 13px;
}

.attach-icon {
  font-size: 16px;
}

.attach-name {
  flex: 1;
  color: var(--tieba-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dark .attachment-bar {
  background: #1a2a3a;
  border-color: #2a3a4a;
}

/* 操作栏 */
.floor-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px dashed #e5e5e5;
}

.action-time {
  margin-left: auto;
  font-size: 12px;
  color: var(--tieba-text-muted);
}

.dark .floor-actions {
  border-top-color: #333;
}

/* 回复引用 */
.reply-quote {
  font-size: 12px;
  color: var(--tieba-text-muted);
  border-left: 3px solid #ccc;
  padding: 4px 8px;
  margin-bottom: 10px;
  background: #f9f9f9;
}

.quote-snippet {
  color: #999;
}

.dark .reply-quote {
  background: #2a2a2a;
  border-left-color: #555;
}

/* ---- 快速回复 ---- */
.quick-reply {
  border: 1px solid var(--tieba-border);
  border-top: 2px solid var(--tieba-blue);
  background: var(--tieba-bg-white);
  margin-top: 0;
}

.reply-header {
  padding: 8px 16px;
  font-size: 14px;
  font-weight: bold;
  color: var(--tieba-text);
  background: #f8f8f8;
  border-bottom: 1px solid #eee;
}

.reply-body {
  padding: 16px;
}

.reply-footer {
  text-align: right;
  margin-top: 12px;
}

.dark .quick-reply {
  background: var(--tieba-bg-white);
  border-color: var(--tieba-border);
}

.dark .reply-header {
  background: #2a2a2a;
  border-bottom-color: var(--tieba-border);
}

/* ---- 移动端适配 ---- */
@media (max-width: 768px) {
  .floor-body {
    flex-direction: column;
  }

  .user-panel {
    width: 100%;
    flex-direction: row;
    padding: 8px 12px;
    border-right: none;
    border-bottom: 1px solid #eee;
    gap: 12px;
    justify-content: flex-start;
  }

  .user-avatar {
    width: 40px;
    height: 40px;
  }

  .user-name {
    font-size: 13px;
  }

  .floor-content {
    padding: 12px;
  }

  .post-main-title {
    font-size: 16px;
  }

  .detail-top-bar {
    flex-wrap: wrap;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .user-panel {
    padding: 6px 8px;
  }

  .user-avatar {
    width: 32px;
    height: 32px;
  }
}

/* ---- 过渡动画 ---- */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>