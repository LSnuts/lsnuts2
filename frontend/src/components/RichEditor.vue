<template>
  <div class="rich-editor-wrapper">
    <!-- 工具栏（横排） -->
    <div class="editor-toolbar">
      <button class="toolbar-btn" title="粗体 Ctrl+B" @mousedown.prevent="wrapSelection('**', '**')">
        <span class="font-bold">B</span>
      </button>
      <button class="toolbar-btn" title="斜体 Ctrl+I" @mousedown.prevent="wrapSelection('*', '*')">
        <span class="font-italic">I</span>
      </button>
      <button class="toolbar-btn" title="删除线" @mousedown.prevent="wrapSelection('~~', '~~')">
        <span class="line-through">S</span>
      </button>
      <button class="toolbar-btn" title="代码" @mousedown.prevent="wrapSelection('`', '`')">
        <span>&lt;/&gt;</span>
      </button>
      <button class="toolbar-btn" title="链接" @mousedown.prevent="insertLink">
        <span>🔗</span>
      </button>
      <div class="toolbar-divider"></div>
      <button class="toolbar-btn" title="@提及用户" @mousedown.prevent="toggleMention">
        <span>@</span>
      </button>
    </div>
    
    <!-- 文本框 -->
    <textarea
      ref="textareaRef"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      @focus="focused = true"
      @blur="focused = false"
      @keydown="onKeydown"
      :placeholder="placeholder"
      :rows="rows"
      class="editor-textarea"
    ></textarea>
    
    <!-- @提及下拉 -->
    <div v-if="mentionVisible && mentionUsers.length > 0" class="mention-dropdown">
      <div v-for="u in mentionUsers" :key="u.id" class="mention-item" @mousedown.prevent="selectMention(u.username)">
        @{{ u.username }}
      </div>
    </div>
    <div v-if="mentionVisible && mentionUsers.length === 0 && mentionQuery" class="mention-dropdown">
      <div class="mention-empty">未找到用户</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from '../axios'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '请输入...' },
  rows: { type: Number, default: 4 }
})
const emit = defineEmits(['update:modelValue'])

const textareaRef = ref(null)
const focused = ref(false)
const mentionVisible = ref(false)
const mentionQuery = ref('')
const mentionUsers = ref([])
let mentionTimer = null

const getCursorPos = (el) => {
  return { start: el.selectionStart, end: el.selectionEnd }
}

const wrapSelection = (before, after) => {
  const el = textareaRef.value
  if (!el) return
  const { start, end } = getCursorPos(el)
  const text = props.modelValue
  const selected = text.substring(start, end)
  const wrapped = before + selected + after
  const newText = text.substring(0, start) + wrapped + text.substring(end)
  emit('update:modelValue', newText)
  setTimeout(() => {
    el.focus()
    if (selected) {
      el.setSelectionRange(start + before.length, start + before.length + selected.length)
    } else {
      el.setSelectionRange(start + before.length, start + before.length)
    }
  }, 0)
}

const insertLink = () => {
  const el = textareaRef.value
  if (!el) return
  const { start, end } = getCursorPos(el)
  const text = props.modelValue
  const selected = text.substring(start, end) || '链接文本'
  const url = prompt('请输入链接地址：', 'https://')
  if (!url) return
  const md = `[${selected}](${url})`
  const newText = text.substring(0, start) + md + text.substring(end)
  emit('update:modelValue', newText)
  setTimeout(() => { el.focus(); el.setSelectionRange(start + md.length, start + md.length) }, 0)
}

const toggleMention = () => {
  const el = textareaRef.value
  if (!el) return
  const { start } = getCursorPos(el)
  const before = props.modelValue.substring(0, start)
  const lastAt = before.lastIndexOf('@')
  if (lastAt >= 0 && !before.substring(lastAt + 1).includes(' ') && !before.substring(lastAt + 1).includes('\n')) {
    const query = before.substring(lastAt + 1)
    mentionQuery.value = query
    searchUsers(query)
    mentionVisible.value = true
  } else {
    const newText = props.modelValue.substring(0, start) + '@' + props.modelValue.substring(start)
    emit('update:modelValue', newText)
    setTimeout(() => { el.focus(); el.setSelectionRange(start + 1, start + 1) }, 0)
  }
}

