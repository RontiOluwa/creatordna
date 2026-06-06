'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { authApi } from '@/lib/api'
import { setAuth } from '@/lib/auth'
import { AuthResponse } from '@/types'

export default function RegisterPage() {
  const router = useRouter()
  const [form, setForm] = useState({
    tiktok_handle: '',
    email: '',
    password: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await authApi.register(form)
      const data: AuthResponse = res.data
      setAuth(data.access_token, {
        id: data.creator_id,
        tiktok_handle: data.tiktok_handle,
      })
      router.push('/today')
    } catch (err: unknown) {
      const details = (err as {
        response?: { data?: { details?: { message: string }[] } }
      })?.response?.data?.details
      if (details?.length) {
        setError(details.map((d) => d.message).join(', '))
      } else {
        const msg = (err as { response?: { data?: { detail?: string } } })
          ?.response?.data?.detail
        setError(msg || 'Registration failed')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rounded-2xl p-8" style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
    }}>
      <h2 className="text-lg font-medium mb-6">Create your account</h2>

      {error && (
        <div className="mb-4 px-4 py-3 rounded-lg text-sm"
          style={{ background: '#FCEBEB', color: '#791F1F' }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-medium mb-1.5"
            style={{ color: '#6B6B66' }}>
            TikTok handle
          </label>
          <input
            type="text"
            required
            value={form.tiktok_handle}
            onChange={e => setForm({ ...form, tiktok_handle: e.target.value })}
            className="w-full px-3 py-2.5 rounded-lg text-sm outline-none"
            style={{
              background: 'var(--background)',
              border: '1px solid var(--border)',
              color: 'inherit',
            }}
            placeholder="@yourhandle"
          />
        </div>

        <div>
          <label className="block text-xs font-medium mb-1.5"
            style={{ color: '#6B6B66' }}>
            Email
          </label>
          <input
            type="email"
            required
            value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })}
            className="w-full px-3 py-2.5 rounded-lg text-sm outline-none"
            style={{
              background: 'var(--background)',
              border: '1px solid var(--border)',
              color: 'inherit',
            }}
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label className="block text-xs font-medium mb-1.5"
            style={{ color: '#6B6B66' }}>
            Password
          </label>
          <input
            type="password"
            required
            value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
            className="w-full px-3 py-2.5 rounded-lg text-sm outline-none"
            style={{
              background: 'var(--background)',
              border: '1px solid var(--border)',
              color: 'inherit',
            }}
            placeholder="Min 8 chars, 1 uppercase, 1 number"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 rounded-lg text-sm font-medium text-white mt-2"
          style={{ background: 'var(--brand)', opacity: loading ? 0.7 : 1 }}
        >
          {loading ? 'Creating account...' : 'Create account'}
        </button>
      </form>

      <p className="text-center text-sm mt-6" style={{ color: '#9B9B96' }}>
        Already have an account?{' '}
        <Link href="/login" style={{ color: 'var(--brand)' }}
          className="font-medium">
          Sign in
        </Link>
      </p>
    </div>
  )
}
