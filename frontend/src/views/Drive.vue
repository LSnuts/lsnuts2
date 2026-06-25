<template>
  <div class="p-3 md:p-5">
    <el-card>
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-semibold">💾 我的网盘</span>
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">已用 {{ stats.used_human }} / {{ stats.total_human }}</span>
          </div>
        </div>
      </template>

      <div class="mb-4">
        <div 
          class="drop-zone border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors"
          :class="isDragging ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-300 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500'"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @drop.prevent="onDrop"
          @click="fileInput.click()"
        >
          <div class="text-3xl mb-2">{{ isDragging ? '📂' : '📤' }}</div>
          <div class="text-sm text-gray-500 dark:text-gray-400">
            {{ isDragging ? '释放文件以上传' : '拖拽文件到此处上传，或点击选择文件' }}
          </div>
          <div class="text-xs text-gray-400 dark:text-gray-500 mt-1">支持多文件批量上传，单个文件最大 10MB</div>
        </div>
        <input ref="fileInput" type="file" class="hidden" multiple @change="onFileSelect" />
        <div v-if="uploading" class="mt-2">
          <div class="text-sm text-gray-500 mb-1">上传中 {{ uploadDone }}/{{ uploadTotal }} ...</div>
          <el-progress :percentage="uploadProgress" :status="uploadProgress === 100 ? 'success' : ''" />
        </div>
      </div>

      <div class="mb-4 flex flex-wrap gap-2">
        <el-upload 
          action="/api/drive/upload" 
          :with-credentials="true" 
          :data="{ category: selectedCategory }"
          :on-success="() => { getFiles(); getCategories(); loadStats(); ElMessage.success('上传成功') }"
          :on-error="() => ElMessage.error('上传失败')">
          <el-button type="primary" size="small">📤 按钮上传</el-button>
        </el-upload>
        <el-button @click="getFiles(); getCategories(); loadStats()" size="small">🔄 刷新</el-button>
        <div class="flex items-center gap-2 ml-auto">
          <span class="text-sm text-gray-500">分类：</span>
          <el-select v-model="selectedCategory" size="small" placeholder="全部" @change="getFiles">
            <el-option label="全部" value="" />
            <el-option v-for="cat in categories" :key="cat.name" :label="cat.name + ' (' + cat.count + ')'" :value="cat.name" />
          </el-select>
          <el-button size="small" type="success" @click="showAddCategory = true">+ 新建分类</el-button>
        </div>
      </div>

      <div v-if="files.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">📂</div>
        <div class="text-gray-400 dark:text-gray-500 text-lg">暂无文件，拖拽或点击上方区域上传</div>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        <el-card 
          v-for="file in files" 
          :key="file.id" 
          class="cursor-pointer hover:shadow-lg transition-shadow group"
          @click="download(file)"
        >
          <template #header>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="text-xl">{{ getFileIcon(file.name) }}</span>
                <span class="font-medium truncate max-w-[150px]">{{ file.name }}</span>
              </div>
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <el-button size="small" text @click.stop="handleShare(file)">🔗</el-button>
                <el-button size="small" text @click.stop="showCategoryChange(file)">📁</el-button>
                <el-button size="small" text type="danger" @click.stop="del(file)">🗑️</el-button>
              </div>
            </div>
          </template>
          <div class="text-xs text-gray-500 space-y-1">
            <div>📅 {{ file.upload_time }}</div>
            <div>📁 <el-tag size="small">{{ file.category || '默认' }}</el-tag></div>
          </div>
        </el-card>
      </div>

      <div v-if="total > pageSize" class="flex justify-center mt-4">
        <el-pagination v-model:current-page="currentPage" :page-size="pageSize" :total="total" layout="prev, pager, next" small @current-change="getFiles" />
      </div>
    </el-card>

    <el-dialog v-model="showAddCategory" title="新建分类" width="400px">
      <el-form :model="newCategory" label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="newCategory.name" placeholder="请输入分类名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddCategory = false">取消</el-button>
        <el-button type="primary" @click="addCategory">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showCategoryDialog" title="修改分类" width="400px">
      <el-form :model="editCategory" label-width="80px">
        <el-form-item label="选择分类">
          <el-select v-model="editCategory.name" placeholder="请选择分类">
            <el-option v-for="cat in categories" :key="cat.name" :label="cat.name" :value="cat.name" />
            <el-option label="新建分类..." value="__new__" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="editCategory.name === '__new__'" label="新分类名">
          <el-input v-model="editCategory.newName" placeholder="请输入新分类名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCategoryDialog = false">取消</el-button>
        <el-button type="primary" @click="updateFileCategory">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showShareDialog" title="分享文件" width="500px">
      <div v-if="shareLink" class="space-y-4">
        <el-alert type="success" :closable="false">
          <template #title>
            <span>分享链接已生成</span>
          </template>
        </el-alert>
        <div class="flex gap-2">
          <el-input v-model="shareLink" readonly />
          <el-button type="primary" @click="copyLink">复制</el-button>
        </div>
        <div class="text-sm text-gray-500">有效期至：{{ shareExpire }}</div>
      </div>
      <div v-else class="space-y-4">
        <el-form-item label="有效期">
          <el-select v-model="shareDays" style="width: 100%">
            <el-option label="7天" :value="7" />
            <el-option label="30天" :value="30" />
            <el-option label="永久" :value="36500" />
          </el-select>
        </el-form-item>
      </div>
      <template #footer>
        <el-button @click="showShareDialog = false; shareLink = ''">关闭</el-button>
        <el-button v-if="!shareLink" type="primary" @click="createShare">生成链接</el-button>
        <el-button v-else type="danger" @click="cancelShare">取消分享</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from '../axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const files = ref([])
