import { useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../App'
import { authAPI } from '../services/api'

export default function AuthCallback() {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
    const { login } = useAuth()
    const hasProcessed = useRef(false)

    useEffect(() => {
        if (hasProcessed.current) return
        hasProcessed.current = true

        const code = searchParams.get('code')
        if (code) {
            authAPI.googleLogin(code)
                .then(user => {
                    login(user)
                    navigate('/')
                })
                .catch(err => {
                    console.error("Login failed", err)
                    navigate('/login')
                })
        } else {
            navigate('/login')
        }
    }, [searchParams, navigate, login])

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                <h2 className="text-xl font-semibold text-slate-700">Authenticating...</h2>
            </div>
        </div>
    )
}
