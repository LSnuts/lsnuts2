<template>
  <div class="comment-tree">
    <div
      v-for="comment in comments"
      :key="comment.id"
      :id="'comment-' + comment.id"
      class="comment-item"
      :class="{ 'highlight-comment': highlightId === comment.id }"
    >
      <div class="comment-main">
        <div class="flex items-start gap-3">
          <img
            :src="getAvatar(comment.avatar)"
            :alt="comment.user"
            class="w-[10vw] h-[10vw] max-w-[48px] max-h-[48px] min-w-[24px] min-h-[24px] object-cover flex-shrink-0 mt-0.5 rounded-full"
          />
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="font-medium text-gray-800 dark:text-gray-200">
                {{ comment.user || '匿名用户' }}
              </span>
              <el-tag type="info" size="small">{{ getFloor(comment) }}</el-tag>
              <el-tag v-if="comment.is_admin === 1" type="danger" size="small">
                管理员
              </el-tag>
              <span class="text-xs text-gray-400 dark:text-gray-500 ml-auto">
                {{ comment.create_time }}
              </span>
            </div>
            <div
              class="text-sm leading-relaxed p-3 rounded bg-gray-100 dark:bg-gray-700 markdown-body"
              v-html="renderMd(comment.content)"
            ></div>
            <div class="mt-2 flex items-center gap-2">
              <el-button
                size="small"
                type="primary"
                class="reply-btn"
                @click="$emit('reply', comment)"
              >
                💬 回复
              </el-button>
              <el-button
                v-if="comment.replies && comment.replies.length"
                size="small"
                text
                @click="toggleCollapse(comment.id)"
              >
                {{ collapsedIds.includes(comment.id) ? '展开' : '收起' }}
                ({{ comment.replies.length }})
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="comment.replies && comment.replies.length && !collapsedIds.includes(comment.id)"
        class="comment-children"
      >
        <CommentTree
          :comments="comment.replies"
          :parent-comment="comment"
          :all-comments="allComments"
          :highlight-id="highlightId"
          @reply="$emit('reply', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { renderMarkdown } from '../markdown.js'
import { API_BASE } from '../utils/constants'

const props = defineProps({
  comments: {
    type: Array,
    required: true
  },
  parentComment: {
    type: Object,
    default: null
  },
  allComments: {
    type: Array,
    default: () => []
  },
  highlightId: {
    type: Number,
    default: null
  }
})

defineEmits(['reply'])

const collapsedIds = ref([])

const renderMd = (text) => renderMarkdown(text)

const defaultAvatar =
  'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"%3E%3Crect fill="%239CA3AF" width="24" height="24" rx="2"/%3E%3Ctext fill="white" font-family="sans-serif" font-size="12" font-weight="bold" x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle"%3EU%3C/text%3E%3C/svg%3E'

const getAvatar = (avatarPath) =>
  avatarPath ? API_BASE + avatarPath : defaultAvatar

const getFloor = (comment) => {
  if (!props.allComments.length) return '-'
  const index = props.allComments.findIndex((c) => c.id === comment.id)
  return index !== -1 ? index + 1 : '-'
}

const toggleCollapse = (id) => {
  const index = collapsedIds.value.indexOf(id)
  if (index === -1) {
    collapsedIds.value.push(id)
  } else {
    collapsedIds.value.splice(index, 1)
  }
}
</script>

<style scoped>
.comment-item {
  transition: background-color 0.3s ease;
  padding-bottom: 16px;
}

.comment-item:last-child {
  padding-bottom: 0;
}

.comment-item.highlight-comment {
  background-color: rgba(251, 191, 36, 0.2);
  border-radius: 8px;
  padding: 12px;
}

.comment-main {
  background: gray-50 dark:bg-gray-800;
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid var(--border-color);
}

.comment-children {
  margin-left: 40px;
  margin-top: 12px;
  padding-left: 12px;
  border-left: 2px solid var(--border-color);
}

.reply-btn {
  border-radius: 4px;
  padding: 4px 12px;
  font-size: 12px;
}

.markdown-body :deep(a) {
  color: #60a5fa;
  text-decoration: underline;
}

.markdown-body :deep(code) {
  background: rgba(0, 0, 0, 0.15);
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 0.9em;
}

.markdown-body :deep(img) {
  max-width: 100%;
  border-radius: 6px;
}
</style>
