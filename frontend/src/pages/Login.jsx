import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Heart, ArrowRight } from 'lucide-react'
import { useAuth } from '../App'
import { authAPI } from '../services/api'

export default function Login() {
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleGoogleLogin = async () => {
    setLoading(true)
    try {
      const { url } = await authAPI.getGoogleAuthUrl()
      window.location.href = url
    } catch (error) {
      console.error('Failed to get auth URL:', error)
      alert('Google Sign-In failed. Please ensure GOOGLE_CLIENT_ID is configured in the backend .env file.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="flex items-center justify-center gap-3 mb-8">
            <Heart className="h-10 w-10 text-primary-600" />
            <h1 className="text-3xl font-bold text-slate-800">Wellness</h1>
          </div>

          <h2 className="text-xl font-semibold text-slate-700 text-center mb-2">
            Track Your Health Journey
          </h2>
          <p className="text-slate-500 text-center mb-8">
            Connect with Google Fit or add data manually to get personalized AI insights
          </p>

          <button
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full flex items-center justify-center gap-3 bg-white border-2 border-slate-200 hover:border-primary-300 hover:bg-primary-50 text-slate-700 font-medium py-3 px-4 rounded-xl transition-all duration-200 disabled:opacity-50"
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            {loading ? 'Connecting...' : 'Sign in with Google'}
          </button>

          <div className="mt-6 text-center">
            <button
              onClick={async () => {
                setLoading(true)
                try {
                  const demoUser = await authAPI.demoLogin()
                  login(demoUser)
                  navigate('/')
                } catch (err) {
                  console.error('Failed to login as demo user:', err)
                } finally {
                  setLoading(false)
                }
              }}
              disabled={loading}
              className="text-primary-600 hover:text-primary-700 font-medium text-sm flex items-center justify-center gap-1 mx-auto disabled:opacity-50"
            >
              Try Demo Mode <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>

        <p className="text-center text-slate-500 text-sm mt-6">
          By signing in, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  )
}
