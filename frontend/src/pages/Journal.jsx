import { useState } from 'react'
import { nlpAPI } from '../services/api'
import { Brain, Activity, Heart, AlertTriangle, Smile, Frown, Meh, Sparkles, Languages } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

export default function Journal() {
    const { t } = useLanguage()
    const [text, setText] = useState('')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)

    const handleTextChange = (e) => {
        setText(e.target.value)
        if (result) setResult(null) // Clear previous result when text changes
    }

    const handleClear = () => {
        setText('')
        setResult(null)
    }

    const handleAnalyze = async () => {
        if (!text.trim() || text.trim().length < 5) return
        setLoading(true)
        try {
            const data = await nlpAPI.analyzeJournal(text)
            setResult(data)
        } catch (error) {
            console.error('Analysis failed:', error)
        } finally {
            setLoading(false)
        }
    }

    const getMoodIcon = (mood) => {
        if (mood?.includes('Positive')) return <Smile className="h-6 w-6 text-green-500" />
        if (mood?.includes('Negative')) return <Frown className="h-6 w-6 text-red-500" />
        return <Meh className="h-6 w-6 text-amber-500" />
    }

    const getMoodBg = (mood) => {
        if (mood?.includes('Positive')) return 'from-green-50 to-emerald-50 border-green-200 shadow-green-100'
        if (mood?.includes('Negative')) return 'from-red-50 to-rose-50 border-red-200 shadow-red-100'
        return 'from-amber-50 to-yellow-50 border-amber-200 shadow-amber-100'
    }

    return (
        <div className="space-y-6 max-w-4xl mx-auto">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                        <Brain className="h-7 w-7 text-primary-600" />
                        {t.journal.title}
                    </h1>
                    <p className="text-slate-500">{t.journal.desc}</p>
                </div>
                <div className="flex gap-2">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded">EN</span>
                    <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs font-bold rounded">HI</span>
                    <span className="px-2 py-1 bg-emerald-100 text-emerald-700 text-xs font-bold rounded">TE</span>
                </div>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden">
                <div className="bg-slate-50 px-6 py-3 border-b border-slate-100 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-slate-500 text-xs font-medium">
                        <Languages className="h-4 w-4" />
                        Auto-detecting Language
                    </div>
                    <div className="text-xs text-slate-400">{text.length}/2000</div>
                </div>
                <textarea
                    value={text}
                    onChange={handleTextChange}
                    autoComplete="off"
                    placeholder={t.journal.placeholder}
                    rows={6}
                    className="w-full px-6 py-4 text-base text-slate-700 resize-none focus:outline-none placeholder:text-slate-300 leading-relaxed"
                />
                <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3">
                    <button
                        onClick={handleClear}
                        className="px-6 py-2.5 bg-white border border-slate-200 text-slate-600 rounded-xl text-sm font-bold hover:bg-slate-50 transition-all"
                    >
                        {t.journal.clear}
                    </button>
                    <button
                        onClick={handleAnalyze}
                        disabled={loading || text.trim().length < 5}
                        className="flex items-center gap-2 px-6 py-2.5 bg-primary-600 text-white rounded-xl text-sm font-bold hover:bg-primary-700 transition-all hover:shadow-lg disabled:opacity-40 disabled:cursor-not-allowed transform hover:-translate-y-0.5 active:translate-y-0"
                    >
                        {loading ? (
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        ) : (
                            <Sparkles className="h-4 w-4" />
                        )}
                        {loading ? t.journal.processing : t.journal.analyze}
                    </button>
                </div>
            </div>

            {result && (
                <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
                    <div className={`bg-gradient-to-br ${getMoodBg(result.mood)} border border-l-8 rounded-2xl p-6 shadow-lg`}>
                        <div className="flex items-center gap-5">
                            <div className="w-16 h-16 bg-white/80 backdrop-blur rounded-2xl flex items-center justify-center shadow-inner">
                                {getMoodIcon(result.mood)}
                            </div>
                            <div className="flex-1">
                                <div className="flex items-center justify-between">
                                    <p className="text-xs font-black uppercase tracking-widest text-slate-500 mb-1">{t.journal.emotion}</p>
                                    <span className="text-[10px] bg-white/50 px-2 py-0.5 rounded-full font-bold text-slate-600 border border-white/50">
                                        {Math.round(result.confidence * 100)}% {t.journal.confidence}
                                    </span>
                                </div>
                                <h2 className="text-3xl font-black text-slate-800">{result.mood}</h2>
                                <p className="text-sm text-slate-600 mt-1 italic leading-relaxed">"{text.length > 100 ? text.substring(0, 100) + '...' : text}"</p>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="p-2 bg-primary-100 rounded-lg">
                                    <Brain className="h-5 w-5 text-primary-600" />
                                </div>
                                <h3 className="font-bold text-slate-800">{t.journal.insights}</h3>
                            </div>
                            <div className="space-y-4">
                                {result.advice.map((tip, idx) => (
                                    <div key={idx} className="flex items-start gap-4 p-4 bg-slate-50 rounded-xl border border-slate-100 group hover:border-primary-200 transition-colors">
                                        <div className="w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs font-black flex-shrink-0 group-hover:scale-110 transition-transform">
                                            {idx + 1}
                                        </div>
                                        <p className="text-sm text-slate-700 leading-relaxed font-medium">{tip}</p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="space-y-6 flex flex-col h-full">
                            <div className="bg-slate-800 rounded-2xl border border-slate-700 p-6 shadow-xl flex-1 flex flex-col">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="font-mono text-sm font-bold text-slate-200 flex items-center gap-2">
                                        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                                        RAW_AI_OUTPUT.txt
                                    </h3>
                                </div>
                                <div className="bg-slate-900 rounded-xl p-4 overflow-y-auto flex-1 custom-scrollbar border border-slate-700">
                                    <pre className="text-xs text-emerald-400 font-mono whitespace-pre-wrap leading-relaxed">
                                        {result.formatted_text || "Waiting for structured data..."}
                                    </pre>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
