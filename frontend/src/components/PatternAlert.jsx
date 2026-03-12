import { AlertTriangle, Info, CheckCircle } from 'lucide-react'

export default function PatternAlert({ type, description, severity }) {
  const getSeverityConfig = (sev) => {
    switch (sev) {
      case 'critical':
        return { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-800', icon: AlertTriangle }
      case 'high':
        return { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-800', icon: AlertTriangle }
      case 'medium':
        return { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-800', icon: Info }
      default:
        return { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-800', icon: CheckCircle }
    }
  }

  const config = getSeverityConfig(severity)
  const Icon = config.icon

  return (
    <div className={`${config.bg} ${config.border} border rounded-xl p-4`}>
      <div className="flex items-start gap-3">
        <Icon className={`h-5 w-5 ${config.text} flex-shrink-0 mt-0.5`} />
        <div>
          <h3 className={`font-semibold ${config.text}`}>{type}</h3>
          <p className={`text-sm ${config.text} opacity-80 mt-1`}>{description}</p>
        </div>
      </div>
    </div>
  )
}
