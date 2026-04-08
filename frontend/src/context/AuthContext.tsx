import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import {
  getCurrentUser,
  getApiErrorMessage,
  login as loginRequest,
  logout as logoutRequest,
  register as registerRequest,
} from '../services/api'
import type { AuthUser, LoginRequest, RegisterRequest } from '../types/api'

interface AuthContextType {
  user: AuthUser | null
  isLoading: boolean
  error: string | null
  login: (payload: LoginRequest) => Promise<boolean>
  register: (payload: RegisterRequest) => Promise<boolean>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const bootstrap = async () => {
      // Nao verificamos mais o localStorage. 
      // Simplesmente tentamos chamar /me para ver se o cookie e valido.
      try {
        const response = await getCurrentUser()
        if (response.success && response.data?.user) {
          setUser(response.data.user)
        }
      } catch (err) {
        // Silencioso: usuario nao esta logado ou sessao expirou
        console.debug('Sessao nao encontrada ou expirada')
      } finally {
        setIsLoading(false)
      }
    }

    bootstrap()
  }, [])

  const login = async (payload: LoginRequest) => {
    setError(null)
    try {
      const response = await loginRequest(payload)
      if (!response.success || !response.data?.user) {
        setError(response.error || 'Nao foi possivel entrar')
        return false
      }

      // O token ja foi setado como cookie HttpOnly pelo backend
      setUser(response.data.user)
      return true
    } catch (error) {
      setError(getApiErrorMessage(error))
      return false
    }
  }

  const register = async (payload: RegisterRequest) => {
    setError(null)
    try {
      const response = await registerRequest(payload)
      if (!response.success || !response.data?.user) {
        setError(response.error || 'Nao foi possivel criar a conta')
        return false
      }

      // O token ja foi setado como cookie HttpOnly pelo backend
      setUser(response.data.user)
      return true
    } catch (error) {
      setError(getApiErrorMessage(error))
      return false
    }
  }

  const logout = async () => {
    try {
      await logoutRequest()
    } finally {
      // O backend ja limpou o cookie no logoutRequest()
      setUser(null)
    }
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, error, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
