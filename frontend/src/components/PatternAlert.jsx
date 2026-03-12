import { AlertTriangle, Info, Moon, Activity, Heart, Monitor, Flame } from 'lucide-react'

const TYPE_CONFIG = {
  low_sleep: { icon: '🌙', label: 'Low Sleep', iconComp: Moon },
  high_stress: { icon: '🧘', label: 'High Stress', iconComp: AlertTriangle },
  low_activity: { icon: '👟', label: 'Low Activity', iconComp: Activity },
  elevated_heart_rate: { icon: '❤️', label: 'Elevated Heart Rate', iconComp: Heart },
  high_screen_time: { icon: '📱', label: 'High Screen Time', iconComp: Monitor },
  high_calories: { icon: '🔥', label: 'Calorie Alert', iconComp: Flame },
}

const SEVERITY_CONFIG = {
  critical: {
    bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-800',
    badge: 'bg-red-100 text-red-700', dot: 'bg-red-500', label: 'Critical'
  },
  high: {
    bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-800',
    badge: 'bg-orange-100 text-orange-700', dot: 'bg-orange-500', label: 'High'
  },
  medium: {
    bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-800',
    badge: 'bg-amber-100 text-amber-700', dot: 'bg-amber-400', label: 'Medium'
  },
  low: {
    bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-800',
    badge: 'bg-green-100 text-green-700', dot: 'bg-green-500', label: 'Low'
  },
}

export default function PatternAlert({ type, description, severity }) {
  const sev = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.low
  const typeInfo = TYPE_CONFIG[type] || { icon: '⚠️', label: type?.replace(/_/g, ' ') || 'Alert' }

  return (
    <div className={`group relative overflow-hidden ${sev.bg} ${sev.border} border rounded-xl p-4 transition-all hover:shadow-md`}>
      <div className="absolute top-0 right-0 w-12 h-12 rounded-bl-full opacity-20"
        style={{ background: severity === 'critical' ? '#ef4444' : severity === 'high' ? '#f97316' : '#f59e0b' }}>
      </div>

      <div className="flex items-start gap-3">
        <div className="text-2xl leading-none mt-0.5 flex-shrink-0">{typeInfo.icon}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className={`font-semibold text-sm ${sev.text}`}>{typeInfo.label}</h3>
            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${sev.badge}`}>
              {sev.label}
            </span>
          </div>
          <p className={`text-xs leading-relaxed ${sev.text} opacity-80`}>{description}</p>
        </div>
        <div className={`w-2 h-2 rounded-full flex-shrink-0 mt-1.5 ${sev.dot} ${severity === 'critical' ? 'animate-pulse' : ''}`}></div>
      </div>
    </div>
  )
}
