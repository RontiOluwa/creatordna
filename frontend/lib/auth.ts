// =============================================================================
// lib/auth.ts
// =============================================================================
// Auth helpers — token storage and retrieval.
// =============================================================================

import Cookies from 'js-cookie'

const TOKEN_KEY = 'sfn_token'
const CREATOR_KEY = 'sfn_creator'

export const setAuth = (token: string, creator: {
  id: number
  tiktok_handle: string
}) => {
  Cookies.set(TOKEN_KEY, token, { expires: 1 }) // 1 day
  localStorage.setItem(CREATOR_KEY, JSON.stringify(creator))
}

export const getToken = () => Cookies.get(TOKEN_KEY)

export const getCreator = () => {
  if (typeof window === 'undefined') return null
  const raw = localStorage.getItem(CREATOR_KEY)
  if (!raw) return null
  try { return JSON.parse(raw) } catch { return null }
}

export const clearAuth = () => {
  Cookies.remove(TOKEN_KEY)
  localStorage.removeItem(CREATOR_KEY)
}

export const isAuthenticated = () => !!getToken()
