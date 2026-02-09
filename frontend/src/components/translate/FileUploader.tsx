import { useCallback, useState } from 'react'
import { Upload, File, X, Image } from 'lucide-react'
import { clsx } from 'clsx'

interface FileUploaderProps {
  onFileSelect: (file: File | null) => void
  selectedFile: File | null
}

const ALLOWED_TYPES = [
  'application/pdf',
  'text/plain',
  'image/png',
  'image/jpeg',
  'image/gif',
  'image/webp',
]

const MAX_SIZE_MB = 10

export function FileUploader({ onFileSelect, selectedFile }: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const validateFile = (file: File): boolean => {
    setError(null)

    if (!ALLOWED_TYPES.includes(file.type)) {
      setError('Tipo de arquivo não suportado. Use PDF, TXT ou imagens.')
      return false
    }

    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`Arquivo muito grande. Máximo: ${MAX_SIZE_MB}MB`)
      return false
    }

    return true
  }

  const handleFile = (file: File) => {
    if (validateFile(file)) {
      onFileSelect(file)
    }
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const file = e.dataTransfer.files[0]
    if (file) {
      handleFile(file)
    }
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFile(file)
    }
  }

  const clearFile = () => {
    onFileSelect(null)
    setError(null)
  }

  const isImage = selectedFile?.type.startsWith('image/')

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Enviar arquivo
      </label>

      {selectedFile ? (
        <div className="relative p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            {isImage ? (
              <Image className="text-green-500" size={24} />
            ) : (
              <File className="text-primary-500" size={24} />
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {selectedFile.name}
              </p>
              <p className="text-xs text-gray-500">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <button
              onClick={clearFile}
              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full"
              aria-label="Remover arquivo"
            >
              <X size={18} />
            </button>
          </div>
        </div>
      ) : (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={clsx(
            'relative border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer',
            isDragging
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
              : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
          )}
        >
          <input
            type="file"
            onChange={handleInputChange}
            accept=".pdf,.txt,.png,.jpg,.jpeg,.gif,.webp"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <Upload
            className={clsx(
              'mx-auto mb-3',
              isDragging ? 'text-primary-500' : 'text-gray-400'
            )}
            size={32}
          />
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Arraste um arquivo ou clique para selecionar
          </p>
          <p className="text-xs text-gray-500 mt-1">
            PDF, TXT ou imagens (PNG, JPG) - Máx. {MAX_SIZE_MB}MB
          </p>
        </div>
      )}

      {error && (
        <p className="mt-2 text-sm text-red-500">{error}</p>
      )}
    </div>
  )
}
