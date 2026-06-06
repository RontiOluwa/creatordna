'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { RefreshCw, Flame, Sparkles } from 'lucide-react'
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

  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long', month: 'long', day: 'numeric'
  })

  useEffect(() => {
    setMounted(true)
    const c = getCreator()
    if (!c?.id) return
    setHandle(c.tiktok_handle)
    setCreatorId(c.id)

    Promise.all([
      creatorsApi.getDna()
        .then(() => setHasProfile(true))
        .catch(() => setHasProfile(false)),
      fetchIdeas(c.id),
      fetchStats(),
    ])
  }, [])

  const fetchIdeas = async (id: number) => {
    setLoading(true)
    try {
      const res = await ideasApi.getToday(id)
      setIdeas(res.data.ideas || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const res = await ideasApi.getStats()
      setStats(res.data)
    } catch (e) {
      console.error(e)
    }
  }

  const generateIdeas = async () => {
    setGenerating(true)
    try {
      await ideasApi.generateNow()
      if (creatorId) {
        await Promise.all([fetchIdeas(creatorId), fetchStats()])
      }
    } catch (e) {
      console.error(e)
    } finally {
      setGenerating(false)
    }
  }

  if (!mounted) return null

  const statItems = [
    { val: stats?.total?.toString() ?? '—', label: 'Delivered' },
    { val: stats?.made_it?.toString() ?? '—', label: 'Made it' },
    { val: stats?.hit_rate ?? '—', label: 'Hit rate' },
    { val: stats?.avg_proof ?? '—', label: 'Avg proof' },
  ]

  return (
    <div>
      <div style={{ background: 'var(--surface)', borderBottom: '1px solid var(--border)' }}>
        <div className="px-5 pt-5 pb-0">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-lg font-medium">
                Good morning, {handle ? `@${handle}` : 'creator'}
              </h1>
              <p className="text-xs mt-0.5" style={{ color: '#9B9B96' }}>
                {today} · {ideas.length} ideas ready
              </p>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full"
              style={{ background: '#FAEEDA' }}>
              <Flame size={13} color="#BA7517" />
              <span className="text-xs font-medium" style={{ color: '#BA7517' }}>
                7 day streak
              </span>
            </div>
          </div>

          {/* <div className="flex" style={{ borderTop: '1px solid var(--border)' }}>
            {statItems.map((s, i, arr) => (
              <div key={s.label} className="flex-1 py-3 text-center"
                style={{
                  borderRight: i < arr.length - 1
                    ? '1px solid var(--border)' : 'none'
                }}>
                <div className="text-lg font-medium">{s.val}</div>
                <div className="text-xs mt-0.5" style={{ color: '#9B9B96' }}>
                  {s.label}
                </div>
              </div>
            ))}
          </div> */}
          <div className="grid grid-cols-2 sm:grid-cols-4"
            style={{ borderTop: '1px solid var(--border)' }}>
            {statItems.map((s, i) => (
              <div key={s.label} className="py-3 text-center"
                style={{
                  borderRight: (i % 2 === 0 || i < 3)
                    ? '1px solid var(--border)' : 'none',
                  borderBottom: i < 2
                    ? '1px solid var(--border)' : 'none',
                }}>
                <div className="text-lg font-medium">{s.val}</div>
                <div className="text-xs mt-0.5" style={{ color: '#9B9B96' }}>
                  {s.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="px-4 py-5">
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-medium uppercase tracking-wider"
            style={{ color: '#9B9B96' }}>
            Today's ideas
          </span>
          <button
            onClick={() => creatorId && fetchIdeas(creatorId)}
            className="flex items-center gap-1 text-xs font-medium"
            style={{ color: 'var(--brand)' }}
          >
            <RefreshCw size={11} /> Refresh
          </button>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2].map(i => (
              <div key={i} className="h-64 rounded-2xl animate-pulse"
                style={{ background: 'var(--surface)' }} />
            ))}
          </div>

        ) : ideas.length === 0 && hasProfile === false ? (
          <div className="text-center py-16">
            <p className="text-sm font-medium mb-1">Complete your profile first</p>
            <p className="text-xs mb-4" style={{ color: '#9B9B96' }}>
              We need your TikTok videos to personalise your ideas
            </p>
            <button
              onClick={() => router.push('/onboard')}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium text-white"
              style={{ background: 'var(--brand)' }}
            >
              Complete onboarding
            </button>
          </div>

        ) : ideas.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-4"
              style={{ background: 'var(--brand-light)' }}>
              <Sparkles size={20} style={{ color: 'var(--brand)' }} />
            </div>
            <p className="text-sm font-medium mb-1">Your ideas are ready to generate</p>
            <p className="text-xs mb-5" style={{ color: '#9B9B96' }}>
              Ideas deliver at 7am UTC — or generate them right now
            </p>
            <button
              onClick={generateIdeas}
              disabled={generating}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium text-white"
              style={{
                background: 'var(--brand)',
                opacity: generating ? 0.7 : 1
              }}
            >
              <Sparkles size={14} />
              {generating ? 'Generating your ideas...' : 'Generate my ideas now'}
            </button>
          </div>

        ) : (
          <div className="space-y-3">
            {ideas.map(idea => (
              <IdeaCard key={idea.id} idea={idea} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
