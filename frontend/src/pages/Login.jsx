import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Heart, ArrowRight } from 'lucide-react'
import { useAuth } from '../App'
import { authAPI } from '../services/api'
import { useLanguage } from '../context/LanguageContext'

export default function Login() {
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()
  const { t } = useLanguage()

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="flex items-center justify-center gap-3 mb-8">
            <Heart className="h-10 w-10 text-primary-600" />
            <h1 className="text-3xl font-bold text-slate-800">{t.login.title}</h1>
          </div>

          <h2 className="text-xl font-semibold text-slate-700 text-center mb-2">
            {t.login.subtitle}
          </h2>
          <p className="text-slate-500 text-center mb-8">
            {t.login.desc}
          </p>

          <button
            onClick={async () => {
              setLoading(true)
              try {
                const demoUser = await authAPI.demoLogin()
                login(demoUser)
                navigate('/')
              } catch (err) {
                console.error('Failed to login:', err)
                alert(`Login Failed: ${err.message}. \n\nCheck if your backend is running at ${import.meta.env.VITE_API_URL || 'http://localhost:8000'}`)
              } finally {
                setLoading(false)
              }
            }}
            disabled={loading}
            className="w-full flex items-center justify-center gap-3 bg-primary-600 hover:bg-primary-700 text-white font-bold py-4 px-6 rounded-2xl shadow-lg hover:shadow-primary-200 transition-all duration-300 transform hover:-translate-y-1 active:scale-95 disabled:opacity-50"
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                {t.login.connecting}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                {t.nav.dashboard}
                <ArrowRight className="h-5 w-5" />
              </div>
            )}
          </button>
        </div>

        <p className="text-center text-slate-500 text-sm mt-6">
          {t.login.footer}
        </p>
      </div>
    </div>
  )
}
