'use client'

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { useTheme } from 'next-themes'
import { isAuthenticated, getCreator, clearAuth } from '@/lib/auth'
import { creatorsApi } from '@/lib/api'
import { BarChart3, Sun, Moon, Bell, LogOut } from 'lucide-react'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const pathname = usePathname()
  const { theme, setTheme } = useTheme()
  const [handle, setHandle] = useState('')
  const [initials, setInitials] = useState('??')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)

    if (!isAuthenticated()) {
      router.push('/login')
      return
    }

    const c = getCreator()
    if (c?.tiktok_handle) {
      setHandle(c.tiktok_handle)
      setInitials(c.tiktok_handle.slice(0, 2).toUpperCase())
    }

    // Check DNA profile — redirect to onboard if missing
    // Skip if already on onboard page
    if (pathname !== '/onboard') {
      creatorsApi.getDna().catch(() => {
        router.push('/onboard')
      })
    }
  }, [router, pathname])

  const handleLogout = () => {
    clearAuth()
    router.push('/login')
  }

  const tabs = [
    { href: '/today', label: 'Today' },
    { href: '/history', label: 'History' },
    { href: '/profile', label: 'Profile' },
  ]

  return (
    <div className="min-h-screen" style={{ background: 'var(--background)' }}>
      <nav style={{
        background: 'var(--surface)',
        borderBottom: '1px solid var(--border)',
      }}>
        <div className="flex items-center justify-between px-5 py-3.5">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center"
              style={{ background: 'var(--brand)' }}>
              <BarChart3 size={14} color="white" />
            </div>
            <span className="text-sm font-medium">TrendScout</span>
          </div>

          <div className="flex items-center gap-2">
            {mounted && (
              <button
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className="w-8 h-8 rounded-full flex items-center justify-center"
                style={{ border: '1px solid var(--border)' }}
              >
                {theme === 'dark'
                  ? <Sun size={15} />
                  : <Moon size={15} />}
              </button>
            )}
            <button
              className="w-8 h-8 rounded-full flex items-center justify-center"
              style={{ border: '1px solid var(--border)' }}
            >
              <Bell size={15} />
            </button>
            <button
              onClick={handleLogout}
              className="w-8 h-8 rounded-full flex items-center justify-center"
              style={{ border: '1px solid var(--border)' }}
            >
              <LogOut size={15} />
            </button>
            {mounted && (
              <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium text-white"
                style={{ background: 'var(--brand)' }}>
                {initials}
              </div>
            )}
          </div>
        </div>

        <div className="flex px-5"
          style={{ borderTop: '1px solid var(--border)' }}>
          {tabs.map(tab => (
            <Link
              key={tab.href}
              href={tab.href}
              className="px-4 py-3 text-sm border-b-2 transition-colors"
              style={{
                borderColor: pathname === tab.href
                  ? 'var(--brand)' : 'transparent',
                color: pathname === tab.href
                  ? 'var(--brand)' : '#9B9B96',
                fontWeight: pathname === tab.href ? 500 : 400,
              }}
            >
              {tab.label}
            </Link>
          ))}
        </div>
      </nav>

      <main>{children}</main>
    </div>
  )
}
