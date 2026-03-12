import { createContext, useContext, useState, ReactNode } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getUsageStatus, incrementUsage } from '../services/api'
import type { UsageStatus } from '../types/api'

interface UsageContextType {
  usage: UsageStatus | null
  isLoading: boolean
  error: string | null
  canTranslate: boolean
  incrementTranslation: () => Promise<void>
  refreshUsage: () => void
}

const UsageContext = createContext<UsageContextType | undefined>(undefined)

interface UsageProviderProps {
  children: ReactNode
}

export function UsageProvider({ children }: UsageProviderProps) {
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)

  const { data: usageResponse, isLoading, refetch } = useQuery({
    queryKey: ['usage'],
    queryFn: getUsageStatus,
    staleTime: 1000 * 60, // 1 minuto
  })

  const incrementMutation = useMutation({
    mutationFn: incrementUsage,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usage'] })
    },
    onError: (err: Error) => {
      setError(err.message)
    },
  })

  const usage = usageResponse?.data ?? null
  const canTranslate = !usage?.is_limit_reached

  const incrementTranslation = async () => {
    await incrementMutation.mutateAsync()
  }

  const refreshUsage = () => {
    refetch()
  }

  return (
    <UsageContext.Provider
      value={{
        usage,
        isLoading,
        error,
        canTranslate,
        incrementTranslation,
        refreshUsage,
      }}
    >
      {children}
    </UsageContext.Provider>
  )
}

export function useUsage() {
  const context = useContext(UsageContext)
  if (context === undefined) {
    throw new Error('useUsage must be used within a UsageProvider')
  }
  return context
}
