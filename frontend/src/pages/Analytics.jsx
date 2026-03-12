import { useState, useEffect } from 'react'
import { useAuth } from '../App'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter } from 'recharts'
import { healthAPI, scoreAPI } from '../services/api'

export default function Analytics() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [weekData, setWeekData] = useState([])
  const [scoreHistory, setScoreHistory] = useState([])

  useEffect(() => {
    loadAnalyticsData()
  }, [user])

  const loadAnalyticsData = async () => {
    if (!user) return
    setLoading(true)
    try {
      const [healthRes, scoresRes] = await Promise.all([
        healthAPI.getWeekHealth(user.id).catch(() => ({ records: [] })),
        scoreAPI.getScoreHistory(user.id, 30).catch(() => [])
      ])

      const formattedWeek = (healthRes.records || []).map(r => ({
        date: new Date(r.date).toLocaleDateString('en-US', { weekday: 'short' }),
        sleep: r.sleep_hours,
        steps: r.steps,
        stress: r.stress_level,
        heartRate: r.heart_rate
      }))

      setWeekData(formattedWeek)
      setScoreHistory(scoresRes.map(s => ({
        date: new Date(s.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        score: s.overall_score
      })))
    } catch (error) {
      console.error('Failed to load analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Analytics</h1>
        <p className="text-slate-500">Track your health trends over time</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Weekly Wellness Score Trend</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={scoreHistory.slice(-7)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} domain={[0, 100]} />
                <Tooltip />
                <Line type="monotone" dataKey="score" stroke="#0ea5e9" strokeWidth={2} dot={{ fill: '#0ea5e9' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Sleep vs Stress</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="sleep" name="Sleep" stroke="#64748b" fontSize={12} />
                <YAxis dataKey="stress" name="Stress" stroke="#64748b" fontSize={12} />
                <Tooltip />
                <Scatter data={weekData} fill="#0ea5e9" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Steps This Week</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={weekData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip />
                <Line type="monotone" dataKey="steps" stroke="#22c55e" strokeWidth={2} dot={{ fill: '#22c55e' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Sleep Hours This Week</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={weekData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} domain={[0, 12]} />
                <Tooltip />
                <Line type="monotone" dataKey="sleep" stroke="#8b5cf6" strokeWidth={2} dot={{ fill: '#8b5cf6' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
