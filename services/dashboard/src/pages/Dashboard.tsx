import { Users, ShoppingCart, Clock, TrendingUp, AlertTriangle } from 'lucide-react'
import KPICard from '../components/kpi/KPICard'
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'

/* ---- Sample Data (replaced by real-time data in production) ---- */
const visitorTrendData = [
  { time: '09:00', visitors: 45, purchases: 12 },
  { time: '10:00', visitors: 78, purchases: 25 },
  { time: '11:00', visitors: 112, purchases: 38 },
  { time: '12:00', visitors: 156, purchases: 52 },
  { time: '13:00', visitors: 143, purchases: 48 },
  { time: '14:00', visitors: 167, purchases: 55 },
  { time: '15:00', visitors: 189, purchases: 63 },
  { time: '16:00', visitors: 201, purchases: 68 },
  { time: '17:00', visitors: 178, purchases: 59 },
  { time: '18:00', visitors: 145, purchases: 47 },
]

const zonePop = [
  { zone: 'Skincare', visitors: 234, color: '#3b82f6' },
  { zone: 'Electronics', visitors: 189, color: '#8b5cf6' },
  { zone: 'Groceries', visitors: 156, color: '#06b6d4' },
  { zone: 'Fashion', visitors: 134, color: '#10b981' },
  { zone: 'Checkout', visitors: 316, color: '#f59e0b' },
]

const conversionData = [
  { time: '09:00', rate: 26.7 },
  { time: '10:00', rate: 32.1 },
  { time: '11:00', rate: 33.9 },
  { time: '12:00', rate: 33.3 },
  { time: '13:00', rate: 33.6 },
  { time: '14:00', rate: 32.9 },
  { time: '15:00', rate: 33.3 },
  { time: '16:00', rate: 33.8 },
  { time: '17:00', rate: 33.1 },
  { time: '18:00', rate: 32.4 },
]

const queueData = [
  { time: '09:00', depth: 2 },
  { time: '10:00', depth: 4 },
  { time: '11:00', depth: 6 },
  { time: '12:00', depth: 8 },
  { time: '13:00', depth: 5 },
  { time: '14:00', depth: 7 },
  { time: '15:00', depth: 9 },
  { time: '16:00', depth: 11 },
  { time: '17:00', depth: 7 },
  { time: '18:00', depth: 4 },
]

const funnelData = [
  { stage: 'Entry', count: 987, pct: 100 },
  { stage: 'Browse', count: 756, pct: 76.6 },
  { stage: 'Engage', count: 512, pct: 51.9 },
  { stage: 'Queue', count: 380, pct: 38.5 },
  { stage: 'Purchase', count: 316, pct: 32.0 },
]

const anomalies = [
  { type: 'QUEUE_SPIKE', severity: 'HIGH', desc: 'Queue depth 15 exceeds 3σ threshold', time: '2 min ago' },
  { type: 'DEAD_ZONE', severity: 'MEDIUM', desc: 'No traffic in Groceries for 35 min', time: '12 min ago' },
  { type: 'CAMERA_FAILURE', severity: 'CRITICAL', desc: 'CAM03 heartbeat lost', time: '5 min ago' },
]