const searchUsers = async (q) => {
  try {
    const res = await axios.get('/api/user/search', { params: { q } })
    mentionUsers.value = (res.data.data || []).slice(0, 6)
  } catch (e) { mentionUsers.value = [] }
}

const selectMention = (username) => {
  const el = textareaRef.value
  if (!el) return
  const caretPos = el.selectionStart
  const text = props.modelValue
  const before = text.substring(0, caretPos)
  const lastAt = before.lastIndexOf('@')
  const newText = text.substring(0, lastAt) + '@' + username + ' ' + text.substring(caretPos)
  emit('update:modelValue', newText)
  mentionVisible.value = false
  setTimeout(() => {
    el.focus()
    const pos = lastAt + username.length + 2
    el.setSelectionRange(pos, pos)
  }, 0)
}

const onKeydown = (e) => {
  if (mentionVisible.value) {
    if (e.key === 'Escape') { mentionVisible.value = false; return }
    if (e.key === 'Enter' && mentionUsers.value.length > 0) {
      e.preventDefault()
      selectMention(mentionUsers.value[0].username)
      return
    }
  }
  if (e.key === '@') {
    mentionQuery.value = ''
    mentionUsers.value = []
    searchUsers('')
    mentionVisible.value = true
  }
  if (mentionVisible.value && e.key !== '@') {
    clearTimeout(mentionTimer)
    mentionTimer = setTimeout(() => {
      const el = textareaRef.value
      if (!el) return
      const pos = el.selectionStart
      const text = props.modelValue
      const beforeAt = text.lastIndexOf('@', pos - 1)
      if (beforeAt >= 0) {
        const afterAt = text.indexOf(' ', beforeAt)
        const afterNewline = text.indexOf('\n', beforeAt)
        const end = Math.min(afterAt === -1 ? Infinity : afterAt, afterNewline === -1 ? Infinity : afterNewline)
        if (end > pos) {
          const q = text.substring(beforeAt + 1, pos)
          mentionQuery.value = q
          searchUsers(q)
          return
        }
      }
      mentionVisible.value = false
    }, 200)
  }
}

watch(() => props.modelValue, () => {
  if (mentionVisible.value) {
    const el = textareaRef.value
    if (!el) { mentionVisible.value = false; return }
    const pos = el.selectionStart
    const text = props.modelValue
    const beforeAt = text.lastIndexOf('@', pos - 1)
    if (beforeAt < 0 || text.indexOf(' ', beforeAt) < pos) {
      mentionVisible.value = false
    }
  }
})
</script>

<style scoped>
.rich-editor-wrapper {
  position: relative;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
}

.dark .rich-editor-wrapper {
  border-color: #4b5563;
  background: #1f2937;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 6px 12px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  flex-wrap: nowrap;
}

.dark .editor-toolbar {
  background: #374151;
  border-bottom-color: #4b5563;
}

.toolbar-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #4b5563;
  transition: all 0.15s ease;
}

.toolbar-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.dark .toolbar-btn {
  color: #d1d5db;
}

.dark .toolbar-btn:hover {
  background: #4b5563;
  color: #fff;
}

.font-bold { font-weight: bold; }
.font-italic { font-style: italic; }
.line-through { text-decoration: line-through; }

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: #d1d5db;
  margin: 0 4px;
}

.dark .toolbar-divider {
  background: #4b5563;
}

.editor-textarea {
  width: 100%;
  min-height: 120px;
  padding: 12px;
  border: none;
  border-radius: 0 0 8px 8px;
  outline: none;
  resize: vertical;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  background: transparent;
  color: #1f2937;
}

.dark .editor-textarea {
  color: #e5e7eb;
}

.editor-textarea::placeholder {
  color: #9ca3af;
}

.dark .editor-textarea::placeholder {
  color: #6b7280;
}

.mention-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  margin-bottom: 4px;
  width: 200px;
  max-height: 180px;
  overflow-y: auto;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
}

.dark .mention-dropdown {
  background: #1f2937;
  border-color: #4b5563;
}

.mention-item {
  padding: 8px 12px;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
  transition: background 0.15s ease;
}

.mention-item:hover {
  background: #eff6ff;
}

.dark .mention-item {
  color: #d1d5db;
}

.dark .mention-item:hover {
  background: #374151;
}

.mention-empty {
  padding: 12px;
  font-size: 14px;
  color: #9ca3af;
  text-align: center;
}
</style>