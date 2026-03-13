import { useState, useEffect, useRef } from 'react'
import { MessageCircle, X, Send, Trash2, Maximize2, Minimize2, Loader2, Bot } from 'lucide-react'
import { chatAPI } from '../services/api'
import { useAuth } from '../App'
import { useLanguage } from '../context/LanguageContext'

export default function Chatbot() {
    const [isOpen, setIsOpen] = useState(false)
    const [isExpanded, setIsExpanded] = useState(false)
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)

    const { user } = useAuth()
    const { language } = useLanguage()
    const messagesEndRef = useRef(null)

    useEffect(() => {
        if (user && isOpen) {
            loadHistory()
        }
    }, [user, isOpen])

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    const loadHistory = async () => {
        if (!user) return
        try {
            const data = await chatAPI.getHistory(user.id)
            if (data && data.history) {
                setMessages(data.history)
            }
        } catch (error) {
            console.error('Failed to load chat history', error)
        }
    }

    const handleClearHistory = async () => {
        if (!user) return
        try {
            await chatAPI.clearHistory(user.id)
            setMessages([])
        } catch (error) {
            console.error('Failed to clear chat history', error)
        }
    }

    const handleSend = async (e) => {
        e.preventDefault()
        if (!input.trim() || !user || loading) return

        const userMessage = input.trim()
        setInput('')
        setMessages(prev => [...prev, { sender: 'user', text: userMessage }])

        setLoading(true)
        try {
            const resp = await chatAPI.sendMessage(user.id, userMessage, language)
            setMessages(prev => [...prev, { sender: 'bot', text: resp.reply }])
        } catch (error) {
            console.error('Chat error', error)
            setMessages(prev => [...prev, { sender: 'bot', text: 'Sorry, I am having trouble connecting.' }])
        } finally {
            setLoading(false)
        }
    }

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                className="fixed bottom-6 right-6 p-4 bg-primary-600 text-white rounded-full shadow-2xl hover:bg-primary-700 hover:scale-110 transition-all z-50 flex items-center justify-center"
            >
                <MessageCircle className="h-8 w-8" />
            </button>
        )
    }

    return (
        <div
            className={`fixed ${isExpanded ? 'inset-4 md:inset-10' : 'bottom-6 right-6 w-[360px] h-[550px]'} bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col z-50 transition-all duration-300 overflow-hidden`}
        >
            {/* Header */}
            <div className="bg-primary-600 p-4 text-white flex items-center justify-between shadow-md z-10">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                        <Bot className="h-6 w-6 text-white" />
                    </div>
                    <div>
                        <h3 className="font-bold text-lg leading-tight">Wellness Guide</h3>
                        <p className="text-xs text-primary-100 opacity-90">AI Powered Assistant</p>
                    </div>
                </div>
                <div className="flex items-center gap-1">
                    <button onClick={handleClearHistory} title="Clear Chat" className="p-2 hover:bg-white/20 rounded-full transition-colors">
                        <Trash2 className="h-4 w-4" />
                    </button>
                    <button onClick={() => setIsExpanded(!isExpanded)} title={isExpanded ? 'Minimize' : 'Expand'} className="p-2 hover:bg-white/20 rounded-full transition-colors hidden md:block">
                        {isExpanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                    </button>
                    <button onClick={() => setIsOpen(false)} title="Close" className="p-2 hover:bg-red-500 rounded-full transition-colors">
                        <X className="h-5 w-5" />
                    </button>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 custom-scrollbar">
                {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-center opacity-50 space-y-4">
                        <Bot className="h-16 w-16 text-slate-300" />
                        <p className="text-sm font-medium text-slate-500">
                            Hello! I'm your Wellness Assistant. Ask me anything about health, your stats, or general wellbeing!
                        </p>
                    </div>
                )}

                {messages.map((msg, index) => (
                    <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div
                            className={`max-w-[85%] rounded-2xl px-5 py-3 ${msg.sender === 'user'
                                    ? 'bg-primary-600 text-white rounded-tr-sm shadow-md'
                                    : 'bg-white border border-slate-200 text-slate-700 rounded-tl-sm shadow-sm'
                                }`}
                        >
                            <div className="text-sm whitespace-pre-wrap leading-relaxed prose prose-sm prose-slate mx-auto">
                                {msg.text}
                            </div>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm flex items-center gap-2">
                            <Loader2 className="h-4 w-4 animate-spin text-primary-500" />
                            <span className="text-xs font-medium text-slate-500">Thinking...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-3 bg-white border-t border-slate-100">
                <form onSubmit={handleSend} className="relative flex items-end">
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault()
                                handleSend(e)
                            }
                        }}
                        placeholder="Ask about wellness..."
                        className="w-full bg-slate-50 border border-slate-200 text-slate-700 text-sm rounded-xl pl-4 pr-12 py-3 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 resize-none custom-scrollbar"
                        rows="1"
                        style={{ minHeight: '44px', maxHeight: '120px' }}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || loading}
                        className="absolute right-2 bottom-1.5 p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:hover:bg-primary-600 transition-colors"
                    >
                        <Send className="h-4 w-4 ml-0.5" />
                    </button>
                </form>
            </div>
        </div>
    )
}
