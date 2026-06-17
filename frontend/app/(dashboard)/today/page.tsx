'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getCreator } from '@/lib/auth'
import { ideasApi, creatorsApi } from '@/lib/api'
import { ContentIdea } from '@/types'
import IdeaCard from '@/components/dashboard/IdeaCard'

interface Stats {
  total: number
  made_it: number
  hit_rate: string
  avg_proof: string
}

export default function TodayPage() {
  const router = useRouter()
  const [ideas, setIdeas] = useState<ContentIdea[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [hasProfile, setHasProfile] = useState<boolean | null>(null)
  const [handle, setHandle] = useState('')
  const [creatorId, setCreatorId] = useState<number | null>(null)
  const [mounted, setMounted] = useState(false)
  const [streak, setStreak] = useState(0)

  useEffect(() => {
    setMounted(true)
    const c = getCreator()
    if (!c?.id) return
    setHandle(c.tiktok_handle)
    setCreatorId(c.id)
    Promise.all([
      creatorsApi.getDna().then(() => setHasProfile(true)).catch(() => setHasProfile(false)),
      fetchIdeas(c.id),
      fetchStats(),
      ideasApi.getStreak().then(r => setStreak(r.data.streak)).catch(() => {}),
    ])
  }, [])

  const fetchIdeas = async (id: number) => {
    setLoading(true)
    try { const res = await ideasApi.getToday(id); setIdeas(res.data.ideas || []) }
    catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const fetchStats = async () => {
    try { const res = await ideasApi.getStats(); setStats(res.data) }
    catch (e) { console.error(e) }
  }

  const generateIdeas = async () => {
    setGenerating(true)
    try {
      await ideasApi.generateNow()
      if (creatorId) await Promise.all([fetchIdeas(creatorId), fetchStats()])
    } catch (e) { console.error(e) }
    finally { setGenerating(false) }
  }

  if (!mounted) return null

  const STATS = [
    { label: 'Daily Ideas Delivered', value: stats?.total?.toString() ?? '—', delta: '+3 vs yesterday', up: true },
    { label: 'Ideas Made', value: stats?.made_it?.toString() ?? '—', delta: '+18% this week', up: true },
    { label: 'Hit Rate', value: stats?.hit_rate ?? '—', delta: '+5.2%', up: true },
    { label: 'Avg. Proof', value: stats?.avg_proof ?? '—', delta: '-2.1%', up: false },
  ]

  return (
    <div className="page-pad" style={{ padding: 'clamp(16px, 3vw, 32px)' }}>

      {/* ── Page header ─────────────────────────────── */}
      <div className="page-header-row" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24, gap: 12, flexWrap: 'wrap' }}>

        {/* Search — hidden on mobile */}
        <div className="hide-mobile" style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '9px 14px', background: 'white', border: '1px solid var(--gray-200)', borderRadius: 9999, minWidth: 220, flex: '0 0 auto' }}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--gray-400)" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
          <input placeholder="Search ideas, niches, hooks..." style={{ border: 'none', outline: 'none', fontSize: 13, color: 'var(--gray-600)', width: '100%', background: 'transparent' }}/>
        </div>

        {/* Title — always visible */}
        <div style={{ textAlign: 'center', flex: 1 }}>
          <h1 style={{ fontSize: 'clamp(18px, 3vw, 24px)', fontWeight: 700 }}>Today's Ideas</h1>
          <p style={{ fontSize: 12, color: 'var(--gray-400)', marginTop: 2 }}>Written in your voice</p>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: '0 0 auto' }}>
          {/* Notification — desktop only */}
          <div className="hide-mobile" style={{ width: 36, height: 36, borderRadius: '50%', border: '1px solid var(--gray-200)', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>
          </div>
          <button
            onClick={generateIdeas}
            disabled={generating}
            style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', background: 'var(--purple)', color: 'white', border: 'none', borderRadius: 9999, fontSize: 13, fontWeight: 500, cursor: 'pointer', opacity: generating ? 0.7 : 1, whiteSpace: 'nowrap' }}
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5"><path d="M12 5v14M5 12h14"/></svg>
            {generating ? 'Generating...' : 'New Idea'}
          </button>
        </div>
      </div>

      {/* ── Stats grid ──────────────────────────────── */}
      <div className="stats-grid" style={{ marginBottom: 24 }}>
        {STATS.map(s => (
          <div key={s.label} style={{ background: 'white', borderRadius: 14, padding: 'clamp(14px, 2vw, 20px)', border: '1px solid var(--gray-100)' }}>
            <div style={{ fontSize: 11, color: 'var(--gray-400)', marginBottom: 6 }}>{s.label}</div>
            <div style={{ fontSize: 'clamp(20px, 3vw, 28px)', fontWeight: 700, marginBottom: 5, lineHeight: 1.1 }}>{s.value}</div>
            <div style={{ fontSize: 11, fontWeight: 500, display: 'flex', alignItems: 'center', gap: 3, color: s.up ? 'var(--green)' : 'var(--red)' }}>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                {s.up ? <path d="M7 17L17 7M17 7H7M17 7v10"/> : <path d="M7 7l10 10M17 17H7M17 17V7"/>}
              </svg>
              {s.delta}
            </div>
          </div>
        ))}
      </div>

      {/* ── Filters row ─────────────────────────────── */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18, gap: 8, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {['Niche', 'Date', 'Performance'].map(f => (
            <button key={f} style={{ display: 'flex', alignItems: 'center', gap: 5, padding: '6px 12px', background: 'white', border: '1px solid var(--gray-200)', borderRadius: 9999, fontSize: 12, color: 'var(--gray-600)', cursor: 'pointer', whiteSpace: 'nowrap' }}>
              {f}
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 9l6 6 6-6"/></svg>
            </button>
          ))}
        </div>
        <span style={{ fontSize: 12, color: 'var(--gray-400)', whiteSpace: 'nowrap' }}>
          Showing {ideas.length} of {ideas.length} ideas
        </span>
      </div>

      {/* ── Ideas ───────────────────────────────────── */}
      {loading ? (
        <div className="ideas-grid">
          {[1,2,3].map(i => (
            <div key={i} style={{ height: 320, borderRadius: 16, background: 'white', animation: 'pulse 1.5s infinite' }}/>
          ))}
        </div>
      ) : ideas.length === 0 && hasProfile === false ? (
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <p style={{ fontSize: 15, fontWeight: 500, marginBottom: 8 }}>Complete your profile first</p>
          <button onClick={() => router.push('/onboard')} style={{ padding: '10px 24px', background: 'var(--purple)', color: 'white', border: 'none', borderRadius: 9999, fontSize: 14, cursor: 'pointer' }}>
            Complete onboarding
          </button>
        </div>
      ) : ideas.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div style={{ width: 56, height: 56, borderRadius: 16, background: 'var(--purple-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--purple)" strokeWidth="2"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>
          </div>
          <p style={{ fontSize: 15, fontWeight: 500, marginBottom: 6 }}>Your ideas are ready to generate</p>
          <p style={{ fontSize: 13, color: 'var(--gray-400)', marginBottom: 20 }}>Ideas deliver at 7am UTC — or generate them right now</p>
          <button onClick={generateIdeas} disabled={generating} style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '12px 24px', background: 'var(--purple)', color: 'white', border: 'none', borderRadius: 12, fontSize: 14, fontWeight: 600, cursor: 'pointer', opacity: generating ? 0.7 : 1 }}>
            {generating ? 'Generating your ideas...' : 'Generate my ideas now'}
          </button>
        </div>
      ) : (
        <div className="ideas-grid">
          {ideas.map(idea => <IdeaCard key={idea.id} idea={idea} />)}
        </div>
      )}
    </div>
  )
}
