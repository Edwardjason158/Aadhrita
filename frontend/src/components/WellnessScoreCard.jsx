export default function WellnessScoreCard({ score, sleepScore, activityScore, heartRateScore, stressScore }) {
  const getScoreColor = (value) => {
    if (value >= 75) return '#22c55e'
    if (value >= 50) return '#eab308'
    return '#ef4444'
  }

  const getScoreLabel = (value) => {
    if (value >= 85) return 'Excellent'
    if (value >= 75) return 'Good'
    if (value >= 60) return 'Fair'
    if (value >= 50) return 'Needs Improvement'
    return 'Poor'
  }

  const color = getScoreColor(score)
  const circumference = 2 * Math.PI * 70
  const strokeDashoffset = circumference - (score / 100) * circumference

  const categories = [
    { label: 'Sleep', score: sleepScore, weight: '30%' },
    { label: 'Activity', score: activityScore, weight: '25%' },
    { label: 'Heart Rate', score: heartRateScore, weight: '25%' },
    { label: 'Stress', score: stressScore, weight: '20%' },
  ]

  return (
    <div className="bg-white rounded-xl p-6 border border-slate-200">
      <h2 className="text-lg font-semibold text-slate-800 mb-4">Wellness Score</h2>
      
      <div className="flex items-center justify-center mb-6">
        <div className="relative w-40 h-40">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="80"
              cy="80"
              r="70"
              fill="none"
              stroke="#e2e8f0"
              strokeWidth="12"
            />
            <circle
              cx="80"
              cy="80"
              r="70"
              fill="none"
              stroke={color}
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className="transition-all duration-1000"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-4xl font-bold text-slate-800">{Math.round(score)}</span>
            <span className="text-sm text-slate-500">{getScoreLabel(score)}</span>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {categories.map((cat) => (
          <div key={cat.label} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-slate-600">{cat.label}</span>
              <span className="text-xs text-slate-400">({cat.weight})</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-20 h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${cat.score || 0}%`,
                    backgroundColor: getScoreColor(cat.score || 0)
                  }}
                />
              </div>
              <span className="text-sm font-semibold text-slate-700 w-8">
                {Math.round(cat.score || 0)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
