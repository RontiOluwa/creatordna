'use client'

import { useState } from 'react'
import { ContentIdea, AngleType } from '@/types'
import { creatorsApi } from '@/lib/api'

const ANGLE_CONFIG: Record<string, { bg: string; color: string; label: string }> = {
  curiosity_gap:          { bg: '#EDE9FE', color: '#7C3AED', label: 'Curiosity Gap' },
  problem_agitate_solve:  { bg: '#FFF7ED', color: '#C2410C', label: 'Problem → Solve' },
  transformation:         { bg: '#ECFDF5', color: '#065F46', label: 'Transformation' },
  social_proof:           { bg: '#EFF6FF', color: '#1E40AF', label: 'Social Proof' },
  urgency_deal:           { bg: '#FFF1F2', color: '#BE123C', label: 'Urgency Deal' },
  demonstration:          { bg: '#F0FDF4', color: '#166534', label: 'Demonstration' },
  tech_gadgets:           { bg: '#EDE9FE', color: '#7C3AED', label: 'Tech & Gadgets' },
  beauty_skincare:        { bg: '#FDF2F8', color: '#9D174D', label: 'Beauty' },
  home_kitchen:           { bg: '#FFF7ED', color: '#C2410C', label: 'Home & Kitchen' },
  fitness:                { bg: '#F0FDF4', color: '#166534', label: 'Fitness' },
  pets:                   { bg: '#FFFBEB', color: '#92400E', label: 'Pets' },
  fashion:                { bg: '#FEF3C7', color: '#92400E', label: 'Fashion' },
  wellness:               { bg: '#ECFDF5', color: '#065F46', label: 'Wellness' },
  cleaning:               { bg: '#EFF6FF', color: '#1E40AF', label: 'Cleaning' },
  hair_care:              { bg: '#FDF4FF', color: '#7E22CE', label: 'Hair Care' },
  entertaining:           { bg: '#FFF1F2', color: '#BE123C', label: 'Entertaining' },
}

const DEFAULT_CONFIG = { bg: '#EDE9FE', color: '#7C3AED', label: 'General' }

export default function IdeaCard({ idea }: { idea: ContentIdea }) {
  const [feedback, setFeedback] = useState(idea.feedback)
  const [loading, setLoading] = useState(false)
  const [expanded, setExpanded] = useState(true)

  const config = ANGLE_CONFIG[idea.angle_type] || DEFAULT_CONFIG

  const handleFeedback = async (val: 'made_it' | 'not_my_style') => {
    if (feedback || loading) return
    setLoading(true)
    try { await creatorsApi.feedback(idea.id, val); setFeedback(val) }
    catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const timeAgo = () => {
    const diff = Date.now() - new Date(idea.delivered_at).getTime()
    const h = Math.floor(diff / 3600000)
    if (h < 1) return 'Just now'
    if (h < 24) return `${h}h ago`
    return `${Math.floor(h / 24)}d ago`
  }

  return (
    <div style={{
      background: 'white', borderRadius: 16,
      border: '1px solid var(--gray-100)',
      overflow: 'hidden',
      boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      display: 'flex', flexDirection: 'column',
    }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 16px 0', gap: 8 }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 5,
          padding: '4px 10px', background: config.bg,
          borderRadius: 9999, fontSize: 12, fontWeight: 500, color: config.color,
          flexShrink: 0, maxWidth: '60%',
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }}>
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ flexShrink: 0 }}><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>
          {config.label}
        </div>
        <span style={{ fontSize: 11, color: 'var(--gray-400)', whiteSpace: 'nowrap' }}>Written in your voice</span>
      </div>

      {/* Title */}
      <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--gray-900)', padding: '10px 16px', lineHeight: 1.4 }}>
        {idea.hook.length > 90 ? idea.hook.slice(0, 90) + '...' : idea.hook}
      </div>

      {/* Hook block */}
      <div style={{ margin: '0 16px', background: config.bg, borderRadius: 12, padding: '10px 12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 10, fontWeight: 700, color: config.color, letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 6 }}>
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
          HOOK
        </div>
        <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--gray-900)', fontStyle: 'italic', lineHeight: 1.5 }}>
          "{idea.hook}"
        </div>
      </div>

      {/* Shot list */}
      <div style={{ padding: '12px 16px 0', flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 10, fontWeight: 700, color: 'var(--gray-500)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polygon points="10,8 16,12 10,16"/></svg>
            SHOT LIST
          </div>
          <button onClick={() => setExpanded(!expanded)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: 'var(--gray-400)' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              {expanded ? <path d="M18 15l-6-6-6 6"/> : <path d="M6 9l6 6 6-6"/>}
            </svg>
          </button>
        </div>

        {expanded && (
          <div style={{ marginBottom: 4 }}>
            {(idea.shot_list || []).slice(0, 3).map((shot, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, marginBottom: 6 }}>
                <div style={{ width: 18, height: 18, borderRadius: '50%', background: config.bg, color: config.color, fontSize: 10, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginTop: 1 }}>
                  {i + 1}
                </div>
                <div style={{ fontSize: 12, color: 'var(--gray-600)', lineHeight: 1.45, flex: 1 }}>{shot}</div>
              </div>
            ))}
          </div>
        )}

        {/* CTA */}
        {idea.cta && (
          <div style={{ fontSize: 12, color: 'var(--gray-400)', fontStyle: 'italic', paddingBottom: 8, lineHeight: 1.4 }}>
            "{idea.cta.length > 80 ? idea.cta.slice(0, 80) + '...' : idea.cta}"
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{ padding: '10px 16px', borderTop: '1px solid var(--gray-100)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 13, fontWeight: 600, color: 'var(--green)' }}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M7 17L17 7M17 7H7M17 7v10"/></svg>
          {idea.source_revenue} proof
        </div>
        <div style={{ fontSize: 11, color: 'var(--gray-400)' }}>{timeAgo()}</div>
      </div>

      {/* Feedback buttons */}
      <div style={{ display: 'flex', gap: 8, padding: '0 16px 14px' }}>
        <button
          onClick={() => handleFeedback('made_it')}
          disabled={!!feedback || loading}
          style={{
            flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
            padding: '9px 8px', borderRadius: 10, fontSize: 13, fontWeight: 600, cursor: feedback ? 'default' : 'pointer',
            background: feedback === 'made_it' ? 'var(--green)' : 'var(--green)',
            color: 'white', border: 'none',
            opacity: feedback === 'not_my_style' ? 0.35 : 1,
            transition: 'opacity 0.2s',
          }}
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5"><path d="M20 6L9 17l-5-5"/></svg>
          {feedback === 'made_it' ? 'Filmed it!' : 'Made It'}
        </button>
        <button
          onClick={() => handleFeedback('not_my_style')}
          disabled={!!feedback || loading}
          style={{
            flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
            padding: '9px 8px', borderRadius: 10, fontSize: 13, fontWeight: 600, cursor: feedback ? 'default' : 'pointer',
            background: 'white', color: 'var(--red)',
            border: '2px solid var(--red)',
            opacity: feedback === 'made_it' ? 0.35 : feedback === 'not_my_style' ? 0.5 : 1,
            transition: 'opacity 0.2s',
          }}
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M18 6L6 18M6 6l12 12"/></svg>
          {feedback === 'not_my_style' ? 'Skipped' : 'Not My Style'}
        </button>
      </div>
    </div>
  )
}
