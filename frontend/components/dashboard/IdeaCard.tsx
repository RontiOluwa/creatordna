'use client'

import { useState } from 'react'
import { Check, X, TrendingUp } from 'lucide-react'
import { ContentIdea, AngleType } from '@/types'
import { angleConfig, accentColor } from '@/lib/utils'
import { creatorsApi } from '@/lib/api'

interface Props {
  idea: ContentIdea
}

export default function IdeaCard({ idea }: Props) {
  const [feedback, setFeedback] = useState(idea.feedback)
  const [loading, setLoading] = useState(false)

  const config = angleConfig[idea.angle_type as AngleType] || angleConfig.curiosity_gap
  const accent = accentColor[idea.angle_type as AngleType] || accentColor.curiosity_gap

  const handleFeedback = async (value: 'made_it' | 'not_my_style') => {
    if (feedback || loading) return
    setLoading(true)
    try {
      await creatorsApi.feedback(idea.id, value)
      setFeedback(value)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rounded-2xl overflow-hidden"
      style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>

      <div className={`h-1 ${accent}`} />

      <div className="p-4">
        <div className="flex items-center justify-between mb-3.5">
          <span className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full font-medium ${config.bg} ${config.color}`}>
            {config.label}
          </span>
          <div className="flex items-center gap-1 text-xs px-2 py-1 rounded-full"
            style={{ background: 'var(--background)', color: '#9B9B96' }}>
            <TrendingUp size={10} />
            {idea.source_revenue} proof
          </div>
        </div>

        <div className="text-sm font-medium leading-relaxed mb-4 px-3.5 py-3 rounded-xl"
          style={{
            background: 'var(--background)',
            borderLeft: `3px solid ${accent.replace('bg-', '').includes('purple')
              ? '#AFA9EC' : accent.includes('orange') ? '#F0997B'
              : accent.includes('teal') ? '#5DCAA5' : accent.includes('blue')
              ? '#85B7EB' : accent.includes('red') ? '#F09595' : '#97C459'}`,
          }}>
          "{idea.hook}"
        </div>

        <p className="text-xs font-medium uppercase tracking-wider mb-2.5"
          style={{ color: '#9B9B96' }}>
          Shot list
        </p>

        <div className="space-y-2 mb-4">
          {idea.shot_list.map((shot, i) => (
            <div key={i} className="flex gap-2.5 items-start">
              <div className="w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-medium mt-0.5"
                style={{
                  border: '1px solid var(--border)',
                  color: '#9B9B96',
                  background: 'var(--surface)',
                }}>
                {i + 1}
              </div>
              <p className="text-sm leading-relaxed" style={{ color: '#6B6B66' }}>
                {shot}
              </p>
            </div>
          ))}
        </div>

        <div className="flex items-center gap-2 px-3 py-2.5 rounded-lg mb-4"
          style={{ background: 'var(--background)', border: '1px solid var(--border)' }}>
          <span style={{ color: '#9B9B96' }}>→</span>
          <p className="text-xs italic" style={{ color: '#6B6B66' }}>
            "{idea.cta}"
          </p>
        </div>

        <div className="flex gap-2 pt-3.5"
          style={{ borderTop: '1px solid var(--border)' }}>
          <button
            onClick={() => handleFeedback('made_it')}
            disabled={!!feedback || loading}
            className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium transition-all"
            style={{
              background: feedback === 'made_it' ? '#E1F5EE' : 'var(--surface)',
              border: `1px solid ${feedback === 'made_it' ? '#1D9E75' : 'var(--border)'}`,
              color: feedback === 'made_it' ? '#085041' : '#6B6B66',
              opacity: feedback === 'not_my_style' ? 0.4 : 1,
              cursor: feedback ? 'default' : 'pointer',
            }}
          >
            <Check size={13} />
            {feedback === 'made_it' ? 'Filmed it!' : 'Made it'}
          </button>

          <button
            onClick={() => handleFeedback('not_my_style')}
            disabled={!!feedback || loading}
            className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium transition-all"
            style={{
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              color: '#6B6B66',
              opacity: feedback === 'made_it' ? 0.4 : feedback === 'not_my_style' ? 0.4 : 1,
              cursor: feedback ? 'default' : 'pointer',
            }}
          >
            <X size={13} />
            {feedback === 'not_my_style' ? 'Skipped' : 'Not my style'}
          </button>
        </div>
      </div>
    </div>
  )
}
