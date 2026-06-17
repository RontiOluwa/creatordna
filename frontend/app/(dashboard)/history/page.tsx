'use client'

import { useEffect, useState } from 'react'
import { getCreator } from '@/lib/auth'
import { ideasApi } from '@/lib/api'
import { ContentIdea } from '@/types'
import IdeaCard from '@/components/dashboard/IdeaCard'

type Filter = 'all' | 'made_it' | 'not_my_style'

export default function HistoryPage() {
  const [ideas, setIdeas] = useState<ContentIdea[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<Filter>('all')

  useEffect(() => {
    const c = getCreator()
    if (c?.id) {
      ideasApi.getAll(c.id)
        .then(res => setIdeas(res.data.ideas || []))
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [])

  const filtered = ideas.filter(idea => {
    if (filter === 'made_it') return idea.feedback === 'made_it'
    if (filter === 'not_my_style') return idea.feedback === 'not_my_style'
    return true
  })

  const grouped = filtered.reduce((acc, idea) => {
    const date = new Date(idea.delivered_at).toLocaleDateString('en-US', {
      weekday: 'long', month: 'long', day: 'numeric'
    })
    if (!acc[date]) acc[date] = []
    acc[date].push(idea)
    return acc
  }, {} as Record<string, ContentIdea[]>)

  const FILTERS: { val: Filter; label: string }[] = [
    { val: 'all', label: 'All' },
    { val: 'made_it', label: '✓ Made It' },
    { val: 'not_my_style', label: '✗ Skipped' },
  ]

  return (
    <div style={{ padding: 'clamp(16px, 3vw, 32px)' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 'clamp(18px, 3vw, 24px)', fontWeight: 700 }}>Idea History</h1>
          <p style={{ fontSize: 13, color: 'var(--gray-400)', marginTop: 2 }}>{ideas.length} ideas total</p>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {FILTERS.map(({ val, label }) => (
            <button key={val} onClick={() => setFilter(val)} style={{ padding: '7px 14px', borderRadius: 9999, fontSize: 12, cursor: 'pointer', background: filter === val ? 'var(--purple)' : 'white', color: filter === val ? 'white' : 'var(--gray-600)', border: `1px solid ${filter === val ? 'var(--purple)' : 'var(--gray-200)'}`, fontWeight: filter === val ? 500 : 400, whiteSpace: 'nowrap' }}>
              {label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="ideas-grid">
          {[1,2,3,4,5,6].map(i => (
            <div key={i} style={{ height: 300, borderRadius: 16, background: 'white', border: '1px solid var(--gray-100)', animation: 'pulse 1.5s infinite' }}/>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div style={{ width: 56, height: 56, borderRadius: 16, background: 'var(--purple-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--purple)" strokeWidth="2"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>
          </div>
          <p style={{ fontSize: 15, fontWeight: 500, marginBottom: 4 }}>No ideas yet</p>
          <p style={{ fontSize: 13, color: 'var(--gray-400)' }}>Ideas you generate will appear here</p>
        </div>
      ) : (
        <div>
          {Object.entries(grouped).map(([date, dateIdeas]) => (
            <div key={date} style={{ marginBottom: 28 }}>
              {/* Date header */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--gray-500)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  {date}
                </span>
                <span style={{ padding: '2px 8px', background: 'var(--purple-light)', color: 'var(--purple)', borderRadius: 9999, fontSize: 11, fontWeight: 600 }}>
                  {dateIdeas.length}
                </span>
                <div style={{ flex: 1, height: 1, background: 'var(--gray-200)' }}/>
              </div>
              {/* Cards grid */}
              <div className="ideas-grid">
                {dateIdeas.map(idea => <IdeaCard key={idea.id} idea={idea} />)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
