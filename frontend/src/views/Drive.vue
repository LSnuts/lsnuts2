<template>
  <div class="p-3 md:p-5">
    <el-card title="我的网盘">
      <!-- 拖拽上传区域 -->
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

      <!-- 操作按钮 -->
      <div class="mb-4 flex gap-2">
        <el-upload 
          action="http://127.0.0.1:5000/api/drive/upload" 
          :with-credentials="true" 
          :on-success="() => { getFiles(); ElMessage.success('上传成功') }"
          :on-error="() => ElMessage.error('上传失败')">
          <el-button type="primary" size="small">📤 按钮上传</el-button>
        </el-upload>
        <el-button class="ml-2" @click="getFiles()" size="small">🔄 刷新</el-button>
      </div>

      <!-- 文件列表表格 -->
      <el-table :data="files" class="w-full">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="文件名" />
        <el-table-column prop="upload_time" label="上传时间" width="160" />
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="download(row)">📥</el-button>
            <el-button type="danger" size="small" @click="del(row.id, row.name)">🗑️</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态插图 -->
      <div v-if="files.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">📂</div>
        <div class="text-gray-400 dark:text-gray-500 text-lg">暂无文件，拖拽或点击上方区域上传</div>
      </div>

      <!-- 分页 -->
      <div v-if="total > pageSize" class="flex justify-center mt-4">
        <el-pagination v-model:current-page="currentPage" :page-size="pageSize" :total="total" layout="prev, pager, next" small @current-change="getFiles" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const files = ref([])
const isDragging = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadTotal = ref(0)
const uploadDone = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const fileInput = ref(null)

const getFiles = async () => {
  try {
    const res = await axios.get('/api/drive/list', {
      params: { page: currentPage.value, per_page: pageSize.value }
    })
    files.value = res.data.data
    total.value = res.data.total || 0
  } catch (e) {}
}

const del = async (id, name) => {
  try {
    await ElMessageBox.confirm(`确定删除文件 "${name}" 吗？此操作不可恢复。`, '确认删除', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' })
    await axios.get(`/api/drive/delete/${id}`)
    ElMessage.success('删除成功')
    getFiles()
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
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败：' + (error.response?.data?.msg || '未知错误'))
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
}

const onDrop = (e) => {
  isDragging.value = false
  uploadFiles(e.dataTransfer.files)
}

const onFileSelect = (e) => {
  uploadFiles(e.target.files)
  e.target.value = ''
}

onMounted(getFiles)
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
