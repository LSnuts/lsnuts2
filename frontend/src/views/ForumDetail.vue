<template>
  <div class="relative p-3 md:p-5 max-w-4xl mx-auto" id="forum-detail">
    <div class="fixed top-4 left-4 z-50">
      <el-button class="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm shadow-md text-gray-600 dark:text-gray-300 hover:text-gray-800 hover:bg-white dark:hover:bg-gray-700" @click="$router.back()">
        ← 返回
      </el-button>
    </div>

    <transition name="fade">
      <div v-if="showBackTop" class="fixed bottom-20 right-6 z-50" @click="scrollToTop">
        <el-button circle size="large" class="shadow-lg !bg-blue-500 !text-white !border-blue-500 hover:!bg-blue-600">↑</el-button>
      </div>
    </transition>

    <el-card class="mb-4 shadow-md">
      <div class="flex items-start justify-between mb-3">
        <div class="flex items-center gap-3">
          <img :src="post.avatar ? 'http://127.0.0.1:5000' + post.avatar : defaultAvatar" :alt="post.user" class="w-6 h-6 object-cover" />
          <div>
            <div class="flex items-center gap-2">
              <span class="font-semibold text-gray-800 dark:text-gray-200">{{ post.user || '匿名用户' }}</span>
              <el-tag v-if="post.is_admin === 1" type="danger" size="small">管理员</el-tag>
              <el-tag v-if="post.tag" size="small" :type="tagType(post.tag)">{{ tagLabel(post.tag) }}</el-tag>
            </div>
            <div class="text-sm text-gray-400">{{ post.create_time }}</div>
          </div>
        </div>
      </div>
      <h2 class="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4 hover:text-blue-600 dark:hover:text-blue-400 transition-colors cursor-default">{{ post.title }}</h2>
      <div class="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap text-base markdown-body" v-html="renderMd(post.content)"></div>

      <div v-if="post.edit_count > 0" class="mt-3 text-xs text-gray-400 dark:text-gray-500">
        已编辑 {{ post.edit_count }} 次 · 最后编辑于 {{ post.last_edit_time }}
      </div>

      <div v-if="post.image" class="mt-4">
        <img :src="'http://127.0.0.1:5000' + post.image" class="max-w-full max-h-[400px] object-contain rounded border" />
      </div>
      <div v-if="post.attachment_name" class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2 min-w-0">
            <span class="text-lg flex-shrink-0">📎</span>
            <span class="text-sm text-gray-700 dark:text-gray-300 font-medium truncate">{{ post.attachment_name }}</span>
          </div>
          <a :href="'http://127.0.0.1:5000/api/forum/attachment/' + post.id" class="el-button el-button--primary el-button--small flex-shrink-0 ml-3 !no-underline">📥 下载附件</a>
        </div>
      </div>

      <div class="mt-4 flex items-center gap-2 flex-wrap">
        <el-button size="small" :type="post.user_liked ? 'danger' : 'default'" @click="toggleLike">
          {{ post.user_liked ? '已赞' : '👍 点赞' }} {{ post.like_count || 0 }}
        </el-button>
        <el-button size="small" :type="post.user_bookmarked ? 'warning' : 'default'" @click="toggleBookmark">
          {{ post.user_bookmarked ? '⭐ 已收藏' : '☆ 收藏' }}
        </el-button>
        <el-button v-if="canEdit" size="small" type="warning" @click="startEdit">✏️ 编辑</el-button>
      </div>

      <el-dialog v-model="editVisible" title="编辑帖子" width="90% max-w-[600px]">
        <el-form :model="editForm" label-width="60px">
          <el-form-item label="标题">
            <el-input v-model="editForm.title" />
          </el-form-item>
          <el-form-item label="分类">
            <el-radio-group v-model="editForm.tag" size="small">
              <el-radio-button value="">📂 其他</el-radio-button>
              <el-radio-button value="tech">💻 技术分享</el-radio-button>
              <el-radio-button value="help">❓ 提问求助</el-radio-button>
              <el-radio-button value="chat">💬 闲聊灌水</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="内容">
            <el-input v-model="editForm.content" type="textarea" :rows="6" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="editVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEdit" :loading="editing">保存修改</el-button>
        </template>
      </el-dialog>
    </el-card>

    <el-card class="shadow-md">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-semibold dark:text-gray-200">评论 ({{ totalCommentCount }})</span>
          <div v-if="comments.length > 3" class="flex gap-1 flex-wrap max-w-[60%] justify-end">
            <el-button v-for="(c, idx) in comments" :key="'nav-'+c.id" size="small" text @click="scrollToComment(c.id)" class="!min-w-[28px] !px-1">{{ idx+1 }}楼</el-button>
          </div>
        </div>
      </template>

      <div class="space-y-4">
        <template v-for="(c, index) in comments" :key="c.id">
          <div :id="'comment-'+c.id" class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-100 dark:border-gray-700 comment-item">
            <div class="flex items-start gap-3">
              <img :src="c.avatar ? 'http://127.0.0.1:5000' + c.avatar : defaultAvatar" :alt="c.user" class="w-[10vw] h-[10vw] max-w-[48px] max-h-[48px] min-w-[24px] min-h-[24px] object-cover flex-shrink-0 mt-0.5 rounded-full" />
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span class="font-medium text-gray-800 dark:text-gray-200">{{ c.user || '匿名用户' }}</span>
                  <el-tag type="info" size="small">{{ index + 1 }}楼</el-tag>
                  <el-tag v-if="c.is_admin === 1" type="danger" size="small">管理员</el-tag>
                  <span class="text-xs text-gray-400 dark:text-gray-500 ml-auto">{{ c.create_time }}</span>
                </div>
                <div class="text-sm leading-relaxed p-3 rounded bg-[#3C4F5C] text-white dark:bg-gray-700 markdown-body" v-html="renderMd(c.content)"></div>
                <div class="mt-2">
                  <el-button size="small" type="primary" class="reply-btn" @click="toggleReply(c)">💬 回复</el-button>
                </div>
                <div v-if="replyTarget === c.id" class="mt-2">
                  <div class="text-xs text-gray-400 dark:text-gray-500 mb-2">↳ 回复 {{ c.user || '匿名用户' }}：</div>
                  <el-input v-model="replyContent[c.id]" type="textarea" :rows="2" placeholder="写下你的回复..." size="small" />
                  <div class="flex justify-end gap-2 mt-2">
                    <el-button size="small" @click="replyTarget = null">取消</el-button>
                    <el-button size="small" type="primary" @click="submitReply(c)">💬 回复</el-button>
                  </div>
                </div>
                <div v-if="c.replies && c.replies.length" class="mt-3 pl-4 border-l-2 border-blue-200 dark:border-blue-800 space-y-2">
                  <div v-for="reply in c.replies" :key="reply.id" class="bg-blue-50/50 dark:bg-gray-750 rounded p-2.5 border border-blue-100 dark:border-gray-700">
                    <div class="flex items-start">
                      <div class="flex-1">
                        <div class="flex items-center gap-1.5 mb-0.5 flex-wrap">
                          <span class="font-medium text-blue-600 dark:text-blue-400 text-xs">{{ reply.user }}</span>
                          <span class="text-[11px] text-gray-400 dark:text-gray-500">回复</span>
                          <span class="font-medium text-gray-700 dark:text-gray-300 text-xs">{{ c.user }}</span>
                          <el-tag v-if="reply.is_admin === 1" type="danger" size="small">管理员</el-tag>
                          <span class="text-[11px] text-gray-400 dark:text-gray-500 ml-auto">{{ reply.create_time }}</span>
                        </div>
                        <div class="text-xs text-gray-600 dark:text-gray-400 leading-relaxed mt-0.5 markdown-body" v-html="renderMd(reply.content)"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <div v-if="comments.length === 0" class="text-center py-10">
        <div class="text-5xl mb-3">💬</div>
        <div class="text-gray-400 dark:text-gray-500">暂无评论，快来发表第一条评论吧！</div>
      </div>

      <div class="mt-6 pt-4 border-t dark:border-gray-700">
        <el-input v-model="content" type="textarea" placeholder="写下你的评论..." :rows="3" resize="none" class="bg-gray-50 dark:bg-gray-800 rounded-lg" />
        <div class="flex justify-end gap-2 mt-3">
          <el-button @click="$router.back()" size="default">返回</el-button>
          <el-button type="primary" @click="sendComment" size="default">💬 发布评论</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../axios'
