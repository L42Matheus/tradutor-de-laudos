import axios from 'axios'
import type {
  AuthResponse,
  LoginRequest,
  FileDuplicateCheckResponse,
  RegisterRequest,
  TranslateTextRequest,
  TranslateResponse,
  TranslationHistoryResponse,
  ValidateResponse,
  UsageResponse,
  SupportQuote,
  BreathingExercise,
  SupportResource,
  SupportResponse,
  EpidemiologyProcessingResult,
  LLMProvider,
} from '../types/api'

const API_BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1'

// Criar instância do axios
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Importante para enviar cookies HttpOnly
  headers: {
    'Content-Type': 'application/json',
  },
})

export function getApiErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return 'Erro inesperado ao processar a solicitacao'
  }

  const responseData = error.response?.data

  if (typeof responseData?.error === 'string' && responseData.error.trim()) {
    return responseData.error
  }

  if (typeof responseData?.detail === 'string' && responseData.detail.trim()) {
    return responseData.detail
  }

  if (Array.isArray(responseData?.detail) && responseData.detail.length > 0) {
    return responseData.detail
      .map((item: { msg?: string }) => item?.msg)
      .filter(Boolean)
      .join(', ')
  }

  if (error.message?.trim()) {
    return error.message
  }

  return 'Nao foi possivel concluir a requisicao'
}

// Interceptor para adicionar session ID
api.interceptors.request.use((config) => {
  const sessionId = localStorage.getItem('session_id')
  if (sessionId) {
    config.headers['X-Session-ID'] = sessionId
  }
  
  // Nao precisamos mais injetar o Bearer Token manualmente
  // O navegador enviara o cookie auth_token automaticamente via withCredentials
  
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

// Auth
export const register = async (payload: RegisterRequest): Promise<AuthResponse> => {
  const response = await api.post('/auth/register', payload)
  return response.data
}

export const login = async (payload: LoginRequest): Promise<AuthResponse> => {
  const response = await api.post('/auth/login', payload)
  return response.data
}

export const getCurrentUser = async (): Promise<AuthResponse> => {
  const response = await api.get('/auth/me')
  return response.data
}

export const logout = async (): Promise<AuthResponse> => {
  const response = await api.post('/auth/logout')
  return response.data
}

export const getMyTranslationHistory = async (limit = 20): Promise<TranslationHistoryResponse> => {
  const response = await api.get('/history/mine', {
    params: { limit },
  })
  return response.data
}

export const getHistoryImage = async (recordId: string): Promise<Blob> => {
  const response = await api.get(`/history/image/${recordId}`, {
    responseType: 'blob',
  })
  return response.data
}

export const checkFileDuplicate = async (file: File): Promise<FileDuplicateCheckResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/history/check-file-duplicate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
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
  documentType: string,
  provider?: LLMProvider
): Promise<TranslateResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('category', category)
  formData.append('document_type', documentType)
  if (provider) {
    formData.append('provider', provider)
  }

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

// Localização
export interface Estado {
  sigla: string
  nome: string
}

export interface Municipio {
  id: string
  nome: string
}

export interface EstadosResponse {
  success: boolean
  data: Estado[]
}

export interface MunicipiosResponse {
  success: boolean
  data: Municipio[]
  estado: string
}

export const listarEstados = async (): Promise<EstadosResponse> => {
  const response = await api.get('/localizacao/estados')
  return response.data
}

export const listarMunicipios = async (estado: string): Promise<MunicipiosResponse> => {
  const response = await api.get(`/localizacao/municipios?estado=${estado}`)
  return response.data
}

export const processarDocumento = async (
  arquivo?: File,
  texto?: string,
  municipioConfirmado?: string,
  estadoConfirmado?: string,
  provider?: LLMProvider
): Promise<EpidemiologyProcessingResult> => {
  const formData = new FormData()

  if (arquivo) {
    formData.append('arquivo', arquivo)
  }
  if (texto) {
    formData.append('texto', texto)
  }
  if (municipioConfirmado) {
    formData.append('municipio_confirmado', municipioConfirmado)
  }
  if (estadoConfirmado) {
    formData.append('estado_confirmado', estadoConfirmado)
  }
  if (provider) {
    formData.append('provider', provider)
  }

  const response = await api.post('/epidemio/processar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const confirmarLocalizacao = async (
  traducaoId: string,
  municipio: string,
  estado: string,
  municipioIbgeId?: string
): Promise<EpidemiologyProcessingResult> => {
  const response = await api.post('/epidemio/confirmar-localizacao', {
    traducao_id: traducaoId,
    municipio,
    estado,
    municipio_ibge_id: municipioIbgeId,
  })
  return response.data
}

// Revisao por especialista
export interface SolicitarRevisaoResponse {
  success: boolean
  message: string
}

export const solicitarRevisao = async (traducaoId: string): Promise<SolicitarRevisaoResponse> => {
  const response = await api.post('/revisao/solicitar', {
    traducao_id: traducaoId,
  })
  return response.data
}

export default api
