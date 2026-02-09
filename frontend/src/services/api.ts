import axios from 'axios'
import type {
  TranslateTextRequest,
  TranslateResponse,
  ValidateResponse,
  UsageResponse,
  SupportQuote,
  BreathingExercise,
  SupportResource,
  SupportResponse,
} from '../types/api'

const API_BASE_URL = '/api/v1'

// Criar instância do axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para adicionar session ID
api.interceptors.request.use((config) => {
  const sessionId = localStorage.getItem('session_id')
  if (sessionId) {
    config.headers['X-Session-ID'] = sessionId
  }
  return config
})

// Interceptor para salvar session ID
api.interceptors.response.use((response) => {
  const sessionId = response.data?.data?.session_id
  if (sessionId) {
    localStorage.setItem('session_id', sessionId)
  }
  return response
})

// Health check
export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await api.get('/health')
  return response.data
}

// Tradução
export const translateText = async (
  request: TranslateTextRequest
): Promise<TranslateResponse> => {
  const response = await api.post('/translate/text', request)
  return response.data
}

export const translateFile = async (
  file: File,
  category: string,
  documentType: string
): Promise<TranslateResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('category', category)
  formData.append('document_type', documentType)

  const response = await api.post('/translate/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Validação
export const validateText = async (text: string): Promise<ValidateResponse> => {
  const response = await api.post('/validate/text', { text })
  return response.data
}

export const validateFile = async (file: File): Promise<ValidateResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/validate/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Uso
export const getUsageStatus = async (): Promise<UsageResponse> => {
  const response = await api.get('/usage/status')
  return response.data
}

export const incrementUsage = async (): Promise<UsageResponse> => {
  const response = await api.post('/usage/increment')
  return response.data
}

// Apoio emocional
export const getRandomQuote = async (): Promise<SupportQuote> => {
  const response = await api.get('/support/quote')
  return response.data
}

export const getExercises = async (): Promise<BreathingExercise[]> => {
  const response = await api.get('/support/exercises')
  return response.data
}

export const getResources = async (): Promise<SupportResource[]> => {
  const response = await api.get('/support/resources')
  return response.data
}

export const getAllSupport = async (): Promise<SupportResponse> => {
  const response = await api.get('/support/all')
  return response.data
}

export default api
