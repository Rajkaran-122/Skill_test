import { Bell, Search, RefreshCw } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function Header() {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <header
      className="flex items-center justify-between px-6 py-3 border-b"
      style={{
        background: 'var(--color-bg-secondary)',
        borderColor: 'var(--color-border)',
      }}
    >
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4" style={{ color: 'var(--color-text-muted)' }} />
        <input
          type="text"
          placeholder="Search stores, metrics..."
          className="pl-10 pr-4 py-2 rounded-xl text-sm w-72 outline-none transition-all duration-200 focus:ring-2"
          style={{
            background: 'var(--color-bg-glass)',
            border: '1px solid var(--color-border)',
            color: 'var(--color-text-primary)',
          }}
          id="global-search"
        />
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-4">
        {/* Live indicator */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full" style={{ background: 'rgba(16, 185, 129, 0.1)' }}>
          <span className="status-dot status-dot--active" />
          <span className="text-xs font-medium" style={{ color: 'var(--color-accent-emerald)' }}>Live</span>
        </div>

        {/* Clock */}
        <span className="text-sm font-mono" style={{ color: 'var(--color-text-secondary)' }}>
          {currentTime.toLocaleTimeString()}
        </span>

        {/* Refresh */}
        <button
          className="p-2 rounded-lg transition-colors duration-200 hover:bg-white/5"
          style={{ color: 'var(--color-text-secondary)' }}
          id="refresh-button"
        >
          <RefreshCw className="h-4 w-4" />
        </button>

        {/* Notifications */}
        <button
          className="relative p-2 rounded-lg transition-colors duration-200 hover:bg-white/5"
          style={{ color: 'var(--color-text-secondary)' }}
          id="notifications-button"
        >
          <Bell className="h-4 w-4" />
          <span
            className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full flex items-center justify-center text-xs font-bold text-white"
            style={{ background: 'var(--color-accent-rose)', fontSize: '10px' }}
          >
            3
          </span>
        </button>
      </div>
    </header>
  )
}
