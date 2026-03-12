import { useState, useEffect } from 'react'
import { useAuth } from '../App'
import WellnessScoreCard from '../components/WellnessScoreCard'
import HealthMetricCard from '../components/HealthMetricCard'
import InsightCard from '../components/InsightCard'
import PatternAlert from '../components/PatternAlert'
import AddHealthDataModal from '../components/AddHealthDataModal'
import { healthAPI, scoreAPI, insightAPI } from '../services/api'
import { RefreshCw, Plus } from 'lucide-react'

export default function Dashboard() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [score, setScore] = useState(null)
  const [todayHealth, setTodayHealth] = useState(null)
  const [insight, setInsight] = useState(null)
  const [patterns, setPatterns] = useState([])
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    loadDashboardData()
  }, [user])

  const loadDashboardData = async () => {
    if (!user) return
    setLoading(true)
    try {
      const [scoreRes, healthRes, insightRes, patternsRes] = await Promise.all([
        scoreAPI.getTodayScore(user.id).catch(() => null),
        healthAPI.getTodayHealth(user.id).catch(() => ({ records: [] })),
        insightAPI.getDailyInsight(user.id).catch(() => null),
        insightAPI.getAlerts(user.id).catch(() => [])
      ])
      setScore(scoreRes)
      setTodayHealth(healthRes.records?.[0] || null)
      setInsight(insightRes)
      setPatterns(Array.isArray(patternsRes) ? patternsRes : [])
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSync = async () => {
    setRefreshing(true)
    try {
      await healthAPI.syncGoogleFit(user.id)
      await loadDashboardData()
    } catch (error) {
      console.error('Failed to sync:', error)
    } finally {
      setRefreshing(false)
    }
  }

  const getScoreColor = (value) => {
    if (value >= 75) return 'green'
    if (value >= 50) return 'yellow'
    return 'red'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const metrics = [
    { label: 'Sleep', value: todayHealth?.sleep_hours, unit: 'hrs', icon: '🌙', good: todayHealth?.sleep_hours >= 7 },
    { label: 'Steps', value: todayHealth?.steps, unit: 'steps', icon: '👟', good: todayHealth?.steps >= 5000 },
    { label: 'Heart Rate', value: todayHealth?.heart_rate, unit: 'bpm', icon: '❤️', good: todayHealth?.heart_rate < 90 },
    { label: 'Stress', value: todayHealth?.stress_level, unit: '/10', icon: '🧘', good: todayHealth?.stress_level <= 5 },
    { label: 'Screen Time', value: todayHealth?.screen_time, unit: 'hrs', icon: '📱', good: todayHealth?.screen_time <= 4 },
    { label: 'Calories', value: todayHealth?.calories, unit: 'kcal', icon: '🔥', good: todayHealth?.calories >= 1500 },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Welcome back, {user?.name || 'User'}!</h1>
          <p className="text-slate-500">Here's your health overview for today</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleSync}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            Sync Fit
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Add Data
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <WellnessScoreCard
            score={score?.overall_score || 0}
            sleepScore={score?.sleep_score}
            activityScore={score?.activity_score}
            heartRateScore={score?.heart_rate_score}
            stressScore={score?.stress_score}
          />
        </div>

        <div className="lg:col-span-2">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {metrics.map((metric) => (
              <HealthMetricCard
                key={metric.label}
                label={metric.label}
                value={metric.value}
                unit={metric.unit}
                icon={metric.icon}
                good={metric.good}
              />
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {insight?.insight && (
          <InsightCard
            insight={insight.insight}
            suggestions={insight.suggestions || []}
          />
        )}

        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold text-slate-800">Health Alerts</h2>
            {patterns.length > 0 && (
              <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-orange-100 text-orange-700">
                {patterns.length}
              </span>
            )}
          </div>
          {patterns.length > 0 ? (
            <div className="space-y-3">
              {patterns.slice(0, 5).map((pattern, idx) => (
                <PatternAlert
                  key={pattern.id ?? idx}
                  type={pattern.pattern_type}
                  description={pattern.description}
                  severity={pattern.severity}
                />
              ))}
            </div>
          ) : (
            <div className="bg-green-50 border border-green-100 rounded-xl p-6 text-center">
              <div className="text-3xl mb-2">✅</div>
              <p className="text-green-700 font-semibold text-sm">All Clear!</p>
              <p className="text-green-600 text-xs mt-1">No health alerts today. Keep it up!</p>
            </div>
          )}
        </div>
      </div>

      {showAddModal && (
        <AddHealthDataModal
          onClose={() => setShowAddModal(false)}
          onSuccess={() => {
            setShowAddModal(false)
            setInsight(null)
            setPatterns([])
            loadDashboardData()
          }}
        />
      )}
    </div>
  )
}
