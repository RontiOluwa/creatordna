'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { creatorsApi } from '@/lib/api'
import { CreatorDNA } from '@/types'
import { getCreator, clearAuth } from '@/lib/auth'

const TONES = ['Casual humor', 'Educational', 'Inspirational', 'Authentic raw', 'Professional', 'Entertaining']
const NICHES = ['Tech & Gadgets', 'Beauty', 'Fitness', 'Home Kitchen', 'Fashion', 'Wellness', 'Cleaning', 'Pets', 'Hair Care']
const AUDIENCES = ['Gen Z 18-34', 'Busy professionals', 'Students', 'Parents', 'Deal hunters', 'Hobbyists']

export default function ProfilePage() {
  const router = useRouter()
  const [dna, setDna] = useState<CreatorDNA | null>(null)
  const [loading, setLoading] = useState(true)
  const [handle, setHandle] = useState('')
  const [initials, setInitials] = useState('??')
  const [mounted, setMounted] = useState(false)
  const [selectedTones, setSelectedTones] = useState<string[]>([])
  const [selectedNiches, setSelectedNiches] = useState<string[]>([])
  const [selectedAudiences, setSelectedAudiences] = useState<string[]>([])

  useEffect(() => {
    setMounted(true)
    const c = getCreator()
    if (c?.tiktok_handle) {
      setHandle(c.tiktok_handle)
      setInitials(c.tiktok_handle.slice(0, 2).toUpperCase())
    }
    creatorsApi.getDna()
      .then(res => {
        const d = res.data as CreatorDNA
        setDna(d)
        if (d.tone) setSelectedTones([d.tone.replace(/_/g, ' ')])
        if (d.primary_niche) setSelectedNiches([d.primary_niche.replace(/_/g, ' ')])
        if (d.audience_type) setSelectedAudiences([d.audience_type.replace(/_/g, ' ')])
      })
      .catch(() => setDna(null))
      .finally(() => setLoading(false))
  }, [])

  const toggle = (arr: string[], item: string) =>
    arr.includes(item) ? arr.filter(x => x !== item) : [...arr, item]

  if (!mounted) return null

  const Card = ({ children, style = {} }: { children: React.ReactNode; style?: React.CSSProperties }) => (
    <div style={{ background: 'white', borderRadius: 20, padding: 'clamp(16px, 2vw, 20px)', border: '1px solid var(--gray-100)', marginBottom: 16, ...style }}>
      {children}
    </div>
  )

  return (
    <div style={{ padding: 'clamp(16px, 3vw, 32px)', maxWidth: 900 }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 'clamp(18px, 3vw, 22px)', fontWeight: 700 }}>Profile</h1>
          <p style={{ fontSize: 13, color: 'var(--gray-400)', marginTop: 2 }}>Tune your DNA so every idea sounds like you</p>
        </div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <button onClick={() => router.push('/onboard')} style={{ padding: '8px 16px', background: 'white', border: '1px solid var(--gray-200)', borderRadius: 9999, fontSize: 13, color: 'var(--gray-600)', cursor: 'pointer', whiteSpace: 'nowrap' }}>
            Re-analyze
          </button>
          <button style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 16px', background: 'var(--purple)', color: 'white', border: 'none', borderRadius: 9999, fontSize: 13, fontWeight: 500, cursor: 'pointer', whiteSpace: 'nowrap' }}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5"><path d="M20 6L9 17l-5-5" /></svg>
            Save Changes
          </button>
        </div>
      </div>

      {/* Profile card */}
      <Card>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
          <div style={{ width: 48, height: 48, borderRadius: '50%', background: 'var(--purple)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, fontWeight: 600, color: 'white', flexShrink: 0 }}>
            {initials}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 16, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, flexWrap: 'wrap' }}>
              @{handle}
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 11, fontWeight: 500, color: 'var(--green)', background: 'var(--green-light)', padding: '2px 8px', borderRadius: 9999, whiteSpace: 'nowrap' }}>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M20 6L9 17l-5-5" /></svg>
                TikTok connected
              </span>
            </div>
            <div style={{ fontSize: 12, color: 'var(--gray-400)' }}>
              {dna?.primary_niche?.replace(/_/g, ' ')} · {dna?.tone?.replace(/_/g, ' ')}
            </div>
          </div>
          <button onClick={() => router.push('/onboard')} style={{ display: 'flex', alignItems: 'center', gap: 5, padding: '7px 14px', border: '1px solid var(--gray-200)', borderRadius: 9999, fontSize: 12, color: 'var(--gray-600)', background: 'white', cursor: 'pointer', whiteSpace: 'nowrap', flexShrink: 0 }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 4v6h6M23 20v-6h-6" /><path d="M20.49 9A9 9 0 005.64 5.64L1 10M23 14l-4.64 4.36A9 9 0 013.51 15" /></svg>
            Re-analyze profile
          </button>
        </div>
      </Card>

      {loading ? (
        <Card>
          {[1, 2, 3].map(i => <div key={i} style={{ height: 36, borderRadius: 10, background: 'var(--gray-100)', marginBottom: 10, animation: 'pulse 1.5s infinite' }} />)}
        </Card>
      ) : dna ? (
        <>
          {/* Content DNA */}
          <Card>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4, flexWrap: 'wrap', gap: 8 }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 15, fontWeight: 600 }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--purple)" strokeWidth="2"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" /></svg>
                Your Content DNA
              </h3>
            </div>
            <p style={{ fontSize: 12, color: 'var(--gray-400)', marginBottom: 18 }}>This is how we write every idea so it sounds like you</p>

            {[
              { label: 'Tone', hint: 'Pick up to 3', items: TONES, selected: selectedTones, setSelected: setSelectedTones },
              { label: 'Niche', hint: 'Your main category', items: NICHES, selected: selectedNiches, setSelected: setSelectedNiches },
              { label: 'Audience Type', hint: 'Who you create for', items: AUDIENCES, selected: selectedAudiences, setSelected: setSelectedAudiences },
            ].map(row => (
              <div key={row.label} style={{ marginBottom: 18 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 500, marginBottom: 10 }}>
                  {row.label}
                  <span style={{ color: 'var(--gray-400)', fontWeight: 400, fontSize: 12 }}>{row.hint}</span>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {row.items.map(item => {
                    const active = row.selected.includes(item)
                    return (
                      <button key={item}
                        style={{ padding: '5px 12px', borderRadius: 9999, border: `1.5px solid ${active ? 'var(--purple)' : 'var(--gray-200)'}`, background: active ? 'var(--purple)' : 'white', color: active ? 'white' : 'var(--gray-600)', fontSize: 12, cursor: 'pointer', fontWeight: active ? 500 : 400, whiteSpace: 'nowrap' }}>
                        {active ? '✓ ' : ''}{item}
                      </button>
                    )
                  })}
                </div>
              </div>
            ))}

            {/* DNA stats */}
            <div className="dna-stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 0, borderRadius: 12, overflow: 'hidden', border: '1px solid var(--gray-100)', marginTop: 4 }}>
              {[
                { key: 'Hook style', val: dna.hook_style },
                { key: 'Content style', val: dna.content_style },
                { key: 'Avg length', val: dna.avg_video_length },
                { key: 'Posting', val: dna.posting_frequency || 'Unknown' },
              ].map((f, i) => (
                <div key={f.key} style={{ padding: '10px 14px', borderRight: i < 3 ? '1px solid var(--gray-100)' : 'none', background: 'var(--gray-50)' }}>
                  <div style={{ fontSize: 10, color: 'var(--gray-400)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 3 }}>{f.key}</div>
                  <div style={{ fontSize: 12, fontWeight: 500, textTransform: 'capitalize' }}>{f.val?.replace(/_/g, ' ')}</div>
                </div>
              ))}
            </div>
          </Card>

          {/* Account */}
          <Card>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 15, fontWeight: 600, marginBottom: 16 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--purple)" strokeWidth="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" /><circle cx="9" cy="7" r="4" /></svg>
              Account
            </h3>
            {[
              { emoji: '👑', title: 'Plan: Creator Pro', sub: 'Unlimited daily ideas', action: 'Manage', danger: false, onClick: undefined },
              { emoji: '🚪', title: 'Log out', sub: 'Sign out on this device', action: null, danger: false, onClick: () => { clearAuth(); router.push('/login') } },
              { emoji: '🗑️', title: 'Delete account', sub: 'Permanently remove your data', action: null, danger: true, onClick: undefined },
            ].map((item, i) => (
              <div key={i} onClick={item.onClick} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 0', borderBottom: i < 2 ? '1px solid var(--gray-100)' : 'none', cursor: item.onClick ? 'pointer' : 'default' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ width: 34, height: 34, borderRadius: '50%', background: item.danger ? '#FEE2E2' : 'var(--gray-100)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 15, flexShrink: 0 }}>
                    {item.emoji}
                  </div>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 500, color: item.danger ? 'var(--red)' : 'var(--gray-900)' }}>{item.title}</div>
                    <div style={{ fontSize: 12, color: 'var(--gray-400)', marginTop: 1 }}>{item.sub}</div>
                  </div>
                </div>
                {item.action && <span style={{ fontSize: 13, color: 'var(--gray-500)' }}>{item.action}</span>}
              </div>
            ))}
          </Card>
        </>
      ) : (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <p style={{ fontSize: 15, fontWeight: 500, marginBottom: 8 }}>No profile yet</p>
            <button onClick={() => router.push('/onboard')} style={{ padding: '10px 24px', background: 'var(--purple)', color: 'white', border: 'none', borderRadius: 9999, fontSize: 14, cursor: 'pointer' }}>
              Complete onboarding
            </button>
          </div>
        </Card>
      )}
    </div>
  )
}
