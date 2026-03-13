import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect, createContext, useContext } from 'react'
import Dashboard from './pages/Dashboard'
import Analytics from './pages/Analytics'
import History from './pages/History'
import Settings from './pages/Settings'
import Layout from './components/Layout'
import Chatbot from './components/Chatbot'
import { LanguageProvider, useLanguage } from './context/LanguageContext'
import LanguageSelector from './components/LanguageSelector'

export const AuthContext = createContext(null)

export const useAuth = () => useContext(AuthContext)

function AppContent() {
  const { user, login } = useAuth()
  const { language } = useLanguage()

  // Auto-login as demo user if language is selected but no user exists
  useEffect(() => {
    if (language && !user) {
      const performAutoLogin = async () => {
        try {
          const { authAPI } = await import('./services/api')
          const demoUser = await authAPI.demoLogin()
          login(demoUser)
        } catch (error) {
          console.error('Auto demo login failed:', error)
          // Fallback demo user
          login({ id: 1, name: 'Demo User', email: 'demo@example.com' })
        }
      }
      performAutoLogin()
    }
  }, [language, user, login])

  if (!language) {
    return <LanguageSelector />
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={user ? <Layout /> : <div className="min-h-screen bg-slate-50 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>}>
          <Route index element={<Dashboard />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="history" element={<History />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
      {user && <Chatbot />}
    </Router>
  )
}

function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user')
    return saved ? JSON.parse(saved) : null
  })

  const login = (userData) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  return (
    <AuthContext.Provider value={{ user, login }}>
      <LanguageProvider>
        <AppContent />
      </LanguageProvider>
    </AuthContext.Provider>
  )
}

export default App
