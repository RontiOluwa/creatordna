'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { creatorsApi } from '@/lib/api'
import { CreatorDNA } from '@/types'
import { getCreator } from '@/lib/auth'
import { ArrowRight, RefreshCw } from 'lucide-react'

export default function ProfilePage() {
  const router = useRouter()
  const [dna, setDna] = useState<CreatorDNA | null>(null)
  const [loading, setLoading] = useState(true)
  const [handle, setHandle] = useState('')
  const [initials, setInitials] = useState('??')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const creator = getCreator()
    if (creator?.tiktok_handle) {
      setHandle(creator.tiktok_handle)
      setInitials(creator.tiktok_handle.slice(0, 2).toUpperCase())
    }
    creatorsApi.getDna()
      .then(res => setDna(res.data))
      .catch(() => setDna(null))
      .finally(() => setLoading(false))
  }, [])

  const fields = dna ? [
    { key: 'Primary niche', val: dna.primary_niche },
    { key: 'Tone', val: dna.tone },
    { key: 'Hook style', val: dna.hook_style },
    { key: 'Content style', val: dna.content_style },
    { key: 'Avg length', val: dna.avg_video_length },
    { key: 'Audience', val: dna.audience_type },
    { key: 'Posting', val: dna.posting_frequency || 'Unknown' },
    { key: 'Secondary niches', val: dna.secondary_niches?.join(', ') || '—' },
  ] : []

  if (!mounted) return null

  return (
    <div className="px-4 py-5">

      <div className="rounded-2xl overflow-hidden"
        style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>

        <div className="px-5 py-4 flex items-center justify-between"
          style={{
            background: 'var(--brand-light)',
            borderBottom: '1px solid var(--border)'
          }}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium text-white"
              style={{ background: 'var(--brand)' }}>
              {initials}
            </div>
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--brand)' }}>
                @{handle}
              </p>
              <p className="text-xs mt-0.5" style={{ color: '#AFA9EC' }}>
                {dna
                  ? `${dna.primary_niche} · ${dna.tone}`
                  : 'No profile yet'}
              </p>
            </div>
          </div>

          {dna && (
            <button
              onClick={() => router.push('/onboard')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium"
              style={{
                background: 'var(--surface)',
                border: '1px solid var(--border)',
                color: 'var(--brand)',
              }}
            >
              <RefreshCw size={11} /> Update profile
            </button>
          )}
        </div>

        {loading ? (
          <div className="p-5 space-y-3">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-10 rounded-lg animate-pulse"
                style={{ background: 'var(--background)' }} />
            ))}
          </div>
        ) : dna ? (
          <div className="grid grid-cols-2">
            {fields.map((f, i) => (
              <div key={f.key} className="px-4 py-3"
                style={{
                  borderRight: i % 2 === 0
                    ? '1px solid var(--border)' : 'none',
                  borderBottom: i < fields.length - 2
                    ? '1px solid var(--border)' : 'none',
                }}>
                <p className="text-xs uppercase tracking-wider mb-1"
                  style={{ color: '#9B9B96' }}>
                  {f.key}
                </p>
                <p className="text-sm font-medium capitalize">
                  {f.val?.replace(/_/g, ' ')}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 px-6">
            <p className="text-sm font-medium mb-1">No profile yet</p>
            <p className="text-xs mb-4" style={{ color: '#9B9B96' }}>
              Complete onboarding to build your content DNA
            </p>
            <button
              onClick={() => router.push('/onboard')}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium text-white"
              style={{ background: 'var(--brand)' }}
            >
              Complete onboarding <ArrowRight size={13} />
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
