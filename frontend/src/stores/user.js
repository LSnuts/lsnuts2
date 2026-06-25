import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '../axios'
import { API_BASE } from '../utils/constants'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref({})
  const isLoggedIn = ref(false)

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

  const logout = async () => {
    try { await axios.get('/api/logout') } catch (e) {}
    isLoggedIn.value = false
    userInfo.value = {}
  }

  return {
    userInfo,
    isLoggedIn,
    avatarUrl,
    fetchUserInfo,
    logout
  }
})
