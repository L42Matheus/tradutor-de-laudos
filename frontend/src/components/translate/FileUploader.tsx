import { useCallback, useState, useEffect } from 'react'
import { Upload, File, X, Image, FileText } from 'lucide-react'
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
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isPreviewOpen, setIsPreviewOpen] = useState(false)

  // Gerar preview quando arquivo for selecionado
  useEffect(() => {
    if (
      selectedFile &&
      (selectedFile.type.startsWith('image/') ||
        selectedFile.type === 'application/pdf')
    ) {
      const url = URL.createObjectURL(selectedFile)
      setPreviewUrl(url)
      return () => URL.revokeObjectURL(url)
    }
    setPreviewUrl(null)
  }, [selectedFile])

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
    setPreviewUrl(null)
    setError(null)
    setIsPreviewOpen(false)
  }

  const isImage = selectedFile?.type.startsWith('image/')
  const isPdf = selectedFile?.type === 'application/pdf'

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Enviar arquivo
      </label>

      {selectedFile ? (
        <div className="relative bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          {/* Preview da imagem */}
          {isImage && previewUrl && (
            <div className="relative w-full bg-gray-100 dark:bg-gray-900 flex items-center justify-center p-2 sm:p-4">
              <img
                src={previewUrl}
                alt="Preview do documento"
                className="max-h-[70vh] w-full object-contain rounded shadow-sm"
              />
              <button
                onClick={() => setIsPreviewOpen(true)}
                className="absolute top-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded"
              >
                Ampliar
              </button>
            </div>
          )}

          {/* Preview do PDF */}
          {isPdf && (
            <div className="relative w-full bg-gray-100 dark:bg-gray-900 p-2 sm:p-4">
              {previewUrl ? (
                <iframe
                  src={previewUrl}
                  title="Preview do PDF"
                  className="w-full h-[70vh] rounded border border-gray-200 dark:border-gray-700"
                />
              ) : (
                <div className="flex items-center justify-center p-8">
                  <div className="text-center">
                    <FileText className="mx-auto text-red-500" size={48} />
                    <p className="text-sm text-gray-500 mt-2">Documento PDF</p>
                  </div>
                </div>
              )}
              <button
                onClick={() => setIsPreviewOpen(true)}
                className="absolute top-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded"
              >
                Ampliar
              </button>
            </div>
          )}

          {/* Informações do arquivo */}
          <div className="p-4 flex items-center gap-3">
            {isImage ? (
              <Image className="text-green-500 flex-shrink-0" size={20} />
            ) : isPdf ? (
              <FileText className="text-red-500 flex-shrink-0" size={20} />
            ) : (
              <File className="text-primary-500 flex-shrink-0" size={20} />
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
              className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
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
            'relative border-2 border-dashed rounded-lg p-4 sm:p-8 text-center transition-colors cursor-pointer',
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
          <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
            Arraste ou clique para selecionar
          </p>
          <p className="text-[10px] sm:text-xs text-gray-500 mt-1">
            PDF, TXT, imagens - Máx. {MAX_SIZE_MB}MB
          </p>
        </div>
      )}

      {/* Preview em tela cheia */}
      {isPreviewOpen && previewUrl && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
          <div className="relative w-full max-w-6xl max-h-[90vh]">
            <button
              onClick={() => setIsPreviewOpen(false)}
              className="absolute -top-10 right-0 text-white text-sm px-3 py-1 bg-black/60 rounded"
            >
              Fechar
            </button>
            {isImage ? (
              <img
                src={previewUrl}
                alt="Preview do documento"
                className="w-full max-h-[90vh] object-contain rounded"
              />
            ) : isPdf ? (
              <iframe
                src={previewUrl}
                title="Preview do PDF"
                className="w-full h-[90vh] rounded border border-gray-700"
              />
            ) : null}
          </div>
        </div>
      )}

      {error && (
        <p className="mt-2 text-sm text-red-500">{error}</p>
      )}
    </div>
  )
}
