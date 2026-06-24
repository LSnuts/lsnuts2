import axios from 'axios'
import { API_BASE } from './utils/constants'
import { useUserStore } from './stores/user'

const getBaseURL = () => {
  return API_BASE
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
      const store = useUserStore()
      store.logout()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default instance
