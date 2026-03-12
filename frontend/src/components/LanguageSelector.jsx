import { useLanguage } from '../context/LanguageContext'
import { Globe, ArrowRight } from 'lucide-react'

export default function LanguageSelector() {
    const { setLanguage } = useLanguage()

    const languages = [
        { id: 'en', name: 'English', native: 'English', color: 'blue' },
        { id: 'hi', name: 'Hindi', native: 'हिन्दी', color: 'orange' },
        { id: 'te', name: 'Telugu', native: 'తెలుగు', color: 'emerald' }
    ]

    return (
        <div className="fixed inset-0 z-[100] bg-slate-50 flex items-center justify-center p-6">
            <div className="max-w-md w-full animate-in fade-in zoom-in duration-500">
                <div className="text-center mb-10">
                    <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-600 rounded-3xl shadow-xl shadow-primary-200 mb-6 text-white transform rotate-12">
                        <Globe className="w-10 h-10" />
                    </div>
                    <h1 className="text-3xl font-black text-slate-800 mb-2">Select Language</h1>
                    <p className="text-slate-500 font-medium">భాషను ఎంచుకోండి • भाषा चुनें</p>
                </div>

                <div className="space-y-4">
                    {languages.map((lang) => (
                        <button
                            key={lang.id}
                            onClick={() => setLanguage(lang.id)}
                            className="group w-full bg-white border-2 border-slate-100 p-5 rounded-2xl flex items-center justify-between hover:border-primary-500 hover:shadow-lg hover:shadow-primary-100 transition-all transform hover:-translate-y-1 active:scale-[0.98]"
                        >
                            <div className="flex items-center gap-5">
                                <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-black text-lg
                  ${lang.id === 'en' ? 'bg-blue-100 text-blue-600' :
                                        lang.id === 'hi' ? 'bg-orange-100 text-orange-600' :
                                            'bg-emerald-100 text-emerald-600'}`}
                                >
                                    {lang.id.toUpperCase()}
                                </div>
                                <div className="text-left">
                                    <div className="font-black text-slate-800 text-lg">{lang.native}</div>
                                    <div className="text-sm font-bold text-slate-400 uppercase tracking-widest">{lang.name}</div>
                                </div>
                            </div>
                            <ArrowRight className="w-6 h-6 text-slate-200 group-hover:text-primary-500 group-hover:translate-x-1 transition-all" />
                        </button>
                    ))}
                </div>

                <p className="text-center mt-12 text-slate-400 text-sm font-medium">
                    You can change this anytime in Settings
                </p>
            </div>
        </div>
    )
}
