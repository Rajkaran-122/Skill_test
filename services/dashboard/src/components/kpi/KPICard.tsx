import { type ReactNode } from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface KPICardProps {
  title: string
  value: string | number
  change?: number
  changeLabel?: string
  icon: ReactNode
  accentColor: string
  format?: 'number' | 'percentage' | 'currency' | 'duration'
  id: string
}

export default function KPICard({
  title,
  value,
  change,
  changeLabel = 'vs yesterday',
  icon,
  accentColor,
  id,
}: KPICardProps) {
  const isPositive = change !== undefined && change > 0
  const isNegative = change !== undefined && change < 0

  return (
    <div className="kpi-card animate-fade-in" id={id}>
      {/* Accent glow */}
      <div
        className="absolute top-0 left-0 right-0 h-[3px] rounded-t-2xl"
        style={{ background: accentColor, opacity: 0.8 }}
      />

      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--color-text-muted)' }}>
            {title}
          </p>
          <p className="text-3xl font-bold tracking-tight animate-count-up" style={{ color: 'var(--color-text-primary)' }}>
            {value}
          </p>
        </div>
        <div
          className="flex h-10 w-10 items-center justify-center rounded-xl"
          style={{ background: `${accentColor}20`, color: accentColor }}
        >
          {icon}
        </div>
      </div>

      {/* Change indicator */}
      {change !== undefined && (
        <div className="flex items-center gap-1.5 mt-3">
          {isPositive && <TrendingUp className="h-3.5 w-3.5" style={{ color: 'var(--color-accent-emerald)' }} />}
          {isNegative && <TrendingDown className="h-3.5 w-3.5" style={{ color: 'var(--color-accent-rose)' }} />}
          {!isPositive && !isNegative && <Minus className="h-3.5 w-3.5" style={{ color: 'var(--color-text-muted)' }} />}

          <span
            className="text-xs font-semibold"
            style={{
              color: isPositive
                ? 'var(--color-accent-emerald)'
                : isNegative
                ? 'var(--color-accent-rose)'
                : 'var(--color-text-muted)',
            }}
          >
            {isPositive ? '+' : ''}
            {change}%
          </span>
          <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
            {changeLabel}
          </span>
        </div>
      )}
    </div>
  )
}
