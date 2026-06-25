<template>
  <div class="tieba-post">
    <!-- 面包屑导航 -->
    <div class="breadcrumb-bar">
      <span class="breadcrumb-item" @click="$router.push('/')">首页</span>
      <span class="breadcrumb-sep">›</span>
      <span class="breadcrumb-item" @click="$router.push('/forum')">论坛</span>
      <span class="breadcrumb-sep">›</span>
      <span class="breadcrumb-item current">发表新帖</span>
    </div>

    <!-- 发帖卡片 -->
    <div class="post-card">
      <div class="card-header">
        <span class="card-title">✍️ 发表新帖</span>
      </div>

      <div class="card-body">
        <!-- 标题输入 -->
        <div class="form-group">
          <label class="form-label">标题</label>
          <el-input
            v-model="form.title"
            placeholder="请输入帖子标题"
            class="form-input"
            size="large"
          />
        </div>

        <!-- 分类选择 -->
        <div class="form-group">
          <label class="form-label">分类</label>
          <div class="tag-selector">
            <span
              v-for="tag in tagOptions"
              :key="tag.value"
              class="tag-option"
              :class="{ active: form.tag === tag.value }"
              @click="form.tag = tag.value"
            >
              {{ tag.icon }} {{ tag.label }}
            </span>
          </div>
        </div>

        <!-- 内容编辑器 -->
        <div class="form-group">
          <label class="form-label">内容</label>
          <RichEditor
            v-model="form.content"
            placeholder="请输入帖子内容... 支持 Markdown 格式"
            :rows="8"
            class="form-editor"
          />
        </div>

        <!-- 图片上传 -->
        <div class="form-group">
          <label class="form-label">图片</label>
          <div class="upload-area">
            <div class="upload-btn" @click="triggerImageInput">
              <span class="upload-icon">📷</span>
              <span class="upload-text">选择图片</span>
            </div>
            <input
              ref="imageInput"
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
              class="hidden"
              @change="onImageChange"
            />
            <div v-if="imageFile" class="upload-preview">
              <img :src="imagePreview" class="preview-image" />
              <span class="preview-name">{{ imageFile.name }}</span>
              <span class="preview-remove" @click="removeImage">✕</span>
            </div>
            <span v-if="!imageFile" class="upload-hint">支持 jpg、png、gif、webp 格式，最大 10M</span>
          </div>
        </div>

        <!-- 附件上传 -->
        <div class="form-group">
          <label class="form-label">附件</label>
          <div class="upload-area">
            <div class="upload-btn" @click="triggerAttachInput">
              <span class="upload-icon">📎</span>
              <span class="upload-text">选择附件</span>
            </div>
            <input
              ref="attachInput"
              type="file"
              class="hidden"
              @change="onAttachChange"
            />
            <div v-if="attachFile" class="attach-preview">
              <span class="attach-icon">📄</span>
              <span class="attach-name">{{ attachFile.name }}</span>
              <span class="attach-remove" @click="removeAttach">✕</span>
            </div>
            <span v-if="!attachFile" class="upload-hint">最大 10M</span>
          </div>
        </div>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            :disabled="!canSubmit"
            @click="submit"
          >
            🚀 发布帖子
          </el-button>
          <el-button size="large" @click="$router.back()">
            ← 返回
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../axios'
import { ElMessage } from 'element-plus'
import RichEditor from '../components/RichEditor.vue'

const router = useRouter()
const form = ref({ title: '', content: '', tag: '' })
const loading = ref(false)
const imageFile = ref(null)
const imagePreview = ref('')
const attachFile = ref(null)
const imageInput = ref(null)
const attachInput = ref(null)

const tagOptions = [
  { value: '', label: '其他', icon: '📂' },
  { value: 'tech', label: '技术分享', icon: '💻' },
  { value: 'help', label: '提问求助', icon: '❓' },
  { value: 'chat', label: '闲聊灌水', icon: '💬' },
]

const canSubmit = computed(() => {
  return form.value.title.trim().length >= 2 && form.value.content.trim().length >= 2
})

const triggerImageInput = () => {
  imageInput.value?.click()
}

const triggerAttachInput = () => {
  attachInput.value?.click()
}

const onImageChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.warning('图片大小不能超过10M')
    return
  }
  imageFile.value = file
  imagePreview.value = URL.createObjectURL(file)
}

const removeImage = () => {
  imageFile.value = null
  imagePreview.value = ''
}

const onAttachChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.warning('附件大小不能超过10M')
    return
  }
  attachFile.value = file
}

const removeAttach = () => {
  attachFile.value = null
}

const submit = async () => {
  if (!canSubmit.value) {
    ElMessage.warning('标题和内容不能为空')
    return
  }
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('title', form.value.title)
    formData.append('content', form.value.content)
    formData.append('tag', form.value.tag)
    if (imageFile.value) {
      formData.append('image', imageFile.value)
    }
    if (attachFile.value) {
      formData.append('attachment', attachFile.value)
    }

    const res = await axios.post('/api/forum/post', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (res.data.code === 200) {
      ElMessage.success('发布成功')
      router.push('/forum')
    } else {
      ElMessage.error(res.data.msg)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.tieba-post {
  max-width: 800px;
  margin: 0 auto;
}

/* ---- 面包屑 ---- */
.breadcrumb-bar {
  font-size: 13px;
  color: var(--tieba-text-muted);
  padding: 8px 0;
  margin-bottom: 12px;
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

.breadcrumb-sep {
  margin: 0 6px;
  color: #ccc;
}

/* ---- 发帖卡片 ---- */
.post-card {
  background: var(--tieba-bg-white);
  border: 1px solid var(--tieba-border);
  border-radius: 4px;
  overflow: hidden;
}

.dark .post-card {
  background: var(--tieba-bg-white);
  border-color: var(--tieba-border);
}

.card-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid var(--tieba-border);
}

.dark .card-header {
  background: #2a2a2a;
  border-color: var(--tieba-border);
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: var(--tieba-text);
}

.card-body {
  padding: 16px;
}

/* ---- 表单组 ---- */
.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--tieba-text);
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
}

.form-editor {
  width: 100%;
}

/* ---- 分类选择 ---- */
.tag-selector {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-option {
  display: inline-flex !important;
  align-items: center !important;
  gap: 4px !important;
  padding: 6px 14px !important;
  font-size: 13px !important;
  color: var(--tieba-text-light) !important;
  background: #f5f5f5 !important;
  border: 1px solid var(--tieba-border) !important;
  border-radius: 4px !important;
  cursor: pointer !important;
  transition: all 0.2s !important;
  pointer-events: auto !important;
  user-select: none !important;
  -webkit-user-select: none !important;
  flex-shrink: 0 !important;
  min-width: auto !important;
  line-height: 1.5 !important;
}

.tag-option:hover {
  border-color: var(--tieba-blue) !important;
  color: var(--tieba-blue) !important;
  background: #f0f7ff !important;
}

.tag-option.active {
  background: var(--tieba-blue) !important;
  border-color: var(--tieba-blue) !important;
  color: #fff !important;
}

.dark .tag-option {
  background: #2a2a2a;
  border-color: var(--tieba-border);
}

.dark .tag-option:hover {
  border-color: var(--tieba-blue);
}

/* ---- 上传区域 ---- */
.upload-area {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #f0f7ff;
  border: 1px dashed var(--tieba-blue);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-btn:hover {
  background: #e0f0ff;
  border-style: solid;
}

.upload-icon {
  font-size: 16px;
}

.upload-text {
  font-size: 13px;
  color: var(--tieba-blue);
}

.upload-hint {
  font-size: 12px;
  color: var(--tieba-text-muted);
}

/* 图片预览 */
.upload-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.dark .upload-preview {
  background: #2a2a2a;
}

.preview-image {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
}

.preview-name {
  font-size: 12px;
  color: var(--tieba-text);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-remove {
  font-size: 14px;
  color: var(--tieba-text-muted);
  cursor: pointer;
  padding: 2px;
}

.preview-remove:hover {
  color: #ef4444;
}

/* 附件预览 */
.attach-preview {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.dark .attach-preview {
  background: #2a2a2a;
}

.attach-icon {
  font-size: 14px;
}

.attach-name {
  font-size: 12px;
  color: var(--tieba-text);
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attach-remove {
  font-size: 14px;
  color: var(--tieba-text-muted);
  cursor: pointer;
  padding: 2px;
}

.attach-remove:hover {
  color: #ef4444;
}

/* ---- 操作按钮 ---- */
.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--tieba-border);
}

.dark .form-actions {
  border-color: var(--tieba-border);
}

/* ---- 隐藏文件输入 ---- */
.hidden {
  display: none;
}
</style>