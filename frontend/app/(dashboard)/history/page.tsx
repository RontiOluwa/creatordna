'use client'

import { useEffect, useState } from 'react'
import { getCreator } from '@/lib/auth'
import { ideasApi } from '@/lib/api'
import { ContentIdea, AngleType } from '@/types'
import { angleConfig } from '@/lib/utils'
import { Check, X } from 'lucide-react'

export default function HistoryPage() {
  const [ideas, setIdeas] = useState<ContentIdea[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const c = getCreator()
    if (c?.id) {
      ideasApi.getAll(c.id)
        .then(res => setIdeas(res.data.ideas || []))
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [])

  return (
    <div className="px-4 py-5">
      <p className="text-xs font-medium uppercase tracking-wider mb-4"
        style={{ color: '#9B9B96' }}>
        Idea history
      </p>

      {loading ? (
        <div className="space-y-2">
          {[1,2,3].map(i => (
            <div key={i} className="h-20 rounded-xl animate-pulse"
              style={{ background: 'var(--surface)' }} />
          ))}
        </div>
      ) : ideas.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-sm font-medium mb-1">No history yet</p>
          <p className="text-xs" style={{ color: '#9B9B96' }}>
            Ideas will appear here after delivery
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {ideas.map(idea => {
            const config = angleConfig[idea.angle_type as AngleType] || angleConfig.curiosity_gap
            return (
              <div key={idea.id} className="rounded-xl p-3.5"
                style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${config.bg} ${config.color}`}>
                        {config.label}
                      </span>
                      <span className="text-xs" style={{ color: '#9B9B96' }}>
                        {new Date(idea.delivered_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-sm leading-snug truncate" style={{ color: 'inherit' }}>
                      "{idea.hook}"
                    </p>
                  </div>
                  <div className="flex-shrink-0">
                    {idea.feedback === 'made_it' ? (
                      <div className="w-7 h-7 rounded-full flex items-center justify-center"
                        style={{ background: '#E1F5EE' }}>
                        <Check size={13} color="#1D9E75" />
                      </div>
                    ) : idea.feedback === 'not_my_style' ? (
                      <div className="w-7 h-7 rounded-full flex items-center justify-center"
                        style={{ background: 'var(--background)' }}>
                        <X size={13} color="#9B9B96" />
                      </div>
                    ) : (
                      <div className="w-7 h-7 rounded-full"
                        style={{ background: 'var(--background)', border: '1px solid var(--border)' }} />
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
