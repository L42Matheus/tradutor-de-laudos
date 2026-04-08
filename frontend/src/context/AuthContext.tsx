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
      const token = localStorage.getItem('auth_token')
      if (!token) {
        setIsLoading(false)
        return
      }

      try {
        const response = await getCurrentUser()
        if (response.success && response.data?.user) {
          setUser(response.data.user)
        } else {
          localStorage.removeItem('auth_token')
        }
      } catch {
        localStorage.removeItem('auth_token')
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
      if (!response.success || !response.data?.token || !response.data.user) {
        setError(response.error || 'Nao foi possivel entrar')
        return false
      }

      localStorage.setItem('auth_token', response.data.token)
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
      if (!response.success || !response.data?.token || !response.data.user) {
        setError(response.error || 'Nao foi possivel criar a conta')
        return false
      }

      localStorage.setItem('auth_token', response.data.token)
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
      localStorage.removeItem('auth_token')
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
