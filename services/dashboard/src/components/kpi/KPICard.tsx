import { type ReactNode } from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface KPICardProps {
  title: string
  value: string | number
  change?: number
  changeLabel?: string
  icon: ReactNode
  format?: 'number' | 'percentage' | 'currency' | 'duration'
  id?: string
  className?: string
}

export default function KPICard({
  title,
  value,
  change,
  changeLabel = 'vs yesterday',
  icon,
  id,
  className,
}: KPICardProps) {
  const isPositive = change !== undefined && change > 0
  const isNegative = change !== undefined && change < 0

  return (
    <div className={`
      relative overflow-hidden glass-strong border border-border-default rounded-2xl p-6
      transition-all duration-400 ease-out hover:-translate-y-1 hover:border-accent-blue/30 
      hover:shadow-[0_12px_40px_rgba(0,0,0,0.4),0_0_0_1px_rgba(59,130,246,0.1),inset_0_1px_0_rgba(255,255,255,0.1)]
      metric-overlay-gradient ${className || ''}
    `} id={id}>
      <div className="flex items-start justify-between relative z-10">
        <div>
          <p className="text-sm font-medium text-text-secondary">{title}</p>
          <h3 className="text-3xl font-bold mt-2 gradient-text-primary drop-shadow-[0_0_30px_rgba(96,165,250,0.3)]">
            {value}
          </h3>
        </div>
        <div className="w-14 h-14 rounded-2xl flex items-center justify-center bg-gradient-to-br from-accent-blue/20 to-accent-blue/5">
          <div className="text-accent-blue filter drop-shadow-[0_0_8px_rgba(59,130,246,0.4)]">
            {icon}
          </div>
        </div>
      </div>

      {/* Change indicator */}
      {change !== undefined && (
        <div className="flex items-center gap-2 mt-4 relative z-10">
          <div className={`
            flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-[13px] font-semibold backdrop-blur-md
            ${isPositive ? 'bg-accent-green/15 text-accent-green border border-accent-green/20' : 
              isNegative ? 'bg-accent-red/15 text-accent-red border border-accent-red/20' : 
              'bg-dark-bg-tertiary/50 text-text-secondary border border-border-subtle'}
          `}>
            {isPositive && <TrendingUp className="h-3.5 w-3.5" />}
            {isNegative && <TrendingDown className="h-3.5 w-3.5" />}
            {!isPositive && !isNegative && <Minus className="h-3.5 w-3.5" />}
            <span>
              {isPositive ? '+' : ''}
              {change}%
            </span>
          </div>
          <span className="text-xs font-medium text-text-tertiary">
            {changeLabel}
          </span>
        </div>
      )}
    </div>
  )
}
