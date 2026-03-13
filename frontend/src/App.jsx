import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect, createContext, useContext } from 'react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Analytics from './pages/Analytics'
import History from './pages/History'
import Settings from './pages/Settings'
import Journal from './pages/Journal'
import AuthCallback from './pages/AuthCallback'
import Layout from './components/Layout'
import { LanguageProvider, useLanguage } from './context/LanguageContext'
import LanguageSelector from './components/LanguageSelector'

export const AuthContext = createContext(null)

export const useAuth = () => useContext(AuthContext)

function AppContent() {
  const { user, login, logout } = useAuth()
  const { language } = useLanguage()

  if (!language) {
    return <LanguageSelector />
  }

  return (
    <Router>
      <Routes>
        <Route path="/login" element={!user ? <Login /> : <Navigate to="/" />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/" element={user ? <Layout /> : <Navigate to="/login" />}>
          <Route index element={<Dashboard />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="history" element={<History />} />
          <Route path="journal" element={<Journal />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
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

  const logout = () => {
    setUser(null)
    localStorage.removeItem('user')
  }

  // Auto-login as demo user if no user exists
  useEffect(() => {
    if (!user) {
      const performAutoLogin = async () => {
        try {
          const { authAPI } = await import('./services/api')
          const demoUser = await authAPI.demoLogin()
          login(demoUser)
        } catch (error) {
          console.error('Auto demo login failed:', error)
          // Temporary fallback structure if backend is slow/offline
          login({ id: 1, name: 'Demo User', email: 'demo@example.com' })
        }
      }
      performAutoLogin()
    }
  }, [user])

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      <LanguageProvider>
        <AppContent />
      </LanguageProvider>
    </AuthContext.Provider>
  )
}

export default App
