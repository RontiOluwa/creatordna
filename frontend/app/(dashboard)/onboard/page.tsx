'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { creatorsApi } from '@/lib/api'
import { getCreator } from '@/lib/auth'

type Step = 'input' | 'analyzing' | 'ready'

interface DnaResult {
  primary_niche: string
  tone: string
  hook_style: string
  content_style: string
  audience_type: string
  secondary_niches: string[]
}

const ANALYZING_STEPS = [
  'Scanning your top videos',
  'Detecting your tone of voice',
  'Mapping your audience',
  'Matching trending products',
]

export default function OnboardPage() {
  const router = useRouter()
  const creator = getCreator()
  const [step, setStep] = useState<Step>('input')
  const [urls, setUrls] = useState(['', '', ''])
  const [error, setError] = useState('')
  const [progress, setProgress] = useState(0)
  const [activeStep, setActiveStep] = useState(0)
  const [dna, setDna] = useState<DnaResult | null>(null)

  const addUrl = () => { if (urls.length < 15) setUrls([...urls, '']) }
  const removeUrl = (i: number) => { if (urls.length > 3) setUrls(urls.filter((_, idx) => idx !== i)) }
  const updateUrl = (i: number, v: string) => { const u = [...urls]; u[i] = v; setUrls(u) }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    const validUrls = urls.filter(u => u.trim())
    if (validUrls.length < 3) { setError('Please add at least 3 TikTok video URLs'); return }

    setStep('analyzing')
    // Simulate progress
    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 95) { clearInterval(interval); return 95 }
        setActiveStep(Math.floor((p / 95) * 4))
        return p + 2
      })
    }, 150)

    try {
      const res = await creatorsApi.onboard({
        tiktok_handle: creator?.tiktok_handle || '',
        video_urls: validUrls,
      })
      clearInterval(interval)
      setProgress(100)
      setActiveStep(4)
      setDna(res.data.dna)
      setTimeout(() => setStep('ready'), 500)
    } catch (err: unknown) {
      clearInterval(interval)
      setStep('input')
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'Onboarding failed — please try again')
    }
  }

  const StepDots = ({ current }: { current: number }) => (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, marginBottom: 32 }}>
      {[0,1,2].map(i => (
        <div key={i} style={{ height: 6, borderRadius: 9999, background: i <= current ? 'var(--purple)' : 'var(--gray-200)', width: i === current ? 32 : 28, transition: 'all 0.3s' }}/>
      ))}
    </div>
  )

  const Logo = () => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, justifyContent: 'center', marginBottom: 24 }}>
      <div style={{ width: 40, height: 40, borderRadius: 12, background: 'var(--purple)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>
      </div>
      <span style={{ fontSize: 17, fontWeight: 700 }}>Ideas Hub</span>
    </div>
  )

  if (step === 'input') return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'var(--gray-100)', padding: 20 }}>
      <div style={{ background: 'white', borderRadius: 24, width: '100%', maxWidth: 420, padding: 32, boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}>
        <Logo />
        <StepDots current={0} />

        <div style={{ width: 72, height: 72, borderRadius: '50%', background: 'var(--purple-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px' }}>
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--purple)" strokeWidth="2"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>
        </div>

        <h1 style={{ fontSize: 22, fontWeight: 700, textAlign: 'center', marginBottom: 8 }}>Paste Your TikTok Profile Link</h1>
        <p style={{ fontSize: 14, color: 'var(--gray-400)', textAlign: 'center', lineHeight: 1.5, marginBottom: 28 }}>
          Drop your handle and we'll read your public videos. It takes about 15 seconds, no login needed.
        </p>

        {error && <div style={{ marginBottom: 16, padding: '12px 16px', background: '#FEE2E2', color: '#991B1B', borderRadius: 12, fontSize: 13 }}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div style={{ background: 'var(--gray-50)', borderRadius: 16, padding: 16, marginBottom: 16 }}>
            {urls.map((url, i) => (
              <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: i < urls.length - 1 ? 8 : 0 }}>
                <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--gray-400)', width: 18, textAlign: 'center' }}>{i+1}</span>
                <input
                  type="url"
                  value={url}
                  onChange={e => updateUrl(i, e.target.value)}
                  placeholder="tiktok.com/@yourname"
                  style={{ flex: 1, padding: '10px 12px', border: '1.5px solid var(--gray-200)', borderRadius: 10, fontSize: 14, outline: 'none', background: 'white', color: 'var(--gray-700)' }}
                />
                {urls.length > 3 && (
                  <button type="button" onClick={() => removeUrl(i)} style={{ width: 28, height: 28, borderRadius: 8, background: '#FEE2E2', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--red)" strokeWidth="2.5"><path d="M18 6L6 18M6 6l12 12"/></svg>
                  </button>
                )}
              </div>
            ))}
            {urls.length < 15 && (
              <button type="button" onClick={addUrl} style={{ width: '100%', padding: '8px', border: 'none', background: 'transparent', color: 'var(--purple)', fontSize: 13, fontWeight: 500, cursor: 'pointer', marginTop: 8 }}>
                + Add another URL
              </button>
            )}
          </div>

          <button type="submit" style={{ width: '100%', padding: 14, background: 'var(--purple)', color: 'white', border: 'none', borderRadius: 12, fontSize: 15, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginBottom: 16 }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>
            Analyze My Profile
          </button>
        </form>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, fontSize: 12, color: 'var(--gray-400)' }}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
          We only read public videos. Nothing is posted.
        </div>
      </div>
    </div>
  )

  if (step === 'analyzing') return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'var(--gray-100)', padding: 20 }}>
      <div style={{ background: 'white', borderRadius: 24, width: '100%', maxWidth: 420, padding: 32, boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}>
        <Logo />
        <StepDots current={1} />

        <div style={{ width: 100, height: 100, borderRadius: '50%', background: 'var(--purple-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px', position: 'relative', fontSize: 24, fontWeight: 700, color: 'var(--purple)' }}>
          {creator?.tiktok_handle?.slice(0,2).toUpperCase() || 'JD'}
          <div style={{ position: 'absolute', inset: -6, borderRadius: '50%', border: '4px solid var(--purple-light)', borderTop: '4px solid var(--purple)', animation: 'spin 1.2s linear infinite' }}/>
        </div>

        <h1 style={{ fontSize: 22, fontWeight: 700, textAlign: 'center', marginBottom: 8 }}>Analyzing Your Style...</h1>
        <p style={{ fontSize: 14, color: 'var(--gray-400)', textAlign: 'center', lineHeight: 1.5, marginBottom: 20 }}>Hang tight — we're learning what makes your content yours.</p>

        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, color: 'var(--gray-400)', marginBottom: 6 }}>
          <span>Almost there</span>
          <span style={{ color: 'var(--purple)', fontWeight: 600 }}>{progress}%</span>
        </div>
        <div style={{ height: 6, background: 'var(--gray-100)', borderRadius: 9999, overflow: 'hidden', marginBottom: 20 }}>
          <div style={{ height: '100%', background: 'var(--purple)', borderRadius: 9999, width: `${progress}%`, transition: 'width 0.3s' }}/>
        </div>

        <div style={{ background: 'var(--gray-50)', borderRadius: 12, padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
          {ANALYZING_STEPS.map((s, i) => {
            const done = i < activeStep
            const active = i === activeStep
            return (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 14, color: done ? 'var(--gray-600)' : active ? 'var(--gray-900)' : 'var(--gray-300)', fontWeight: active ? 500 : 400 }}>
                <div style={{ width: 22, height: 22, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, background: done ? 'var(--green)' : 'white', border: done ? 'none' : active ? '2px solid var(--purple)' : '2px solid var(--gray-200)' }}>
                  {done && <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3"><path d="M20 6L9 17l-5-5"/></svg>}
                  {active && <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--purple)' }}/>}
                </div>
                {s}
              </div>
            )
          })}
        </div>

        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    </div>
  )

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'var(--gray-100)', padding: 20 }}>
      <div style={{ background: 'white', borderRadius: 24, width: '100%', maxWidth: 420, padding: 32, boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}>
        <Logo />
        <StepDots current={2} />

        <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'var(--green)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px' }}>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3"><path d="M20 6L9 17l-5-5"/></svg>
        </div>

        <h1 style={{ fontSize: 22, fontWeight: 700, textAlign: 'center', marginBottom: 8 }}>Your DNA Profile is Ready!</h1>
        <p style={{ fontSize: 14, color: 'var(--gray-400)', textAlign: 'center', lineHeight: 1.5, marginBottom: 20 }}>
          We mapped your Content DNA. Every idea from here is written in your voice and tailored for your audience.
        </p>

        {dna && (
          <div style={{ background: 'var(--gray-50)', borderRadius: 12, padding: 16, marginBottom: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 14, fontWeight: 600, marginBottom: 14 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--purple)" strokeWidth="2"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>
              Your Content DNA
            </div>
            {[
              { key: 'Tone', vals: [dna.tone] },
              { key: 'Niche', vals: [dna.primary_niche] },
              { key: 'Audience', vals: [dna.audience_type] },
            ].map(row => (
              <div key={row.key} style={{ display: 'flex', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--gray-200)' }}>
                <div style={{ fontSize: 13, color: 'var(--gray-500)', width: 90, flexShrink: 0 }}>{row.key}</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, justifyContent: 'flex-end', flex: 1 }}>
                  {row.vals.map(v => (
                    <span key={v} style={{ padding: '3px 10px', background: 'var(--purple-light)', color: 'var(--purple)', borderRadius: 9999, fontSize: 12, fontWeight: 500 }}>
                      {v?.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            ))}
            <div style={{ marginTop: 12, padding: 10, background: 'var(--purple-light)', borderRadius: 10, fontSize: 13, color: 'var(--purple)', display: 'flex', alignItems: 'center', gap: 6 }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
              Written in your voice, tailored for your audience.
            </div>
          </div>
        )}

        <button onClick={() => router.push('/today')} style={{ width: '100%', padding: 14, background: 'var(--purple)', color: 'white', border: 'none', borderRadius: 12, fontSize: 15, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
          Enter My Ideas Hub
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </button>
      </div>
    </div>
  )
}
