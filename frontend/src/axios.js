import axios from 'axios'
import { API_BASE } from './utils/constants'

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
      localStorage.removeItem('lsnuts_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default instance
