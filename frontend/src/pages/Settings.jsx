import { useState } from 'react'
import { useAuth } from '../App'
import { authAPI } from '../services/api'
import { Check, X } from 'lucide-react'

export default function Settings() {
  const { user } = useAuth()
  const [connecting, setConnecting] = useState(false)
  const [connected, setConnected] = useState(!!user?.google_id)

  const handleConnectGoogleFit = async () => {
    setConnecting(true)
    try {
      const { url } = await authAPI.getGoogleAuthUrl()
      window.location.href = url
    } catch (error) {
      console.error('Failed to connect Google Fit:', error)
    } finally {
      setConnecting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Settings</h1>
        <p className="text-slate-500">Manage your account and preferences</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Account</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b border-slate-100">
            <div>
              <p className="font-medium text-slate-700">Name</p>
              <p className="text-sm text-slate-500">{user?.name || 'Not set'}</p>
            </div>
          </div>
          <div className="flex items-center justify-between py-3 border-b border-slate-100">
            <div>
              <p className="font-medium text-slate-700">Email</p>
              <p className="text-sm text-slate-500">{user?.email}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Google Fit Integration</h2>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium text-slate-700">Connect Google Fit</p>
            <p className="text-sm text-slate-500">Sync your health data automatically from Google Fit</p>
          </div>
          <button
            onClick={handleConnectGoogleFit}
            disabled={connecting || connected}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${connected
                ? 'bg-green-100 text-green-700'
                : 'bg-primary-600 text-white hover:bg-primary-700'
              } disabled:opacity-50`}
          >
            {connected ? (
              <>
                <Check className="h-4 w-4" />
                Connected
              </>
            ) : connecting ? (
              'Connecting...'
            ) : (
              'Connect'
            )}
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Notifications</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-slate-700">Daily Reminders</p>
              <p className="text-sm text-slate-500">Get reminded to log your health data</p>
            </div>
            <button className="w-12 h-6 bg-primary-600 rounded-full relative">
              <span className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full transition-all"></span>
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-slate-700">Weekly Insights</p>
              <p className="text-sm text-slate-500">Receive weekly AI-powered health insights</p>
            </div>
            <button className="w-12 h-6 bg-slate-200 rounded-full relative">
              <span className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-all"></span>
            </button>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Health Goals</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Daily Step Goal</label>
            <input
              type="number"
              defaultValue={10000}
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Sleep Goal (hours)</label>
            <input
              type="number"
              step="0.5"
              defaultValue={8}
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button className="px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700">
            Save Goals
          </button>
        </div>
      </div>
    </div>
  )
}
