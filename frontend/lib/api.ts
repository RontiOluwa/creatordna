// =============================================================================
// lib/api.ts
// =============================================================================
// Axios instance and all API calls to the api-gateway.
// Single base URL — everything proxied through :8000.
// =============================================================================

import axios from 'axios'
import Cookies from 'js-cookie'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = Cookies.get('sfn_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle auth errors globally
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      Cookies.remove('sfn_token')
      localStorage.removeItem('sfn_creator')
      window.location.href = '/login?reason=expired'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data: {
    tiktok_handle: string
    email: string
    password: string
  }) => api.post('/auth/register', data),

  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),

  me: () => api.get('/auth/me'),
}

// ── Creators ──────────────────────────────────────────────────────────────────
export const creatorsApi = {
  onboard: (data: { tiktok_handle: string; video_urls: string[] }) =>
    api.post('/creators/onboard', data),

  getMe: () => api.get('/creators/me'),

  getDna: () => api.get('/creators/me/dna'),

  feedback: (idea_id: number, feedback: 'made_it' | 'not_my_style') =>
    api.post('/creators/feedback', { idea_id, feedback }),
}

// ── Ideas ─────────────────────────────────────────────────────────────────────
export const ideasApi = {
  getToday: (creator_id: number) =>
    api.get(`/ideas/${creator_id}/today`),

  getAll: (creator_id: number) =>
    api.get(`/ideas/${creator_id}`),

  generateNow: () =>
    api.post('/ideas/deliver/me'),

  getStats: () =>
    api.get('/ideas/stats/me'),

  getStreak: () =>
    api.get('/ideas/streak/me'),
}
