'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Plus, X, ArrowRight, Video, Sparkles } from 'lucide-react'
import { creatorsApi } from '@/lib/api'
import { getCreator } from '@/lib/auth'

interface DnaSuccess {
  niche: string
  tone: string
  style: string
  hook_style: string
  audience: string
}

export default function OnboardPage() {
  const router = useRouter()
  const creator = getCreator()
  const [urls, setUrls] = useState<string[]>(['', '', ''])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState<DnaSuccess | null>(null)

  const addUrl = () => {
    if (urls.length < 15) setUrls([...urls, ''])
  }

  const removeUrl = (i: number) => {
    if (urls.length <= 3) return
    setUrls(urls.filter((_, idx) => idx !== i))
  }

  const updateUrl = (i: number, val: string) => {
    const updated = [...urls]
    updated[i] = val
    setUrls(updated)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    const validUrls = urls.filter(u => u.trim())
    if (validUrls.length < 3) {
      setError('Please add at least 3 TikTok video URLs')
      return
    }

    setLoading(true)
    try {
      const res = await creatorsApi.onboard({
        tiktok_handle: creator?.tiktok_handle || '',
        video_urls: validUrls,
      })
      const dna = res.data.dna
      setSuccess({
        niche: dna.primary_niche,
        tone: dna.tone,
        style: dna.content_style,
        hook_style: dna.hook_style,
        audience: dna.audience_type,
      })
    } catch (err: unknown) {
      const details = (err as {
        response?: { data?: { details?: { message: string }[] } }
      })?.response?.data?.details
      if (details?.length) {
        setError(details.map(d => d.message).join(', '))
      } else {
        const msg = (err as {
          response?: { data?: { detail?: string } }
        })?.response?.data?.detail
        setError(msg || 'Onboarding failed — please try again')
      }
    } finally {
      setLoading(false)
    }
  }

  // ── Success screen ─────────────────────────────────────────────────────────
  if (success) {
    return (
      <div className="px-4 py-8 max-w-lg mx-auto text-center">
        <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-5"
          style={{ background: 'var(--brand-light)' }}>
          <Sparkles size={28} style={{ color: 'var(--brand)' }} />
        </div>
        <h1 className="text-xl font-medium mb-2">Your DNA profile is ready</h1>
        <p className="text-sm mb-8" style={{ color: '#9B9B96' }}>
          Here's what we detected from your content
        </p>

        <div className="rounded-2xl overflow-hidden mb-6 text-left"
          style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
          {[
            { key: 'Primary niche', val: success.niche },
            { key: 'Tone', val: success.tone },
            { key: 'Content style', val: success.style },
            { key: 'Hook style', val: success.hook_style },
            { key: 'Audience', val: success.audience },
          ].map((f, i, arr) => (
            <div key={f.key}
              className="flex items-center justify-between px-5 py-3.5"
              style={{
                borderBottom: i < arr.length - 1
                  ? '1px solid var(--border)' : 'none'
              }}>
              <span className="text-xs uppercase tracking-wider"
                style={{ color: '#9B9B96' }}>
                {f.key}
              </span>
              <span className="text-sm font-medium capitalize">
                {f.val?.replace(/_/g, ' ')}
              </span>
            </div>
          ))}
        </div>

        <button
          onClick={() => router.push('/today')}
          className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-medium text-white"
          style={{ background: 'var(--brand)' }}
        >
          <Sparkles size={14} />
          Generate my first ideas
        </button>
      </div>
    )
  }

  // ── Onboard form ───────────────────────────────────────────────────────────
  return (
    <div className="px-4 py-6 max-w-lg mx-auto">
      <div className="mb-6">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
          style={{ background: 'var(--brand-light)' }}>
          <Video size={18} style={{ color: 'var(--brand)' }} />
        </div>
        <h1 className="text-lg font-medium mb-1">
          Build your content DNA
        </h1>
        <p className="text-sm" style={{ color: '#9B9B96' }}>
          Paste 3–15 links to your best TikTok videos.
          We'll analyse your style and personalise your daily ideas.
        </p>
      </div>

      {error && (
        <div className="mb-4 px-4 py-3 rounded-lg text-sm"
          style={{ background: '#FCEBEB', color: '#791F1F' }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="rounded-2xl overflow-hidden mb-4"
          style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>

          <div className="px-4 py-3"
            style={{
              borderBottom: '1px solid var(--border)',
              background: 'var(--background)'
            }}>
            <p className="text-xs font-medium uppercase tracking-wider"
              style={{ color: '#9B9B96' }}>
              Your TikTok video URLs
            </p>
          </div>

          <div className="p-4 space-y-3">
            {urls.map((url, i) => (
              <div key={i} className="flex gap-2 items-center">
                <span className="text-xs font-medium w-5 text-center flex-shrink-0"
                  style={{ color: '#9B9B96' }}>
                  {i + 1}
                </span>
                <input
                  type="url"
                  value={url}
                  onChange={e => updateUrl(i, e.target.value)}
                  placeholder="https://www.tiktok.com/@user/video/..."
                  className="flex-1 px-3 py-2 rounded-lg text-sm outline-none"
                  style={{
                    background: 'var(--background)',
                    border: '1px solid var(--border)',
                    color: 'inherit',
                  }}
                />
                {urls.length > 3 && (
                  <button
                    type="button"
                    onClick={() => removeUrl(i)}
                    className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ background: '#FCEBEB' }}
                  >
                    <X size={12} color="#D85A30" />
                  </button>
                )}
              </div>
            ))}
          </div>

          {urls.length < 15 && (
            <div style={{ borderTop: '1px solid var(--border)' }}>
              <button
                type="button"
                onClick={addUrl}
                className="w-full flex items-center justify-center gap-2 py-3 text-sm"
                style={{ color: 'var(--brand)' }}
              >
                <Plus size={14} /> Add another URL
              </button>
            </div>
          )}
        </div>

        <div className="rounded-xl px-4 py-3 mb-5 text-xs"
          style={{
            background: 'var(--brand-light)',
            color: 'var(--brand)',
          }}>
          💡 Pick videos with the most views and sales — better data means
          better personalisation
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-medium text-white"
          style={{ background: 'var(--brand)', opacity: loading ? 0.7 : 1 }}
        >
          {loading ? (
            'Analysing your content style...'
          ) : (
            <>Build my DNA profile <ArrowRight size={15} /></>
          )}
        </button>
      </form>
    </div>
  )
}
