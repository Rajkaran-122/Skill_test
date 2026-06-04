import { useState, useEffect } from 'react'
import KPICard from '../components/kpi/KPICard'
import { Users, Target, IndianRupee, ListOrdered, BellRing } from 'lucide-react'
import { fetchWithAuth } from '../utils/api'
import { useWebSocket } from '../hooks/useWebSocket'
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'

// Fallback mock data while loading
const defaultVisitorTrendData = [
  { time: '09:00', visitors: 0, purchases: 0 }
]

/* Enterprise Tooltip Style */
const ZONE_COLORS = ['#3b82f6', '#2563eb', '#1d4ed8', '#0ea5e9', '#0284c7']
const FUNNEL_COLORS = ['#3b82f6', '#2563eb', '#1d4ed8', '#0ea5e9', '#0284c7']

const chartTooltipStyle = {
  contentStyle: {
    background: '#09090b',
    border: 'none',
    borderRadius: '8px',
    color: '#f8fafc',
    fontSize: '12px',
    fontWeight: '500',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  },
  itemStyle: { color: '#f8fafc' },
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null)
  const [visitorTrend, setVisitorTrend] = useState(defaultVisitorTrendData)
  const [insights, setInsights] = useState<any[]>([])
  const [predictions, setPredictions] = useState<any[]>([])
  
  // Real DB data states
  const [zonePop, setZonePop] = useState<any[]>([])
  const [funnelData, setFunnelData] = useState<any[]>([])
  const [anomalies, setAnomalies] = useState<any[]>([])
  
  // Real-time WebSocket connection
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  useWebSocket({
    url: `${protocol}//${window.location.host}/api/v1/ws/dashboard/STORE001`,
    onMessage: (data: any) => {
      try {
        const parsedData = data;
        if (parsedData.type === 'METRICS_UPDATE') {
          // Optimistically update KPIs
        } else if (parsedData.type === 'EVENTS_BATCH') {
          // Additional handling for event counts if needed
        }
      } catch (e) {
        // Ignore non-JSON messages like 'pong'
      }
    }
  })

  useEffect(() => {
    const loadData = async () => {
      try {
        const [res, insightsRes, predsRes, funnelRes, heatmapRes, anomaliesRes] = await Promise.all([
          fetchWithAuth('/api/v1/stores/STORE001/metrics'),
          fetchWithAuth('/api/v1/stores/STORE001/insights'),
          fetchWithAuth('/api/v1/stores/STORE001/predictions'),
          fetchWithAuth('/api/v1/stores/STORE001/funnel'),
          fetchWithAuth('/api/v1/stores/STORE001/heatmap'),
          fetchWithAuth('/api/v1/stores/STORE001/anomalies')
        ])
        if (res.ok) {
          const data = await res.json()
          setMetrics(data.kpis)
          setVisitorTrend(data.visitor_trend)
        }
        if (insightsRes.ok) {
          const data = await insightsRes.json()
          setInsights(data.insights)
        }
        if (predsRes.ok) {
          const data = await predsRes.json()
          setPredictions(data.forecast)
        }
        if (funnelRes.ok) {
          const data = await funnelRes.json()
          setFunnelData(data.funnel.map((f: any) => ({
             stage: f.stage,
             count: f.count,
             pct: f.percentage
          })))
        }
        if (heatmapRes.ok) {
          const data = await heatmapRes.json()
          // Ensure we always have some zones so the chart doesn't crash if empty
          setZonePop(data.zones.length > 0 ? data.zones : [
            { zone: 'Entrance', visitors: 0 },
            { zone: 'Aisle', visitors: 0 }
          ])
        }
        if (anomaliesRes.ok) {
          const data = await anomaliesRes.json()
          setAnomalies(data.anomalies)
        }
      } catch (e) {
        console.error('Failed to load metrics', e)
      }
    }
    loadData()
  }, [])

  return (
    <div className="space-y-6 animate-fade-in max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6">
        <div>
          <h2 className="text-2xl font-bold gradient-text-primary tracking-tight">Overview</h2>
          <p className="text-sm text-text-secondary mt-1">Real-time metrics and predictive intelligence.</p>
        </div>
      </div>

      {/* AI Insights & Predictions Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Insights Box */}
        <div className="lg:col-span-2 bg-gray-900 border border-blue-500/30 rounded-xl p-5 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
          <h3 className="text-lg font-bold text-white flex items-center space-x-2 mb-4">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
            <span>AI Executive Summary</span>
          </h3>
          <div className="space-y-4">
            {insights.length === 0 ? (
              <p className="text-gray-400">Loading insights...</p>
            ) : (
              insights.map((insight, idx) => (
                <div key={idx} className="flex flex-col space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className={`text-sm font-semibold ${insight.type === 'warning' ? 'text-orange-400' : insight.type === 'success' ? 'text-green-400' : 'text-blue-400'}`}>
                      {insight.title}
                    </span>
                    {insight.action !== 'None' && (
                      <span className="text-xs bg-white/10 px-2 py-0.5 rounded text-gray-300">
                        Suggested Action: {insight.action}
                      </span>
                    )}
                  </div>
                  <p className="text-gray-300 text-sm">{insight.message}</p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Predictions Widget */}
        <div className="bg-gray-900 border border-purple-500/30 rounded-xl p-5 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-purple-500"></div>
          <h3 className="text-lg font-bold text-white mb-4 flex items-center space-x-2">
            <Target className="w-4 h-4 text-purple-400" />
            <span>Next 3 Hours Forecast</span>
          </h3>
          <div className="space-y-3">
            {predictions.length === 0 ? (
              <p className="text-gray-400">Loading predictions...</p>
            ) : (
              predictions.map((pred, idx) => (
                <div key={idx} className="flex justify-between items-center border-b border-gray-800 pb-2 last:border-0">
                  <span className="text-gray-300 font-medium">{pred.hour}</span>
                  <div className="text-right">
                    <div className="text-sm text-white">
                      {pred.expected_visitors} <span className="text-gray-500 text-xs">visitors</span>
                    </div>
                    <div className={`text-xs ${pred.risk_level === 'High' ? 'text-red-400' : 'text-green-400'}`}>
                      {pred.expected_queue_time_mins} min queue
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5">
        <KPICard
          id="kpi-visitors"
          title="Visitors Today"
          value={metrics?.visitors_today?.toLocaleString() || "..."}
          change={metrics?.visitors_change || 0}
          icon={<Users className="w-6 h-6" />}
        />
        <KPICard
          id="kpi-conversion"
          title="Conversion Rate"
          value={metrics ? `${metrics.conversion_rate}%` : "..."}
          change={metrics?.conversion_change || 0}
          icon={<Target className="w-6 h-6" />}
        />
        <KPICard
          id="kpi-revenue"
          title="Revenue"
          value={metrics ? `₹${metrics.revenue.toLocaleString()}` : "..."}
          change={metrics?.revenue_change || 0}
          icon={<IndianRupee className="w-6 h-6" />}
        />
        <KPICard
          id="kpi-queue"
          title="Avg Queue Depth"
          value={metrics?.queue_depth || "..."}
          change={metrics?.queue_change || 0}
          icon={<ListOrdered className="w-6 h-6" />}
        />
        <KPICard
          id="kpi-alerts"
          title="Active Alerts"
          value={metrics?.active_alerts || "..."}
          change={metrics?.alerts_change || 0}
          icon={<BellRing className="w-6 h-6" />}
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 gap-6">
        {/* Visitor Trend */}
        <div className="chart-container-glass stagger-3 animate-fade-in-up" id="chart-visitor-trend">
          <h3>Visitor Flow vs Purchases</h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={visitorTrend}>
              <defs>
                <linearGradient id="visitorGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="purchaseGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
              <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} dy={10} />
              <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} dx={-10} />
              <Tooltip {...(chartTooltipStyle as any)} />
              <Area type="monotone" dataKey="visitors" stroke="#3b82f6" fill="url(#visitorGrad)" strokeWidth={2} />
              <Area type="monotone" dataKey="purchases" stroke="#10b981" fill="url(#purchaseGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Zone Popularity */}
        <div className="chart-container-glass stagger-3 animate-fade-in-up" id="chart-zones">
          <h3>Zone Popularity</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={zonePop} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" horizontal={false} />
              <XAxis type="number" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis dataKey="zone" type="category" stroke="#64748b" fontSize={12} width={80} tickLine={false} axisLine={false} />
              <Tooltip {...(chartTooltipStyle as any)} />
              <Bar dataKey="visitors" radius={[0, 4, 4, 0]} barSize={20}>
                {zonePop.map((_, i) => (
                  <Cell key={i} fill={ZONE_COLORS[i % ZONE_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Conversion Funnel */}
        <div className="chart-container-glass stagger-3 animate-fade-in-up" id="chart-funnel">
          <h3>Conversion Funnel</h3>
          <div className="space-y-4 mt-2">
            {funnelData.length === 0 ? (
               <div className="text-gray-500 py-10 text-center">No funnel data available yet.</div>
            ) : (
              funnelData.map((stage, i) => (
                <div key={stage.stage} className="space-y-1.5">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-text-secondary">
                      {stage.stage}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-text-primary">
                        {stage.count.toLocaleString()}
                      </span>
                      <span className="text-xs font-medium text-text-secondary">
                        ({stage.pct.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                  <div className="h-2 bg-dark-bg-hover rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700 ease-out"
                      style={{
                        width: `${stage.pct}%`,
                        background: FUNNEL_COLORS[i % FUNNEL_COLORS.length],
                      }}
                    />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Alerts Row */}
      <div className="chart-container-glass stagger-3 animate-fade-in-up" id="alerts-panel">
        <h3>Active Alerts</h3>
        <div className="space-y-3 mt-1">
          {anomalies.length === 0 ? (
            <div className="bg-green-500/10 border border-green-500/50 text-green-400 p-4 rounded-xl flex items-center justify-center space-x-2 font-medium">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              <span>All Systems Normal</span>
            </div>
          ) : (
            anomalies.map((alert, i) => (
              <div
                key={i}
                className={`
                  grid grid-cols-[1fr_100px_80px] items-center gap-4 p-4 rounded-[10px] mb-3 relative overflow-hidden transition-all duration-300 ease-in-out hover:translate-x-1 hover:bg-[#050505]/80
                  ${alert.severity === 'CRITICAL' ? 'bg-[#050505]/60 border-l-[3px] border-accent-red animate-critical-pulse' : 
                    alert.severity === 'HIGH' ? 'bg-[#050505]/60 border-l-[3px] border-accent-amber hover:shadow-[-4px_0_12px_rgba(245,158,11,0.2)]' : 
                    'bg-[#050505]/60 border-l-[3px] border-accent-blue hover:shadow-[-4px_0_12px_rgba(59,130,246,0.2)]'}
                `}
              >
                <div>
                  <p className="text-sm font-semibold text-text-primary">{alert.description}</p>
                  <p className="text-xs font-medium text-text-secondary mt-0.5">{alert.type.replace('_', ' ')}</p>
                </div>
                <div className="flex justify-end">
                  <span className="bg-white/10 border border-white/20 px-2.5 py-1 rounded-md text-[11px] font-bold tracking-[0.5px] uppercase text-text-primary">
                    {alert.severity}
                  </span>
                </div>
                <span className="text-xs font-medium text-text-secondary text-right">{new Date(alert.detected_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  )
}
