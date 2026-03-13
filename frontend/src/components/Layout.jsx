import { NavLink, Outlet } from 'react-router-dom'
import { Heart, LayoutDashboard, BarChart3, History, Settings, Brain } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

export default function Layout() {
  const { t } = useLanguage()

  const navItems = [
    { to: '/', icon: LayoutDashboard, label: t.nav.dashboard },
    { to: '/analytics', icon: BarChart3, label: t.nav.analytics },
    { to: '/history', icon: History, label: t.nav.history },
    { to: '/journal', icon: Brain, label: t.nav.journal },
    { to: '/settings', icon: Settings, label: t.nav.settings },
  ]

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex items-center gap-2">
                <Heart className="h-8 w-8 text-primary-600" />
                <span className="text-xl font-bold text-slate-800">{t.login.title}</span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-1">
                {navItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                      `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${isActive
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-slate-600 hover:bg-slate-50'
                      }`
                    }
                    end={item.to === '/'}
                  >
                    <item.icon className="h-4 w-4" />
                    {item.label}
                  </NavLink>
                ))}
              </div>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}