const chartTooltipStyle = {
  contentStyle: {
    background: 'rgba(17, 24, 39, 0.95)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '12px',
    color: '#f1f5f9',
    fontSize: '13px',
  },
}

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <KPICard
          id="kpi-visitors"
          title="Visitors Today"
          value="1,234"
          change={12.5}
          icon={<Users className="h-5 w-5" />}
          accentColor="var(--color-accent-blue)"
        />
        <KPICard
          id="kpi-conversion"
          title="Conversion Rate"
          value="32.0%"
          change={2.1}
          icon={<ShoppingCart className="h-5 w-5" />}
          accentColor="var(--color-accent-emerald)"
        />
        <KPICard
          id="kpi-revenue"
          title="Revenue"
          value="₹4,58,900"
          change={8.3}
          icon={<TrendingUp className="h-5 w-5" />}
          accentColor="var(--color-accent-violet)"
        />
        <KPICard
          id="kpi-queue"
          title="Queue Depth"
          value="5"
          change={-15}
          icon={<Clock className="h-5 w-5" />}
          accentColor="var(--color-accent-cyan)"
        />
        <KPICard
          id="kpi-alerts"
          title="Active Alerts"
          value="3"
          change={50}
          icon={<AlertTriangle className="h-5 w-5" />}
          accentColor="var(--color-accent-rose)"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Visitor Trend */}
        <div className="chart-container animate-fade-in" id="chart-visitor-trend" style={{ animationDelay: '0.1s' }}>
          <h3>Visitor Flow</h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={visitorTrendData}>
              <defs>
                <linearGradient id="visitorGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="purchaseGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="time" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip {...chartTooltipStyle} />
              <Area type="monotone" dataKey="visitors" stroke="#3b82f6" fill="url(#visitorGrad)" strokeWidth={2} />
              <Area type="monotone" dataKey="purchases" stroke="#10b981" fill="url(#purchaseGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Conversion Rate */}
        <div className="chart-container animate-fade-in" id="chart-conversion" style={{ animationDelay: '0.2s' }}>
          <h3>Conversion Rate Trend</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={conversionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="time" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} domain={[25, 40]} unit="%" />
              <Tooltip {...chartTooltipStyle} />
              <Line type="monotone" dataKey="rate" stroke="#8b5cf6" strokeWidth={2.5} dot={{ r: 4, fill: '#8b5cf6' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Zone Popularity */}
        <div className="chart-container animate-fade-in" id="chart-zones" style={{ animationDelay: '0.3s' }}>
          <h3>Zone Popularity</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={zonePop} layout="vertical" margin={{ left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" stroke="#64748b" fontSize={12} />
              <YAxis dataKey="zone" type="category" stroke="#64748b" fontSize={12} width={80} />
              <Tooltip {...chartTooltipStyle} />
              <Bar dataKey="visitors" radius={[0, 6, 6, 0]} barSize={24}>
                {zonePop.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Queue Depth */}
        <div className="chart-container animate-fade-in" id="chart-queue" style={{ animationDelay: '0.4s' }}>
          <h3>Queue Depth</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={queueData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="time" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip {...chartTooltipStyle} />
              <Bar dataKey="depth" fill="#06b6d4" radius={[6, 6, 0, 0]} barSize={28}>
                {queueData.map((entry, i) => (
                  <Cell key={i} fill={entry.depth > 8 ? '#f43f5e' : entry.depth > 5 ? '#f59e0b' : '#06b6d4'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Conversion Funnel */}
        <div className="chart-container animate-fade-in" id="chart-funnel" style={{ animationDelay: '0.5s' }}>
          <h3>Conversion Funnel</h3>
          <div className="space-y-3 mt-2">
            {funnelData.map((stage, i) => {
              const colors = ['#3b82f6', '#8b5cf6', '#06b6d4', '#f59e0b', '#10b981']
              return (
                <div key={stage.stage} className="space-y-1.5">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium" style={{ color: 'var(--color-text-secondary)' }}>
                      {stage.stage}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold" style={{ color: 'var(--color-text-primary)' }}>
                        {stage.count.toLocaleString()}
                      </span>
                      <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                        ({stage.pct}%)
                      </span>
                    </div>
                  </div>
                  <div className="h-2.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.05)' }}>
                    <div
                      className="h-full rounded-full transition-all duration-700 ease-out"
                      style={{
                        width: `${stage.pct}%`,
                        background: colors[i],
                        boxShadow: `0 0 8px ${colors[i]}40`,
                      }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Alerts Row */}
      <div className="chart-container animate-fade-in" id="alerts-panel" style={{ animationDelay: '0.6s' }}>
        <h3>Active Alerts</h3>
        <div className="space-y-3">
          {anomalies.map((alert, i) => (
            <div
              key={i}
              className="flex items-center justify-between px-4 py-3 rounded-xl transition-colors duration-200 hover:bg-white/5"
              style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--color-border)' }}
            >
              <div className="flex items-center gap-3">
                <span className={`status-dot status-dot--${alert.severity === 'CRITICAL' ? 'critical' : alert.severity === 'HIGH' ? 'warning' : 'active'}`} />
                <div>
                  <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>{alert.desc}</p>
                  <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>{alert.type.replace('_', ' ')}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`badge badge--${alert.severity.toLowerCase()}`}>{alert.severity}</span>
                <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>{alert.time}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
