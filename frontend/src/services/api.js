import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  if (user.id) {
    config.params = { ...config.params, user_id: user.id }
  }
  return config
})

export const authAPI = {
  googleLogin: async (code) => {
    const response = await api.post('/auth/google', { code })
    return response.data
  },
  getGoogleAuthUrl: async () => {
    const response = await api.get('/auth/google/url')
    return response.data
  },
  demoLogin: async () => {
    const response = await api.post('/auth/demo')
    return response.data
  },
  getCurrentUser: async (userId) => {
    const response = await api.get('/auth/me', { params: { user_id: userId } })
    return response.data
  },
}

export const healthAPI = {
  getTodayHealth: async (userId) => {
    const response = await api.get('/health/today', { params: { user_id: userId } })
    return response.data
  },
  getWeekHealth: async (userId) => {
    const response = await api.get('/health/week', { params: { user_id: userId } })
    return response.data
  },
  getMonthHealth: async (userId) => {
    const response = await api.get('/health/month', { params: { user_id: userId } })
    return response.data
  },
  addManualHealth: async (userId, data) => {
    const response = await api.post('/health/manual', data, { params: { user_id: userId } })
    return response.data
  },
  syncGoogleFit: async (userId) => {
    const response = await api.post('/health/sync', {}, { params: { user_id: userId } })
    return response.data
  },
  getRecords: async (userId, params = {}) => {
    const response = await api.get('/health/records', { params: { ...params, user_id: userId } })
    return response.data
  },
}

export const scoreAPI = {
  getTodayScore: async (userId) => {
    const response = await api.get('/score/today', { params: { user_id: userId } })
    return response.data
  },
  getScoreHistory: async (userId, days = 30) => {
    const response = await api.get('/score/history', { params: { user_id: userId, days } })
    return response.data
  },
  calculateScore: async (userId) => {
    const response = await api.post('/score/calculate', null, { params: { user_id: userId } })
    return response.data
  },
}

export const insightAPI = {
  getDailyInsight: async (userId, lang = 'en') => {
    const response = await api.get('/insights/daily', { params: { user_id: userId, lang } })
    return response.data
  },
  getWeeklyInsight: async (userId) => {
    const response = await api.get('/insights/weekly', { params: { user_id: userId } })
    return response.data
  },
  getPatterns: async (userId, limit = 10) => {
    const response = await api.get('/insights/patterns', { params: { user_id: userId, limit } })
    return response.data
  },
  getAlerts: async (userId, lang = 'en') => {
    const response = await api.get('/insights/alerts', { params: { user_id: userId, lang } })
    return response.data
  },
}

export const analyticsAPI = {
  getCorrelation: async () => {
    const response = await api.get('/analytics/correlation')
    return response.data
  },
  getDataset: async () => {
    const response = await api.get('/analytics/dataset')
    return response.data
  }
}

export const nlpAPI = {
  analyzeJournal: async (text) => {
    const response = await api.post('/nlp/analyze', { text })
    return response.data
  }
}

export const chatAPI = {
  sendMessage: async (userId, message, language = 'en') => {
    const response = await api.post('/chatbot/chat', { user_id: userId, message, language })
    return response.data
  },
  getHistory: async (userId) => {
    const response = await api.get(`/chatbot/history/${userId}`)
    return response.data
  },
  clearHistory: async (userId) => {
    const response = await api.delete(`/chatbot/history/${userId}`)
    return response.data
  }
}

export default api
