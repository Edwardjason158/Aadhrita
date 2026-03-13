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

    </div>
  )
}
