import { createContext, useContext, useState, useEffect } from 'react'
import { translations } from '../translations'

const LanguageContext = createContext(null)

export const useLanguage = () => useContext(LanguageContext)

export const LanguageProvider = ({ children }) => {
    const [language, setLanguage] = useState(null)

    const t = translations[language || 'en']

    const changeLanguage = (lang) => {
        setLanguage(lang)
        localStorage.setItem('app_language', lang)
    }

    return (
        <LanguageContext.Provider value={{ language, setLanguage: changeLanguage, t }}>
            {children}
        </LanguageContext.Provider>
    )
}