import { ElMessage } from 'element-plus'
import { renderMarkdown } from '../markdown.js'
import { tagType, tagLabel } from '../utils/helpers'

const route = useRoute()
const router = useRouter()
const post = ref({})
const comments = ref([])
const content = ref('')
const replyContent = reactive({})
const replyTarget = ref(null)
const editVisible = ref(false)
const editing = ref(false)
const editForm = ref({ title: '', content: '', tag: '' })
const showBackTop = ref(false)
const currentUserId = ref(null)

const defaultAvatar = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"%3E%3Crect fill="%239CA3AF" width="24" height="24" rx="2"/%3E%3Ctext fill="white" font-family="sans-serif" font-size="12" font-weight="bold" x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle"%3EU%3C/text%3E%3C/svg%3E'

const renderMd = (text) => renderMarkdown(text)

const canEdit = computed(() => {
  return post.value.user_id && currentUserId.value && post.value.user_id === currentUserId.value
})

const countReplies = (commentList) => {
  let count = 0
  for (const c of commentList) { count += 1; if (c.replies) count += c.replies.length }
  return count
}

const totalCommentCount = computed(() => countReplies(comments.value))

const clearReplyContent = () => {
  Object.keys(replyContent).forEach(key => delete replyContent[key])
}

const getDetail = async () => {
  try {
    const res = await axios.get(`/api/forum/detail/${route.params.id}`)
    post.value = res.data.data.post
    post.value.user_id = res.data.data.post.user_id
    currentUserId.value = res.data.data.current_user_id
    comments.value = res.data.data.comments
    clearReplyContent()
    replyTarget.value = null
  } catch (e) {}
  nextTick(() => {
    const hash = route.hash || window.location.hash
    if (hash && hash.startsWith('#comment-')) { scrollToEl(hash.slice(1)) }
  })
}

