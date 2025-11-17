import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// API methods
export const authApi = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (data) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
}

export const podcastsApi = {
  list: (params) => api.get('/podcasts', { params }),
  get: (id) => api.get(`/podcasts/${id}`),
  create: (data) => api.post('/podcasts', data),
  update: (id, data) => api.put(`/podcasts/${id}`, data),
  delete: (id) => api.delete(`/podcasts/${id}`),
}

export const episodesApi = {
  list: (params) => api.get('/episodes', { params }),
  get: (id) => api.get(`/episodes/${id}`),
  create: (data) => api.post('/episodes', data),
  update: (id, data) => api.put(`/episodes/${id}`, data),
  delete: (id) => api.delete(`/episodes/${id}`),
}

export const transcriptionsApi = {
  list: (params) => api.get('/transcriptions', { params }),
  get: (id) => api.get(`/transcriptions/${id}`),
  upload: (formData) => api.post('/transcriptions/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
}

export const analyticsApi = {
  overview: (params) => api.get('/analytics/overview', { params }),
  podcasts: (id, params) => api.get(`/analytics/podcasts/${id}`, { params }),
  episodes: (id, params) => api.get(`/analytics/episodes/${id}`, { params }),
}

export const distributionApi = {
  list: (params) => api.get('/distribution', { params }),
  publish: (data) => api.post('/distribution/publish', data),
  status: (id) => api.get(`/distribution/${id}`),
}
