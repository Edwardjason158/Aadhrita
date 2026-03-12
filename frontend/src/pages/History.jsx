import { useState, useEffect } from 'react'
import { useAuth } from '../App'
import { healthAPI, analyticsAPI } from '../services/api'
import { Download, Database, User } from 'lucide-react'

export default function History() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [records, setRecords] = useState([])
  const [datasetRecords, setDatasetRecords] = useState([])
  const [activeTab, setActiveTab] = useState('myrecords')

  useEffect(() => {
    loadRecords()
  }, [user])

  const loadRecords = async () => {
    if (!user) return
    setLoading(true)
    try {
      const [userRecords, csvRecords] = await Promise.all([
        healthAPI.getRecords(user.id, { limit: 50 }).catch(() => []),
        analyticsAPI.getDataset().catch(() => [])
      ])
      setRecords(userRecords)
      setDatasetRecords(csvRecords)
    } catch (error) {
      console.error('Failed to load records:', error)
    } finally {
      setLoading(false)
    }
  }

  const exportData = () => {
    const isDataset = activeTab === 'dataset'
    const csvContent = isDataset
      ? [
        ['Date', 'Sleep (hrs)', 'Steps', 'Heart Rate', 'Stress Level', 'Screen Time (hrs)', 'Calories', 'Wellness Score'].join(','),
        ...datasetRecords.map(r => [
          r.date, r.sleep_hours, r.steps, r.heart_rate,
          r.stress_level, r.screen_time, r.calories_burned, r.wellness_score
        ].join(','))
      ].join('\n')
      : [
        ['Date', 'Sleep (hrs)', 'Steps', 'Heart Rate', 'Stress Level', 'Screen Time (hrs)', 'Calories', 'Source'].join(','),
        ...records.map(r => [
          new Date(r.date).toLocaleDateString(),
          r.sleep_hours || '', r.steps || '', r.heart_rate || '',
          r.stress_level || '', r.screen_time || '', r.calories || '', r.data_source
        ].join(','))
      ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = isDataset ? 'wellness-dataset.csv' : 'health-data.csv'
    a.click()
  }

  const tabs = [
    { id: 'myrecords', label: 'My Records', icon: User, count: records.length },
    { id: 'dataset', label: 'Dataset Records', icon: Database, count: datasetRecords.length },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Health History</h1>
          <p className="text-slate-500">View and export your past health records and dataset</p>
        </div>
        <button
          onClick={exportData}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
        >
          <Download className="h-4 w-4" />
          Export CSV
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 p-1 rounded-xl w-fit">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id
              ? 'bg-white text-slate-800 shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
              }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
            <span className={`text-xs px-1.5 py-0.5 rounded-full font-semibold ${activeTab === tab.id ? 'bg-primary-100 text-primary-700' : 'bg-slate-200 text-slate-500'
              }`}>
              {tab.count}
            </span>
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            {activeTab === 'myrecords' ? (
              <table className="w-full">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    {['Date', 'Sleep', 'Steps', 'Heart Rate', 'Stress', 'Screen Time', 'Calories', 'Source'].map(h => (
                      <th key={h} className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {records.length > 0 ? records.map((record) => (
                    <tr key={record.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{new Date(record.date).toLocaleDateString()}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-800">{record.sleep_hours ? `${record.sleep_hours} hrs` : '-'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-800">{record.steps?.toLocaleString() || '-'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-800">{record.heart_rate ? `${record.heart_rate} bpm` : '-'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-800">{record.stress_level ? `${record.stress_level}/10` : '-'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-800">{record.screen_time ? `${record.screen_time} hrs` : '-'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-800">{record.calories ? `${record.calories} kcal` : '-'}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${record.data_source === 'google_fit' ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'}`}>
                          {record.data_source === 'google_fit' ? 'Google Fit' : 'Manual'}
                        </span>
                      </td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan="8" className="px-6 py-12 text-center text-slate-400">
                        <User className="h-10 w-10 mx-auto mb-3 text-slate-200" />
                        No health records found. Start tracking your health!
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            ) : (
              <table className="w-full">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    {['Date', 'Sleep', 'Steps', 'Heart Rate', 'Stress', 'Screen Time', 'Calories Burned', 'Wellness Score'].map(h => (
                      <th key={h} className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {datasetRecords.length > 0 ? datasetRecords.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{row.date}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-800">{row.sleep_hours} hrs</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-800">{row.steps?.toLocaleString()}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-800">{row.heart_rate} bpm</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-800">{row.stress_level}/10</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-800">{row.screen_time} hrs</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-800">{row.calories_burned} kcal</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-slate-100 rounded-full h-1.5">
                            <div
                              className="h-1.5 rounded-full"
                              style={{
                                width: `${row.wellness_score}%`,
                                backgroundColor: row.wellness_score >= 80 ? '#22c55e' : row.wellness_score >= 60 ? '#f59e0b' : '#ef4444'
                              }}
                            ></div>
                          </div>
                          <span className={`text-xs font-bold ${row.wellness_score >= 80 ? 'text-green-600' : row.wellness_score >= 60 ? 'text-amber-600' : 'text-red-600'}`}>
                            {row.wellness_score}
                          </span>
                        </div>
                      </td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan="8" className="px-6 py-12 text-center text-slate-400">
                        <Database className="h-10 w-10 mx-auto mb-3 text-slate-200" />
                        No dataset records found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