const scrollToEl = (id) => {
  const el = document.getElementById(id)
  if (el) { el.scrollIntoView({ behavior: 'smooth', block: 'center' }); el.classList.add('highlight-comment'); setTimeout(() => el.classList.remove('highlight-comment'), 2000) }
}

const scrollToComment = (commentId) => {
  const el = document.getElementById('comment-' + commentId)
  if (el) { el.scrollIntoView({ behavior: 'smooth', block: 'center' }); el.classList.add('highlight-comment'); setTimeout(() => el.classList.remove('highlight-comment'), 2000) }
}

const scrollToTop = () => { window.scrollTo({ top: 0, behavior: 'smooth' }) }
const onScroll = () => { showBackTop.value = window.scrollY > 400 }

const toggleLike = async () => {
  try {
    const res = await axios.post(`/api/forum/like/${route.params.id}`)
    post.value.like_count = res.data.data.like_count
    post.value.user_liked = res.data.data.liked
    ElMessage.success(res.data.msg)
  } catch (e) { ElMessage.error(e.response?.data?.msg || '操作失败') }
}

const toggleBookmark = async () => {
  try {
    const res = await axios.post(`/api/forum/bookmark/${route.params.id}`)
    post.value.user_bookmarked = res.data.data.bookmarked
    ElMessage.success(res.data.msg)
  } catch (e) { ElMessage.error(e.response?.data?.msg || '操作失败') }
}

const startEdit = () => {
  editForm.value.title = post.value.title; editForm.value.content = post.value.content; editForm.value.tag = post.value.tag || ''; editVisible.value = true
}

const submitEdit = async () => {
  if (!editForm.value.title.trim() || !editForm.value.content.trim()) { ElMessage.warning('标题和内容不能为空'); return }
  editing.value = true
  try {
    await axios.put(`/api/forum/post/${route.params.id}`, editForm.value)
    ElMessage.success('编辑成功')
    editVisible.value = false; getDetail()
  } catch (e) { ElMessage.error(e.response?.data?.msg || '编辑失败') }
  finally { editing.value = false }
}

const sendComment = async () => {
  if (!content.value.trim()) { ElMessage.warning('请输入评论内容'); return }
  await axios.post(`/api/forum/comment/${route.params.id}`, { content: content.value })
  ElMessage.success('评论成功')
  content.value = ''; getDetail()
}

const toggleReply = (c) => {
  replyTarget.value = replyTarget.value === c.id ? null : c.id
  if (replyTarget.value && !replyContent[c.id]) replyContent[c.id] = ''
}

const submitReply = async (c) => {
  if (!(replyContent[c.id] || '').trim()) { ElMessage.warning('请输入回复内容'); return }
  await axios.post(`/api/forum/comment/${route.params.id}`, { content: replyContent[c.id], parent_id: c.id })
  ElMessage.success('回复成功')
  replyContent[c.id] = ''; replyTarget.value = null; getDetail()
}

onMounted(() => { getDetail(); window.addEventListener('scroll', onScroll) })
watch(() => route.params.id, () => { if (route.params.id) getDetail() })
</script>

<style scoped>
.comment-item { transition: background-color 0.5s ease; }
.comment-item.highlight-comment { background-color: #fbbf24 !important; }
.dark .comment-item.highlight-comment { background-color: #78350f !important; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.markdown-body :deep(a) { color: #60a5fa; text-decoration: underline; }
.markdown-body :deep(code) { background: rgba(0,0,0,0.15); padding: 1px 4px; border-radius: 3px; font-size: 0.9em; }
.markdown-body :deep(img) { max-width: 100%; border-radius: 6px; }
.reply-btn {
  border-radius: 4px;
  padding: 4px 12px;
  font-size: 12px;
  border: 1px solid #409eff;
  background: #ecf5ff;
}
.dark .reply-btn {
  background: #1e3a5f;
}
</style>
