import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '../axios'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])
  const unreadCount = ref(0)
  const isLoading = ref(false)

  const fetchNotifications = async () => {
    isLoading.value = true
    try {
      const res = await axios.get('/api/notifications')
      notifications.value = res.data.data
    } catch (e) {
      console.error('加载通知失败:', e)
    } finally {
      isLoading.value = false
    }
  }

  const fetchUnreadCount = async () => {
    try {
      const res = await axios.get('/api/notifications/count')
      unreadCount.value = res.data.data.count
    } catch (e) {
      console.error('加载未读数量失败:', e)
    }
  }

  const markAllRead = async () => {
    try {
      await axios.post('/api/notifications/read')
      unreadCount.value = 0
      notifications.value.forEach(n => n.is_read = 1)
    } catch (e) {
      console.error('标记已读失败:', e)
    }
  }

  const deleteNotification = async (id) => {
    try {
      await axios.delete(`/api/notifications/${id}`)
      notifications.value = notifications.value.filter(n => n.id !== id)
      if (unreadCount.value > 0) {
        unreadCount.value--
      }
    } catch (e) {
      console.error('删除通知失败:', e)
    }
  }

  const incrementUnread = () => {
    unreadCount.value++
  }

  const reset = () => {
    notifications.value = []
    unreadCount.value = 0
  }

  return {
    notifications,
    unreadCount,
    isLoading,
    fetchNotifications,
    fetchUnreadCount,
    markAllRead,
    deleteNotification,
    incrementUnread,
    reset
  }
})
