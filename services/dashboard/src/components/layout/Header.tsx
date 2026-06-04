import { useState, useEffect } from 'react'
import { Search, User, Bell, Settings, LogOut } from 'lucide-react'
import { useAuthStore } from '../../hooks/useAuthStore'

export default function Header() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const logout = useAuthStore((state) => state.logout)

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <header className="h-16 glass-light border-b border-border-default flex items-center justify-between px-8 sticky top-0 z-40 transition-all duration-300">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary" />
        <input
          type="text"
          placeholder="Search stores, metrics..."
          className="pl-10 pr-4 py-2 rounded-xl text-sm w-72 bg-white/5 border border-white/10 backdrop-blur-md focus:border-accent-blue/40 focus:ring-4 focus:ring-accent-blue/10 focus:shadow-[0_8px_24px_rgba(59,130,246,0.2)] focus:scale-[1.02] outline-none transition-all duration-300 text-text-primary placeholder-text-tertiary"
          id="global-search"
        />
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-6">
        {/* Live indicator */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-accent-green/15 border border-accent-green/30 text-accent-green rounded-full shadow-[0_0_12px_rgba(16,185,129,0.2)]">
          <div className="w-2 h-2 rounded-full bg-accent-green animate-live-pulse" style={{ boxShadow: '0 0 12px rgba(16, 185, 129, 0.8)' }} />
          <span className="text-xs font-semibold tracking-wide uppercase">Live</span>
        </div>

        {/* Clock */}
        <div className="text-sm font-medium text-text-secondary font-mono tracking-tight" id="header-clock">
          {currentTime.toLocaleTimeString()}
        </div>

        <div className="h-6 w-px bg-dark-bg-tertiary" />

        {/* Actions */}
        <button className="p-2 text-text-secondary hover:text-text-primary hover:bg-accent-blue/15 hover:rotate-90 hover:shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:text-accent-blue rounded-lg transition-all duration-300">
          <Settings className="h-5 w-5" />
        </button>

        {/* Notifications */}
        <button className="p-2 text-text-secondary hover:text-text-primary hover:bg-accent-blue/15 hover:shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:text-accent-blue rounded-lg transition-all duration-300 relative">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-accent-red rounded-full border-2 border-dark-bg-secondary" />
        </button>
        
        {/* Profile */}
        <button className="h-9 w-9 rounded-xl bg-gradient-to-br from-accent-blue to-accent-blue flex items-center justify-center text-white shadow-[0_0_15px_rgba(59,130,246,0.4)] transition-all duration-300 hover:scale-105">
          <User className="h-5 w-5" />
        </button>

        {/* Logout */}
        <button 
          onClick={logout}
          title="Logout"
          className="p-2 text-text-secondary hover:text-accent-red hover:bg-accent-red/15 hover:shadow-[0_0_20px_rgba(239,68,68,0.3)] rounded-lg transition-all duration-300"
        >
          <LogOut className="h-5 w-5" />
        </button>
      </div>
    </header>
  )
}
