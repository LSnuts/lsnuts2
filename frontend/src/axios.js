import axios from 'axios'

const getBaseURL = () => {
  if (import.meta.env.DEV) {
    return ''
  }
  return import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000'
}

const instance = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000,
  withCredentials: true
})

instance.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      // 防止无限循环：只有不在登录页面时才跳转
      if (window.location.pathname !== '/login') {
        localStorage.removeItem?.('lsnuts_token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export default instance
