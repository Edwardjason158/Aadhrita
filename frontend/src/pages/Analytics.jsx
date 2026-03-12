import { useState, useEffect } from 'react'
import { useAuth } from '../App'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter } from 'recharts'
import { healthAPI, scoreAPI, analyticsAPI } from '../services/api'
import { Info, TrendingUp, TrendingDown, Activity } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

export default function Analytics() {
  const { user } = useAuth()
  const { t } = useLanguage()
  const [loading, setLoading] = useState(true)
  const [weekData, setWeekData] = useState([])
  const [scoreHistory, setScoreHistory] = useState([])
  const [correlation, setCorrelation] = useState(null)
  const [fullDataset, setFullDataset] = useState([])

  useEffect(() => {
    loadAnalyticsData()
  }, [user])

  const loadAnalyticsData = async () => {
    if (!user) return
    setLoading(true)
    try {
      const [healthRes, scoresRes, corrRes, datasetRes] = await Promise.all([
        healthAPI.getWeekHealth(user.id).catch(() => ({ records: [] })),
        scoreAPI.getScoreHistory(user.id, 30).catch(() => []),
        analyticsAPI.getCorrelation().catch(() => null),
        analyticsAPI.getDataset().catch(() => [])
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
      setCorrelation(corrRes)
      setFullDataset(datasetRes)
    } catch (error) {
      console.error('Failed to load analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  const getCorrColor = (val) => {
    if (val > 0.7) return 'bg-green-100 text-green-700'
    if (val > 0.4) return 'bg-green-50 text-green-600'
    if (val < -0.7) return 'bg-red-100 text-red-700'
    if (val < -0.4) return 'bg-red-50 text-red-600'
    return 'bg-slate-50 text-slate-500'
  }

  const formatLabel = (label) => label.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')

  const CustomScatterPlot = ({ title, data, xKey, yKey, xLabel, yLabel, color, xUnit = '', yUnit = '' }) => (
    <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm transition-all hover:shadow-md">
      <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
        <Activity className="h-5 w-5" style={{ color }} />
        {title}
      </h2>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
            <XAxis
              type="number"
              dataKey={xKey}
              name={xLabel}
              stroke="#64748b"
              fontSize={10}
              axisLine={false}
              tickLine={false}
              unit={xUnit}
            />
            <YAxis
              type="number"
              dataKey={yKey}
              name={yLabel}
              stroke="#64748b"
              fontSize={10}
              axisLine={false}
              tickLine={false}
              unit={yUnit}
            />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
            />
            <Scatter name="Data Points" data={data} fill={color} shape="circle" fillOpacity={0.6} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">{t.analytics.title}</h1>
          <p className="text-slate-500">{t.analytics.desc}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm transition-all hover:shadow-md h-full">
          <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Activity className="h-5 w-5 text-sky-500" />
            {t.analytics.scoreTrend}
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={fullDataset}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="date" hide={true} />
                <YAxis stroke="#64748b" fontSize={10} domain={[0, 100]} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  labelFormatter={(value) => `Date: ${value}`}
                />
                <Line
                  type="monotone"
                  dataKey="wellness_score"
                  stroke="#0ea5e9"
                  strokeWidth={3}
                  dot={false}
                  activeDot={{ r: 6, strokeWidth: 0 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <CustomScatterPlot
          title={t.analytics.sleepStress}
          data={fullDataset}
          xKey="sleep_hours"
          yKey="stress_level"
          xLabel={t.dashboard.sleep}
          yLabel={t.dashboard.stress}
          color="#8b5cf6"
          xUnit="h"
          yUnit="/10"
        />

        <CustomScatterPlot
          title={t.analytics.stepsCalories}
          data={fullDataset}
          xKey="steps"
          yKey="calories_burned"
          xLabel={t.dashboard.steps}
          yLabel={t.dashboard.calories}
          color="#22c55e"
          yUnit=" kcal"
        />

        <CustomScatterPlot
          title={t.analytics.screenStress}
          data={fullDataset}
          xKey="screen_time"
          yKey="stress_level"
          xLabel={t.dashboard.screenTime}
          yLabel={t.dashboard.stress}
          color="#f43f5e"
          xUnit="h"
          yUnit="/10"
        />

        <CustomScatterPlot
          title={t.analytics.sleepWellness}
          data={fullDataset}
          xKey="sleep_hours"
          yKey="wellness_score"
          xLabel={t.dashboard.sleep}
          yLabel={t.dashboard.score}
          color="#0ea5e9"
          xUnit="h"
        />
      </div>
    </div>
  )
}
