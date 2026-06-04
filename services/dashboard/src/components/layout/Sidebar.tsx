import { NavLink, useLocation } from 'react-router-dom'
import { LayoutDashboard, Video, AlertTriangle, Store } from 'lucide-react'

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: Video, label: 'Live Feeds', path: '/live' },
  { icon: AlertTriangle, label: 'Alerts Inbox', path: '/alerts' },
  { icon: Store, label: 'Stores Fleet', path: '/stores' },
]

export default function Sidebar({ isOpen = true }: { isOpen?: boolean }) {
  const location = useLocation()

  return (
    <aside className={`fixed left-0 top-0 h-full w-64 glass-medium text-text-secondary transition-all duration-300 z-50 ${isOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 md:relative`}>
      {/* Logo */}
      <div className="p-6 flex items-center justify-between border-b border-border-default bg-[radial-gradient(circle_at_top,rgba(59,130,246,0.15),transparent)]">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-accent-blue/10 rounded-lg" style={{ boxShadow: '0 0 30px rgba(59, 130, 246, 0.4)' }}>
            <LayoutDashboard className="h-6 w-6 text-accent-blue" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-accent-blue to-accent-cyan tracking-tight">SIP</h1>
            <p className="text-xs text-text-tertiary font-medium">Store Intelligence</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 border-l-4 ${
                isActive
                  ? 'bg-gradient-to-r from-accent-blue/15 to-transparent border-accent-blue text-text-primary shadow-[0_0_20px_rgba(59,130,246,0.2)]'
                  : 'border-transparent text-text-secondary hover:bg-accent-blue/5 hover:border-accent-blue hover:text-text-primary hover:translate-x-1'
              }`}
            >
              <item.icon className="h-5 w-5" />
              {item.label}
            </NavLink>
          )
        })}
      </nav>

      {/* Status Footer */}
      <div className="px-6 py-4 border-t border-border-subtle bg-dark-bg-tertiary">
        <div className="flex items-center gap-2">
          <span className="status-dot status-dot--active" />
          <span className="text-xs font-medium text-text-secondary">System Online</span>
        </div>
      </div>
    </aside>
  )
}
