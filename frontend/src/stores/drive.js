import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '../axios'

export const useDriveStore = defineStore('drive', () => {
  const files = ref([])
  const totalFiles = ref(0)
  const currentPage = ref(1)
  const isLoading = ref(false)
  const stats = ref({
    total_files: 0,
    used_bytes: 0,
    used_human: '0 B',
    total_bytes: 10 * 1024 * 1024 * 1024,
    total_human: '10GB'
  })

  const loadFiles = async (page = 1) => {
    isLoading.value = true
    try {
      const res = await axios.get(`/api/drive/list?page=${page}&per_page=10`)
      if (page === 1) {
        files.value = res.data.data
      } else {
        files.value = [...files.value, ...res.data.data]
      }
      totalFiles.value = res.data.total
      currentPage.value = page
    } catch (e) {
      console.error('加载文件失败:', e)
    } finally {
      isLoading.value = false
    }
  }

  const uploadFile = async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await axios.post('/api/drive/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      await loadFiles(1)
      await loadStats()
      return res.data
    } catch (e) {
      console.error('上传文件失败:', e)
      throw e
    }
  }

  const deleteFile = async (fileId) => {
    try {
      const res = await axios.delete(`/api/drive/delete/${fileId}`)
      files.value = files.value.filter(f => f.id !== fileId)
      totalFiles.value = Math.max(0, totalFiles.value - 1)
      await loadStats()
      return res.data
    } catch (e) {
      console.error('删除文件失败:', e)
      throw e
    }
  }

  const downloadFile = (fileId) => {
    window.open(`/api/drive/download/${fileId}`, '_blank')
  }

  const loadStats = async () => {
    try {
      const res = await axios.get('/api/drive/stats')
      stats.value = res.data.data
    } catch (e) {
      console.error('加载存储空间统计失败:', e)
    }
  }

  const reset = () => {
    files.value = []
    totalFiles.value = 0
    currentPage.value = 1
  }

  return {
    files,
    totalFiles,
    currentPage,
    isLoading,
    stats,
    loadFiles,
    uploadFile,
    deleteFile,
    downloadFile,
    loadStats,
    reset
  }
})
