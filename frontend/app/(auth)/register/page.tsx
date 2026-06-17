'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { authApi } from '@/lib/api'
import { setAuth } from '@/lib/auth'
import { AuthResponse } from '@/types'

export default function RegisterPage() {
  const router = useRouter()
  const [form, setForm] = useState({ tiktok_handle: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await authApi.register(form)
      const data: AuthResponse = res.data
      setAuth(data.access_token, { id: data.creator_id, tiktok_handle: data.tiktok_handle })
      router.push('/today')
    } catch (err: unknown) {
      const details = (err as { response?: { data?: { details?: { message: string }[] } } })?.response?.data?.details
      setError(details?.length ? details.map(d => d.message).join(', ') : (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Registration failed')
    } finally { setLoading(false) }
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'var(--gray-100)', padding: 20 }}>
      <div style={{ background: 'white', borderRadius: 24, width: '100%', maxWidth: 400, padding: 32, boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, justifyContent: 'center', marginBottom: 8 }}>
          <div style={{ width: 40, height: 40, borderRadius: 12, background: 'var(--purple)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" /></svg>
          </div>
          <span style={{ fontSize: 18, fontWeight: 700 }}>Ideas Hub</span>
        </div>
        <p style={{ fontSize: 13, color: 'var(--gray-400)', textAlign: 'center', marginBottom: 28 }}>Create your creator account</p>

        {error && <div style={{ marginBottom: 16, padding: '12px 16px', background: '#FEE2E2', color: '#991B1B', borderRadius: 12, fontSize: 13 }}>{error}</div>}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {[{ label: 'TikTok handle', type: 'text', key: 'tiktok_handle', placeholder: '@yourhandle' },
          { label: 'Email', type: 'email', key: 'email', placeholder: 'you@example.com' },
          { label: 'Password', type: 'password', key: 'password', placeholder: 'Min 8 chars, 1 uppercase, 1 number' }].map(f => (
            <div key={f.key}>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, color: 'var(--gray-600)', marginBottom: 6 }}>{f.label}</label>
              <input type={f.type} required placeholder={f.placeholder} value={form[f.key as keyof typeof form]} onChange={e => setForm({ ...form, [f.key]: e.target.value })}
                style={{ width: '100%', padding: '11px 14px', border: '1.5px solid var(--gray-200)', borderRadius: 10, fontSize: 14, outline: 'none', color: 'var(--gray-700)', background: 'white' }} />
            </div>
          ))}
          <button type="submit" disabled={loading} style={{ width: '100%', padding: 13, background: 'var(--purple)', color: 'white', border: 'none', borderRadius: 10, fontSize: 15, fontWeight: 600, cursor: 'pointer', opacity: loading ? 0.7 : 1, marginTop: 4 }}>
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        <p style={{ textAlign: 'center', fontSize: 14, color: 'var(--gray-400)', marginTop: 20 }}>
          Already have an account?{' '}
          <Link href="/login" style={{ color: 'var(--purple)', fontWeight: 500, textDecoration: 'none' }}>Sign in</Link>
        </p>
      </div>
    </div>
  )
}