import { useEffect, useState } from 'react'
import { getHistoryImage } from '../../services/api'
import { Loader2, AlertCircle } from 'lucide-react'

interface SecureHistoryImageProps {
  recordId: string
  alt?: string
  className?: string
  fallbackBase64?: string | null
  mediaType?: string | null
}

export function SecureHistoryImage({ 
  recordId, 
  alt = 'Documento original', 
  className,
  fallbackBase64,
  mediaType
}: SecureHistoryImageProps) {
  const [imageUrl, setImageUrl] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Se começar com encrypted://, buscamos via API segura
    if (fallbackBase64 && fallbackBase64.startsWith('encrypted://')) {
      const fetchImage = async () => {
        try {
          setIsLoading(true)
          const blob = await getHistoryImage(recordId)
          const url = URL.createObjectURL(blob)
          setImageUrl(url)
          setError(null)
        } catch (err) {
          console.error('Erro ao carregar imagem segura:', err)
          setError('Nao foi possivel carregar a imagem original com seguranca.')
        } finally {
          setIsLoading(false)
        }
      }

      fetchImage()
      
      return () => {
        if (imageUrl) URL.revokeObjectURL(imageUrl)
      }
    } else if (fallbackBase64) {
      // Legado: Base64 direto
      const src = `data:${mediaType || 'image/jpeg'};base64,${fallbackBase64}`
      setImageUrl(src)
      setIsLoading(false)
    } else {
      setIsLoading(false)
    }
  }, [recordId, fallbackBase64, mediaType])

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-dashed border-gray-300 dark:border-gray-700 ${className}`}>
        <div className="flex flex-col items-center gap-2 text-gray-400">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span className="text-xs">Descriptografando imagem...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-200 dark:border-red-900/30 p-4 ${className}`}>
        <div className="flex items-center gap-2 text-red-600 dark:text-red-400 text-sm text-center">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      </div>
    )
  }

  if (!imageUrl) return null

  return (
    <img
      src={imageUrl}
      alt={alt}
      className={className}
    />
  )
}
