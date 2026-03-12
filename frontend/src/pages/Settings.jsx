import { useState } from 'react'
import { useAuth } from '../App'
import { authAPI } from '../services/api'
import { Check, X, Globe } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

export default function Settings() {
  const { user } = useAuth()
  const { language, setLanguage, t } = useLanguage()
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
        <h1 className="text-2xl font-bold text-slate-800">{t.settings.title}</h1>
        <p className="text-slate-500">{t.settings.desc}</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Globe className="h-5 w-5 text-primary-600" />
          {t.settings.language}
        </h2>
        <div className="grid grid-cols-3 gap-4">
          {[
            { id: 'en', name: 'English', native: 'English' },
            { id: 'hi', name: 'Hindi', native: 'हिन्दी' },
            { id: 'te', name: 'Telugu', native: 'తెలుగు' }
          ].map(lang => (
            <button
              key={lang.id}
              onClick={() => setLanguage(lang.id)}
              className={`p-4 rounded-xl border-2 transition-all text-center ${language === lang.id
                ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200'
                : 'border-slate-100 bg-white hover:border-slate-200'
                }`}
            >
              <div className="font-bold text-slate-800">{lang.native}</div>
              <div className="text-xs text-slate-400 font-medium">{lang.name}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">{t.settings.account}</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b border-slate-100">
            <div>
              <p className="font-medium text-slate-700">{t.settings.name}</p>
              <p className="text-sm text-slate-500">{user?.name || 'Not set'}</p>
            </div>
          </div>
          <div className="flex items-center justify-between py-3 border-b border-slate-100">
            <div>
              <p className="font-medium text-slate-700">{t.settings.email}</p>
              <p className="text-sm text-slate-500">{user?.email}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">{t.settings.googleFit}</h2>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium text-slate-700">{t.settings.connect}</p>
            <p className="text-sm text-slate-500">{t.settings.connectDesc}</p>
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
                {t.settings.connected}
              </>
            ) : connecting ? (
              t.login.connecting
            ) : (
              t.settings.connect
            )}
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">{t.settings.notifications}</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-slate-700">{t.settings.reminders}</p>
              <p className="text-sm text-slate-500">{t.settings.remindersDesc}</p>
            </div>
            <button className="w-12 h-6 bg-primary-600 rounded-full relative">
              <span className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full transition-all"></span>
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-slate-700">{t.settings.insights}</p>
              <p className="text-sm text-slate-500">{t.settings.insightsDesc}</p>
            </div>
            <button className="w-12 h-6 bg-slate-200 rounded-full relative">
              <span className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-all"></span>
            </button>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">{t.settings.goals}</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">{t.settings.stepGoal}</label>
            <input
              type="number"
              defaultValue={10000}
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">{t.settings.sleepGoal}</label>
            <input
              type="number"
              step="0.5"
              defaultValue={8}
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button className="px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700">
            {t.settings.save}
          </button>
        </div>
      </div>
    </div>
  )
}
