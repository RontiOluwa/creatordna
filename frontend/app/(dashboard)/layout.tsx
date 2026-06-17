'use client'

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { isAuthenticated, getCreator, clearAuth } from '@/lib/auth'
import { creatorsApi } from '@/lib/api'

const NAV = [
  {
    href: '/today', label: 'Ideas',
    icon: (active: boolean) => (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={active ? 2.5 : 2}>
        <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
      </svg>
    )
  },
  {
    href: '/history', label: 'Saved',
    icon: (active: boolean) => (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={active ? 2.5 : 2}>
        <path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z" />
      </svg>
    )
  },
  {
    href: '/profile', label: 'Profile',
    icon: (active: boolean) => (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={active ? 2.5 : 2}>
        <circle cx="12" cy="8" r="4" /><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
      </svg>
    )
  }
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const [handle, setHandle] = useState('')
  const [initials, setInitials] = useState('??')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    if (!isAuthenticated()) { router.push('/login'); return }
    const c = getCreator()
    if (c?.tiktok_handle) {
      setHandle(c.tiktok_handle)
      setInitials(c.tiktok_handle.slice(0, 2).toUpperCase())
    }
    if (pathname !== '/onboard') {
      creatorsApi.getDna().catch(() => router.push('/onboard'))
    }
  }, [router, pathname])

  const isActive = (href: string) => pathname === href

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--gray-100)' }}>

      {/* ── Desktop Sidebar ──────────────────────────── */}
      <aside className="desktop-sidebar" style={{
        width: 'var(--sidebar-w)', background: 'white',
        borderRight: '1px solid var(--gray-200)',
        flexDirection: 'column',
        position: 'fixed', top: 0, left: 0, height: '100vh',
        zIndex: 40, overflowY: 'auto',
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '20px', borderBottom: '1px solid var(--gray-100)', flexShrink: 0 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: 'var(--purple)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" /></svg>
          </div>
          <div>
            <div style={{ fontSize: 15, fontWeight: 600 }}>Ideas Hub</div>
            <div style={{ fontSize: 11, color: 'var(--gray-400)' }}>TikTok Shop</div>
          </div>
        </div>

        {/* Nav links */}
        <nav style={{ padding: '16px 12px', flex: 1 }}>
          {NAV.map(item => (
            <Link key={item.label} href={item.href} style={{ textDecoration: 'none' }}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '9px 12px', borderRadius: 8,
                fontSize: 14, marginBottom: 2,
                background: isActive(item.href) ? 'var(--purple-light)' : 'transparent',
                color: isActive(item.href) ? 'var(--purple)' : 'var(--gray-600)',
                fontWeight: isActive(item.href) ? 500 : 400,
                transition: 'all 0.15s',
              }}>
                {item.icon(isActive(item.href))}
                {item.label}
              </div>
            </Link>
          ))}
        </nav>

        {/* Creator footer */}
        <div style={{ padding: '16px 12px', borderTop: '1px solid var(--gray-100)', flexShrink: 0 }}>
          <div
            onClick={() => { clearAuth(); router.push('/login') }}
            style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 12px', borderRadius: 8, cursor: 'pointer' }}
          >
            <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'var(--purple)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 600, color: 'white', flexShrink: 0 }}>
              {mounted ? initials : '??'}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {mounted ? `@${handle}` : '...'}
              </div>
              <div style={{ fontSize: 11, color: 'var(--gray-400)' }}>Creator · Pro</div>
            </div>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 18l6-6-6-6" /></svg>
          </div>
        </div>
      </aside>

      {/* ── Mobile Top Bar ───────────────────────────── */}
      <div className="mobile-topbar" style={{
        position: 'fixed', top: 0, left: 0, right: 0,
        background: 'white', borderBottom: '1px solid var(--gray-200)',
        alignItems: 'center', justifyContent: 'space-between',
        padding: '10px 16px', zIndex: 50, height: 56,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 30, height: 30, borderRadius: 8, background: 'var(--purple)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" /></svg>
          </div>
          <span style={{ fontSize: 15, fontWeight: 600 }}>Ideas Hub</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 32, height: 32, borderRadius: '50%', border: '1px solid var(--gray-200)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 01-3.46 0" /></svg>
          </div>
          <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'var(--purple)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 600, color: 'white' }}>
            {mounted ? initials : '??'}
          </div>
        </div>
      </div>

      {/* ── Main Content ─────────────────────────────── */}
      <main className="main-content" style={{ flex: 1 }}>
        {children}
      </main>

      {/* ── Mobile Bottom Nav ────────────────────────── */}
      <nav className="mobile-bottomnav" style={{
        position: 'fixed', bottom: 0, left: 0, right: 0,
        background: 'white', borderTop: '1px solid var(--gray-200)',
        zIndex: 50, paddingBottom: 'env(safe-area-inset-bottom)',
      }}>
        {NAV.map(item => (
          <Link key={item.label} href={item.href} style={{ textDecoration: 'none', flex: 1 }}>
            <div style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center',
              justifyContent: 'center', padding: '8px 0 6px', gap: 3,
              color: isActive(item.href) ? 'var(--purple)' : 'var(--gray-400)',
            }}>
              {item.icon(isActive(item.href))}
              <span style={{ fontSize: 10, fontWeight: isActive(item.href) ? 600 : 400, letterSpacing: '0.02em' }}>
                {item.label}
              </span>
              {isActive(item.href) && (
                <div style={{ width: 4, height: 4, borderRadius: '50%', background: 'var(--purple)', marginTop: 1 }} />
              )}
            </div>
          </Link>
        ))}
      </nav>
    </div>
  )
}
