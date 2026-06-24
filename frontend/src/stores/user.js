import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '../axios'
import { API_BASE } from '../utils/constants'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref({})
  const isLoggedIn = ref(false)
  const unreadCount = ref(0)
  const notifications = ref([])

  const avatarUrl = computed(() => {
    if (userInfo.value.avatar) return API_BASE + userInfo.value.avatar
    return ''
  })

  const fetchUserInfo = async () => {
    try {
      const res = await axios.get('/api/user/info')
      userInfo.value = res.data.data
      isLoggedIn.value = true
    } catch (e) {
      isLoggedIn.value = false
      userInfo.value = {}
    }
  }

  const fetchUnreadCount = async () => {
    if (!isLoggedIn.value) return
    try {
      const res = await axios.get('/api/notifications/count')
      unreadCount.value = res.data.data.count
    } catch (e) {}
  }

  const fetchNotifications = async () => {
    try {
      const res = await axios.get('/api/notifications')
      notifications.value = res.data.data
    } catch (e) {}
  }

  const markAllRead = async () => {
    await axios.post('/api/notifications/read')
    unreadCount.value = 0
  }

  const deleteNotification = async (id) => {
    await axios.delete(`/api/notifications/${id}`)
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  const logout = async () => {
    try { await axios.get('/api/logout') } catch (e) {}
    isLoggedIn.value = false
    userInfo.value = {}
  }

  return {
    userInfo,
    isLoggedIn,
    unreadCount,
    notifications,
    avatarUrl,
    fetchUserInfo,
    fetchUnreadCount,
    fetchNotifications,
    markAllRead,
    deleteNotification,
    logout
  }
})