const categories = ref([])
const stats = ref({
  used_human: '0 B',
  total_human: '10GB'
})
const isDragging = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadTotal = ref(0)
const uploadDone = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const fileInput = ref(null)
const selectedCategory = ref('')
const showAddCategory = ref(false)
const showCategoryDialog = ref(false)
const currentFile = ref(null)
const showShareDialog = ref(false)
const shareLink = ref('')
const shareExpire = ref('')
const shareDays = ref(7)
const shareFileId = ref(null)

const newCategory = reactive({ name: '' })
const editCategory = reactive({ name: '', newName: '' })

const getFiles = async () => {
  try {
    const params = { page: currentPage.value, per_page: pageSize.value }
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    const res = await axios.get('/api/drive/list', { params })
    files.value = res.data.data
    total.value = res.data.total || 0
  } catch (e) {}
}

const getCategories = async () => {
  try {
    const res = await axios.get('/api/drive/categories')
    categories.value = res.data.data
  } catch (e) {}
}

const loadStats = async () => {
  try {
    const res = await axios.get('/api/drive/stats')
    stats.value = res.data.data
  } catch (e) {}
}

const del = async (file) => {
  try {
    await ElMessageBox.confirm(`确定删除文件 "${file.name}" 吗？此操作不可恢复。`, '确认删除', { type: 'warning' })
    await axios.delete(`/api/drive/delete/${file.id}`)
    ElMessage.success('删除成功')
    getFiles()
    getCategories()
    loadStats()
  } catch (e) { if (e !== 'cancel') throw e }
}

const download = async (row) => {
  try {
    const res = await axios.get(`/api/drive/download/${row.id}`, { responseType: 'blob', withCredentials: true })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = row.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const uploadFiles = async (fileList) => {
  const filesArray = Array.from(fileList)
  if (filesArray.length === 0) return
  
  uploading.value = true
  uploadTotal.value = filesArray.length
  uploadDone.value = 0
  uploadProgress.value = 0
  
  for (const file of filesArray) {
    if (file.size > 10 * 1024 * 1024) {
      ElMessage.warning(`${file.name} 超过10M限制，已跳过`)
      uploadDone.value++
      continue
    }
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('category', selectedCategory.value || '默认')
      await axios.post('/api/drive/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    } catch (e) {
      ElMessage.error(`${file.name} 上传失败`)
    }
    uploadDone.value++
    uploadProgress.value = Math.round((uploadDone.value / uploadTotal.value) * 100)
  }
  
  ElMessage.success(`上传完成：${uploadDone.value}/${uploadTotal.value}`)
  uploading.value = false
  uploadProgress.value = 0
  getFiles()
  getCategories()
  loadStats()
}

const onDrop = (e) => {
  isDragging.value = false
  uploadFiles(e.dataTransfer.files)
}

const onFileSelect = (e) => {
  uploadFiles(e.target.files)
  e.target.value = ''
}

const addCategory = () => {
  const name = newCategory.name.trim()
  if (!name) {
    ElMessage.warning('请输入分类名称')
    return
  }
  selectedCategory.value = name
  newCategory.name = ''
  showAddCategory.value = false
  ElMessage.success('分类创建成功')
}

const showCategoryChange = (file) => {
  currentFile.value = file
  editCategory.name = file.category || ''
  editCategory.newName = ''
  showCategoryDialog.value = true
}

const updateFileCategory = async () => {
  let category = editCategory.name
  if (category === '__new__') {
    category = editCategory.newName.trim()
    if (!category) {
      ElMessage.warning('请输入新分类名称')
      return
    }
  }
  
  try {
    await axios.post(`/api/drive/update-category/${currentFile.value.id}`, { category })
    ElMessage.success('分类更新成功')
    showCategoryDialog.value = false
    getFiles()
    getCategories()
  } catch (e) {}
}

const handleShare = (file) => {
  shareFileId.value = file.id
  shareLink.value = ''
  shareExpire.value = ''
  shareDays.value = 7
  showShareDialog.value = true
}

const createShare = async () => {
  try {
    const res = await axios.post(`/api/drive/share/${shareFileId.value}`, { days: shareDays.value })
    shareLink.value = res.data.data.url
    shareExpire.value = res.data.data.expire
    ElMessage.success('分享链接已生成')
  } catch (e) {}
}

const cancelShare = async () => {
  try {
    await axios.post(`/api/drive/unshare/${shareFileId.value}`)
    shareLink.value = ''
    shareExpire.value = ''
    ElMessage.success('已取消分享')
  } catch (e) {}
}

const copyLink = () => {
  navigator.clipboard.writeText(shareLink.value)
  ElMessage.success('链接已复制')
}

const getFileIcon = (filename) => {
  const ext = filename.split('.').pop().toLowerCase()
  const icons = {
    'pdf': '📕', 'doc': '📘', 'docx': '📘', 'txt': '📗',
    'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'webp': '🖼️',
    'mp4': '🎬', 'avi': '🎬', 'mov': '🎬',
    'mp3': '🎵', 'wav': '🎵',
    'zip': '📦', 'rar': '📦', '7z': '📦',
    'exe': '⚙️', 'dll': '⚙️',
    'html': '🌐', 'css': '🎨', 'js': '📜', 'py': '🐍', 'java': '☕', 'cpp': '⚡',
    'json': '📋', 'xml': '📋', 'csv': '📊', 'xlsx': '📊', 'xls': '📊',
    'ppt': '📈', 'pptx': '📈'
  }
  return icons[ext] || '📄'
}

onMounted(() => {
  getFiles()
  getCategories()
  loadStats()
})
</script>

<style scoped>
.drop-zone {
  min-height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>
