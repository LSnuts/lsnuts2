import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '../axios'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref({ is_admin: 0 })
  const isLoggedIn = ref(!!localStorage.getItem('lsnuts_token'))
  const unreadCount = ref(0)
  const notifications = ref([])

  const avatarUrl = computed(() => {
    if (userInfo.value.avatar) return 'http://127.0.0.1:5000' + userInfo.value.avatar
    return ''
  })

  const fetchUserInfo = async () => {
    const token = localStorage.getItem('lsnuts_token')
    isLoggedIn.value = !!token
    if (!token) {
      userInfo.value = { is_admin: 0 }
      return
    }
    try {
      const res = await axios.get('/api/user/info')
      userInfo.value = res.data.data
    } catch (e) {
      localStorage.removeItem('lsnuts_token')
      isLoggedIn.value = false
      userInfo.value = { is_admin: 0 }
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
    localStorage.removeItem('lsnuts_token')
    isLoggedIn.value = false
    userInfo.value = { is_admin: 0 }
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
