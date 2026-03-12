import { useState } from 'react'
import { Send, FileText, Type, ArrowLeft } from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Alert } from '../components/ui/Alert'
import { CategorySelector } from '../components/translate/CategorySelector'
import { TypeSelector } from '../components/translate/TypeSelector'
import { FileUploader } from '../components/translate/FileUploader'
import { TextInput } from '../components/translate/TextInput'
import { ResultTabs } from '../components/translate/ResultTabs'
import { useTranslate } from '../hooks/useTranslate'
import { useUsage } from '../context/UsageContext'
import type { DocumentCategory, TranslationResult } from '../types/api'

type InputMethod = 'file' | 'text'

export function HomePage() {
  const [category, setCategory] = useState<DocumentCategory | null>(null)
  const [documentType, setDocumentType] = useState<string | null>(null)
  const [inputMethod, setInputMethod] = useState<InputMethod>('text')
  const [text, setText] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<TranslationResult | null>(null)

  const { canTranslate, usage } = useUsage()
  const {
    translateText,
    translateFile,
    isTranslating,
    error,
    anonymizedFields,
    reset,
  } = useTranslate({
    onSuccess: (data) => setResult(data),
  })

  const canSubmit =
    category &&
    documentType &&
    canTranslate &&
    (inputMethod === 'text' ? text.length >= 10 : file !== null)

  const handleSubmit = async () => {
    if (!category || !documentType) return

    try {
      if (inputMethod === 'text') {
        await translateText({ text, category, documentType })
      } else if (file) {
        await translateFile({ file, category, documentType })
      }
    } catch {
      // Error is handled by the mutation
    }
  }

  const handleReset = () => {
    setCategory(null)
    setDocumentType(null)
    setText('')
    setFile(null)
    setResult(null)
    reset()
  }

  // Resetar tipo quando categoria muda
  const handleCategoryChange = (newCategory: DocumentCategory) => {
    setCategory(newCategory)
    setDocumentType(null)
  }

  return (
    <div className="max-w-3xl mx-auto space-y-4 sm:space-y-6">
      {/* Limite atingido */}
      {!canTranslate && (
        <Alert variant="warning" title="Limite de traduções atingido">
          Você utilizou todas as suas {usage?.translations_limit} traduções gratuitas.
          Aguarde um momento para realizar novas traduções.
        </Alert>
      )}

      {/* Resultado */}
      {result ? (
        <div className="space-y-4">
          <div className="flex justify-start">
            <Button onClick={handleReset} variant="outline" leftIcon={<ArrowLeft size={18} />}>
              Voltar
            </Button>
          </div>
          <ResultTabs result={result} anonymizedFields={anonymizedFields} />
          <div className="flex justify-center">
            <Button onClick={handleReset} variant="primary" leftIcon={<ArrowLeft size={18} />}>
              Traduzir outro documento
            </Button>
          </div>
        </div>
      ) : (
        <>
          {/* Seleção de categoria */}
          <Card>
            <CategorySelector value={category} onChange={handleCategoryChange} />
          </Card>

          {/* Seleção de tipo específico */}
          {category && (
            <Card>
              <TypeSelector
                category={category}
                value={documentType}
                onChange={setDocumentType}
              />
            </Card>
          )}

          {/* Método de entrada */}
          {documentType && (
            <Card>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Como deseja enviar o documento?
                </label>
                <div className="flex gap-2 sm:gap-3">
                  <button
                    onClick={() => setInputMethod('text')}
                    className={`flex-1 flex items-center justify-center gap-1.5 sm:gap-2 p-2 sm:p-3 rounded-lg border-2 transition-colors text-sm sm:text-base ${
                      inputMethod === 'text'
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                        : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400'
                    }`}
                  >
                    <Type size={18} />
                    <span>Colar texto</span>
                  </button>
                  <button
                    onClick={() => setInputMethod('file')}
                    className={`flex-1 flex items-center justify-center gap-1.5 sm:gap-2 p-2 sm:p-3 rounded-lg border-2 transition-colors text-sm sm:text-base ${
                      inputMethod === 'file'
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                        : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400'
                    }`}
                  >
                    <FileText size={18} />
                    <span>Arquivo</span>
                  </button>
                </div>
              </div>

              {/* Input de texto ou arquivo */}
              {inputMethod === 'text' ? (
                <TextInput value={text} onChange={setText} />
              ) : (
                <FileUploader selectedFile={file} onFileSelect={setFile} />
              )}
            </Card>
          )}

          {/* Erro */}
          {error && (
            <Alert variant="error" title="Erro">
              {error.message}
            </Alert>
          )}

          {/* Botão de enviar */}
          {documentType && (
            <div className="flex justify-center">
              <Button
                onClick={handleSubmit}
                disabled={!canSubmit}
                isLoading={isTranslating}
                size="lg"
                leftIcon={<Send size={20} />}
              >
                {isTranslating ? 'Traduzindo...' : 'Traduzir Documento'}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
