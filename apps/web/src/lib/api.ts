import axios from 'axios'

export const TOKEN_STORAGE_KEY = 'metaway.auth.token'
export const USER_STORAGE_KEY = 'metaway.auth.user'

const LOGIN_PATH = '/login'
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_STORAGE_KEY)
      localStorage.removeItem(USER_STORAGE_KEY)
      if (window.location.pathname !== LOGIN_PATH) {
        window.location.assign(LOGIN_PATH)
      }
    }
    return Promise.reject(error)
  },
)
