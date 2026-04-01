import { useState } from 'react'
import { Send, FileText, Type, RotateCcw } from 'lucide-react'
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
import type {
  DocumentCategory,
  TranslationResult,
  ValidationResult,
} from '../types/api'
import { CATEGORY_LABELS } from '../types/api'

type InputMethod = 'file' | 'text'
type SubmissionStage = 'idle' | 'validating' | 'translating'

const DEFAULT_DOCUMENT_TYPE_BY_CATEGORY: Record<DocumentCategory, string> = {
  laudo: 'outros',
  receita: 'simples',
  saude_mental: 'outros',
}

const DETECTED_CATEGORY_LABELS: Record<DocumentCategory, string> = {
  laudo: 'Laudo Medico',
  receita: 'Receita Medica',
  saude_mental: 'Documento de Saude Mental',
}

export function HomePage() {
  const [category, setCategory] = useState<DocumentCategory | null>(null)
  const [documentType, setDocumentType] = useState<string | null>(null)
  const [inputMethod, setInputMethod] = useState<InputMethod>('text')
  const [text, setText] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<TranslationResult | null>(null)
  const [submissionStage, setSubmissionStage] = useState<SubmissionStage>('idle')
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null)
  const [submissionError, setSubmissionError] = useState<string | null>(null)

  const { canTranslate, usage } = useUsage()
  const {
    validateText,
    validateFile,
    translateText,
    translateFile,
    isValidating,
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

  const buildValidationSummary = (validation: ValidationResult) => {
    const parts = [`Documento validado: ${validation.message}`]

    if (validation.suggested_category && validation.suggested_category !== category) {
      parts.push(
        `Documento detectado como ${DETECTED_CATEGORY_LABELS[validation.suggested_category]}. Ajustando automaticamente.`
      )
    } else if (validation.suggested_category) {
      parts.push(`Documento detectado como ${CATEGORY_LABELS[validation.suggested_category]}.`)
    }

    if (
      validation.professional_authorship_detected &&
      validation.professional_authorship_evidence.length > 0
    ) {
      parts.push(
        `Indicios de emissao profissional: ${validation.professional_authorship_evidence.join(', ')}.`
      )
    }

    return parts.join(' ')
  }

  const getProcessingMessage = () => {
    if (inputMethod === 'file' && file?.type.startsWith('image/')) {
      return 'Processando imagem...'
    }

    if (inputMethod === 'file') {
      return 'Processando arquivo...'
    }

    return 'Traduzindo documento...'
  }

  const handleSubmit = async () => {
    if (!category || !documentType) return

    try {
      setSubmissionError(null)
      setValidationResult(null)
      setSubmissionStage('validating')

      if (inputMethod === 'text') {
        const validation = await validateText(text)
        if (!validation.is_valid) {
          throw new Error(`Documento nao aceito: ${validation.message}`)
        }

        const effectiveCategory = validation.suggested_category || category
        const effectiveDocumentType =
          validation.suggested_category && validation.suggested_category !== category
            ? DEFAULT_DOCUMENT_TYPE_BY_CATEGORY[validation.suggested_category]
            : documentType

        if (effectiveCategory !== category) {
          setCategory(effectiveCategory)
          setDocumentType(effectiveDocumentType)
        }

        setValidationResult(validation)
        setSubmissionStage('translating')
        await translateText({
          text,
          category: effectiveCategory,
          documentType: effectiveDocumentType,
        })
      } else if (file) {
        const validation = await validateFile(file)
        if (!validation.is_valid) {
          throw new Error(`Documento nao aceito: ${validation.message}`)
        }

        const effectiveCategory = validation.suggested_category || category
        const effectiveDocumentType =
          validation.suggested_category && validation.suggested_category !== category
            ? DEFAULT_DOCUMENT_TYPE_BY_CATEGORY[validation.suggested_category]
            : documentType

        if (effectiveCategory !== category) {
          setCategory(effectiveCategory)
          setDocumentType(effectiveDocumentType)
        }

        setValidationResult(validation)
        setSubmissionStage('translating')
        await translateFile({
          file,
          category: effectiveCategory,
          documentType: effectiveDocumentType,
        })
      }
    } catch (err) {
      if (err instanceof Error) {
        setSubmissionError(err.message)
      }
    } finally {
      setSubmissionStage('idle')
    }
  }

  const handleReset = () => {
    setCategory(null)
    setDocumentType(null)
    setText('')
    setFile(null)
    setResult(null)
    setValidationResult(null)
    setSubmissionError(null)
    setSubmissionStage('idle')
    reset()
  }

  const handleCategoryChange = (newCategory: DocumentCategory) => {
    setCategory(newCategory)
    setDocumentType(null)
    setResult(null)
    setValidationResult(null)
    setSubmissionError(null)
    setSubmissionStage('idle')
  }

  return (
    <div className="max-w-3xl mx-auto space-y-4 sm:space-y-6">
      {!canTranslate && (
        <Alert variant="warning" title="Limite de traducoes atingido">
          Voce utilizou todas as suas {usage?.translations_limit} traducoes gratuitas.
          Aguarde um momento para realizar novas traducoes.
        </Alert>
      )}

      <Card>
        <CategorySelector value={category} onChange={handleCategoryChange} />
      </Card>

      {category && (
        <Card>
          <TypeSelector
            category={category}
            value={documentType}
            onChange={setDocumentType}
          />
        </Card>
      )}

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

          {inputMethod === 'text' ? (
            <TextInput value={text} onChange={setText} />
          ) : (
            <FileUploader selectedFile={file} onFileSelect={setFile} />
          )}
        </Card>
      )}

      {(submissionError || error) && (
        <Alert variant="error" title="Erro">
          {submissionError || error?.message}
        </Alert>
      )}

      {submissionStage === 'validating' && (
        <Alert variant="info" title="Validando documento">
          Analisando se o conteudo pertence ao dominio clinico...
        </Alert>
      )}

      {validationResult && (
        <Alert variant="success" title="Documento validado">
          {buildValidationSummary(validationResult)}
        </Alert>
      )}

      {submissionStage === 'translating' && (
        <Alert variant="info" title="Traducao em andamento">
          {getProcessingMessage()}
        </Alert>
      )}

      {documentType && (
        <div className="flex flex-col sm:flex-row justify-center gap-3">
          <Button
            onClick={handleSubmit}
            disabled={!canSubmit}
            isLoading={isValidating || isTranslating}
            size="lg"
            leftIcon={<Send size={20} />}
          >
            {submissionStage === 'validating'
              ? 'Validando...'
              : submissionStage === 'translating'
                ? 'Traduzindo...'
                : result
                  ? 'Traduzir novamente'
                  : 'Traduzir Documento'}
          </Button>

          {(result || text || file || category || documentType) && (
            <Button
              onClick={handleReset}
              variant="outline"
              size="lg"
              leftIcon={<RotateCcw size={18} />}
            >
              Limpar tudo
            </Button>
          )}
        </div>
      )}

      {result && (
        <ResultTabs result={result} anonymizedFields={anonymizedFields} />
      )}
    </div>
  )
}
