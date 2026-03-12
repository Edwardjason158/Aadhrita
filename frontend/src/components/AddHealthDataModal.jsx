import { useState } from 'react'
import { X } from 'lucide-react'
import { useAuth } from '../App'
import { healthAPI, scoreAPI } from '../services/api'

export default function AddHealthDataModal({ onClose, onSuccess }) {
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    sleep_hours: '',
    steps: '',
    heart_rate: '',
    stress_level: '',
    screen_time: '',
    calories: ''
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const data = {}
      Object.entries(formData).forEach(([key, value]) => {
        if (value) data[key] = parseFloat(value)
      })
      await healthAPI.addManualHealth(user.id, data)
      await scoreAPI.calculateScore(user.id)
      onSuccess()
    } catch (error) {
      console.error('Failed to add health data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-slate-800">Add Health Data</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Sleep Hours</label>
            <input
              type="number"
              name="sleep_hours"
              step="0.1"
              min="0"
              max="24"
              value={formData.sleep_hours}
              onChange={handleChange}
              placeholder="7.5"
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Steps</label>
            <input
              type="number"
              name="steps"
              min="0"
              value={formData.steps}
              onChange={handleChange}
              placeholder="8000"
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Heart Rate (bpm)</label>
            <input
              type="number"
              name="heart_rate"
              min="30"
              max="220"
              value={formData.heart_rate}
              onChange={handleChange}
              placeholder="72"
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Stress Level (1-10)</label>
            <input
              type="number"
              name="stress_level"
              min="1"
              max="10"
              value={formData.stress_level}
              onChange={handleChange}
              placeholder="5"
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Screen Time (hours)</label>
            <input
              type="number"
              name="screen_time"
              step="0.5"
              min="0"
              max="24"
              value={formData.screen_time}
              onChange={handleChange}
              placeholder="4"
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Calories Burned</label>
            <input
              type="number"
              name="calories"
              min="0"
              value={formData.calories}
              onChange={handleChange}
              placeholder="2000"
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Saving...' : 'Save Data'}
          </button>
        </form>
      </div>
    </div>
  )
}
