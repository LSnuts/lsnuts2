import axios from 'axios'

const getBaseURL = () => {
  if (import.meta.env.DEV) {
    return ''
  }
  return import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000'
}

const instance = axios.create({
  baseURL: getBaseURL(),
  timeout: 15000,
  withCredentials: true
})

const showError = (msg) => {
  try {
    const ElMessage = require('element-plus').ElMessage
    ElMessage.error(msg)
  } catch (e) {
    console.error('Axios error:', msg)
  }
}

instance.interceptors.request.use(
  config => {
    return config
  },
  error => {
    showError('请求配置错误')
    return Promise.reject(error)
  }
)

instance.interceptors.response.use(
  res => {
    if (res.data && res.data.code !== 200) {
      showError(res.data.msg || '操作失败')
    }
    return res
  },
  err => {
    const status = err.response?.status
    
    if (status === 401) {
      const currentPath = window.location.pathname
      const authPaths = ['/login', '/register', '/forgot-password', '/reset-password']
      if (!authPaths.includes(currentPath)) {
        localStorage.removeItem?.('lsnuts_token')
        showError('登录已失效，请重新登录')
        setTimeout(() => {
          window.location.href = '/login'
        }, 1500)
      }
    } else if (status === 403) {
      showError('无权限访问')
    } else if (status === 404) {
      showError('请求的资源不存在')
    } else if (status === 500) {
      showError('服务器内部错误，请稍后重试')
    } else if (err.message?.includes('timeout')) {
      showError('请求超时，请检查网络')
    } else if (err.message?.includes('Network')) {
      showError('网络连接失败，请检查网络')
    } else {
      const msg = err.response?.data?.msg || err.message || '请求失败'
      showError(msg)
    }
    
    return Promise.reject(err)
  }
)

export default instance
