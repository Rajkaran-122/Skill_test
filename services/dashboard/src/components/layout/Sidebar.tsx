import { LayoutDashboard, BarChart3, AlertTriangle, Settings, Store, Activity } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
  { icon: BarChart3, label: 'Analytics', path: '/analytics' },
  { icon: AlertTriangle, label: 'Alerts', path: '/alerts' },
  { icon: Store, label: 'Stores', path: '/stores' },
  { icon: Settings, label: 'Settings', path: '/settings' },
]

export default function Sidebar() {
  return (
    <aside
      className="flex w-64 flex-col border-r"
      style={{
        background: 'var(--color-bg-secondary)',
        borderColor: 'var(--color-border)',
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b" style={{ borderColor: 'var(--color-border)' }}>
        <div
          className="flex h-10 w-10 items-center justify-center rounded-xl"
          style={{ background: 'var(--gradient-primary)' }}
        >
          <Activity className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold" style={{ color: 'var(--color-text-primary)' }}>SIP</h1>
          <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Store Intelligence</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'text-white'
                  : ''
              }`
            }
            style={({ isActive }) => ({
              background: isActive ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
              color: isActive ? 'var(--color-accent-blue)' : 'var(--color-text-secondary)',
            })}
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Status Footer */}
      <div className="px-4 py-4 border-t" style={{ borderColor: 'var(--color-border)' }}>
        <div className="flex items-center gap-2">
          <span className="status-dot status-dot--active" />
          <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>System Online</span>
        </div>
      </div>
    </aside>
  )
}
