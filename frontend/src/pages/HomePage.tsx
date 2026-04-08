import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { Send, FileText, Type, RotateCcw, UserCheck } from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Alert } from '../components/ui/Alert'
import { CategorySelector } from '../components/translate/CategorySelector'
import { TypeSelector } from '../components/translate/TypeSelector'
import { FileUploader } from '../components/translate/FileUploader'
import { TextInput } from '../components/translate/TextInput'
import { ConfirmacaoLocalizacao } from '../components/translate/ConfirmacaoLocalizacao'
import { ResultTabs } from '../components/translate/ResultTabs'
import { ProviderSelector } from '../components/translate/ProviderSelector'
import { useUsage } from '../context/UsageContext'
import { useAuth } from '../context/AuthContext'
import {
  checkFileDuplicate,
  confirmarLocalizacao,
  processarDocumento,
  solicitarRevisao,
  validateFile,
  validateText,
} from '../services/api'
import type {
  DocumentCategory,
  EpidemiologyProcessingResult,
  TranslationResult,
  ValidationResult,
  LLMProvider,
} from '../types/api'
import { CATEGORY_LABELS } from '../types/api'
import { formatBrazilDateTime } from '../utils/datetime'

type InputMethod = 'file' | 'text'
type SubmissionStage = 'idle' | 'validating' | 'translating' | 'confirming-location'

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

interface HomePageProps {
  embedded?: boolean
  onOpenHistoryDocument?: (historyId: string) => void
}

export function HomePage({ embedded = false, onOpenHistoryDocument }: HomePageProps) {
  const queryClient = useQueryClient()
  const { user } = useAuth()
  
  const [category, setCategory] = useState<DocumentCategory | null>(null)
  const [documentType, setDocumentType] = useState<string | null>(null)
  const [inputMethod, setInputMethod] = useState<InputMethod>('text')
  const [text, setText] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [llmProvider, setLlmProvider] = useState<LLMProvider>('claude')
  const [result, setResult] = useState<TranslationResult | null>(null)
  const [submissionStage, setSubmissionStage] = useState<SubmissionStage>('idle')
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null)
  const [submissionError, setSubmissionError] = useState<string | null>(null)
  const [pendingTranslationId, setPendingTranslationId] = useState<string | null>(null)
  const [requiresLocationConfirmation, setRequiresLocationConfirmation] = useState(false)
  const [revisaoSolicitada, setRevisaoSolicitada] = useState(false)
  const [solicitandoRevisao, setSolicitandoRevisao] = useState(false)
  const [duplicateHistoryInfo, setDuplicateHistoryInfo] = useState<{
    id: string
    translatedSummary: string
    createdAt?: string | null
  } | null>(null)

  const { canTranslate, usage, incrementTranslation } = useUsage()

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

  const mapProcessingResultToTranslationResult = (
    processingResult: EpidemiologyProcessingResult,
    processingCategory: DocumentCategory,
    fallbackGlossario: Record<string, string> = {}
  ): TranslationResult => {
    const resumo =
      processingResult.resumo ||
      processingResult.texto_traduzido ||
      'Nao foi possivel gerar a traducao do documento.'
    const detalhadoBase =
      processingResult.detalhado ||
      processingResult.texto_traduzido ||
      'Nao foi possivel gerar a traducao do documento.'
    const detalhado = detalhadoBase
    const entendaFacil = processingResult.entenda_facil || resumo
    const glossarioRecebido = processingResult.glossario ?? {}
    const glossario =
      Object.keys(glossarioRecebido).length > 0 ? glossarioRecebido : fallbackGlossario
    const alertas: string[] = [...(processingResult.alertas ?? [])]

    if (processingResult.documento_repetido) {
      const detalhesReuso = []
      if (processingResult.total_acessos && processingResult.total_acessos > 1) {
        detalhesReuso.push(`total de acessos: ${processingResult.total_acessos}`)
      }
      if (processingResult.ultimo_acesso_em) {
        detalhesReuso.push(
          `ultimo acesso em ${formatBrazilDateTime(processingResult.ultimo_acesso_em)}`
        )
      }

      alertas.push(
        detalhesReuso.length > 0
          ? `Este documento ja foi traduzido antes. Exibindo resultado em cache (${detalhesReuso.join(', ')}).`
          : 'Este documento ja foi traduzido antes. Exibindo resultado em cache.'
      )
    }

    if (processingResult.requer_confirmacao_localizacao) {
      alertas.push(
        'Nao foi possivel identificar a localizacao automaticamente. Confirme abaixo para incluir no dashboard epidemiologico.'
      )
    }

    return {
      resumo,
      detalhado,
      entenda_facil: entendaFacil,
      glossario,
      alertas,
      is_saude_mental: processingCategory === 'saude_mental',
      from_cache: processingResult.from_cache,
      professional_authorship_detected: false,
      professional_authorship_evidence: [],
    }
  }

  const handleProcessingSuccess = async (
    processingResult: EpidemiologyProcessingResult,
    processingCategory: DocumentCategory
  ) => {
    setResult(mapProcessingResultToTranslationResult(processingResult, processingCategory))
    setPendingTranslationId(processingResult.id || null)
    setRequiresLocationConfirmation(processingResult.requer_confirmacao_localizacao)

    if (!processingResult.from_cache) {
      await incrementTranslation()
    }

    await queryClient.invalidateQueries({ queryKey: ['translation-history'] })
  }

  const handleSubmit = async () => {
    if (!category || !documentType) return

    try {
      setSubmissionError(null)
      setValidationResult(null)
      setRequiresLocationConfirmation(false)
      setPendingTranslationId(null)
      setDuplicateHistoryInfo(null)
      setSubmissionStage('validating')

      if (inputMethod === 'text') {
        const validationResponse = await validateText(text)
        if (!validationResponse.success || !validationResponse.data) {
          throw new Error(validationResponse.error || 'Erro ao validar documento')
        }

        const validation = validationResponse.data
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
        const processingResult = await processarDocumento(undefined, text, undefined, undefined, llmProvider)
        if (!processingResult.success) {
          throw new Error(processingResult.error || 'Erro ao processar documento')
        }

        await handleProcessingSuccess(processingResult, effectiveCategory)
      } else if (file) {
        const duplicateResponse = await checkFileDuplicate(file)
        if (!duplicateResponse.success) {
          throw new Error(duplicateResponse.error || 'Erro ao verificar documento repetido')
        }

        if (duplicateResponse.duplicate && duplicateResponse.history_item_id) {
          setDuplicateHistoryInfo({
            id: duplicateResponse.history_item_id,
            translatedSummary:
              duplicateResponse.translated_summary ||
              'Este arquivo ja foi traduzido anteriormente.',
            createdAt: duplicateResponse.created_at,
          })
          return
        }

        const validationResponse = await validateFile(file)
        if (!validationResponse.success || !validationResponse.data) {
          throw new Error(validationResponse.error || 'Erro ao validar arquivo')
        }

        const validation = validationResponse.data
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
        const processingResult = await processarDocumento(file, undefined, undefined, undefined, llmProvider)
        if (!processingResult.success) {
          throw new Error(processingResult.error || 'Erro ao processar arquivo')
        }

        await handleProcessingSuccess(processingResult, effectiveCategory)
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
    setPendingTranslationId(null)
    setRequiresLocationConfirmation(false)
    setRevisaoSolicitada(false)
    setSolicitandoRevisao(false)
    setDuplicateHistoryInfo(null)
  }

  const handleSolicitarRevisao = async () => {
    if (!pendingTranslationId || revisaoSolicitada) return

    try {
      setSolicitandoRevisao(true)
      const response = await solicitarRevisao(pendingTranslationId)
      if (response.success) {
        setRevisaoSolicitada(true)
      }
    } catch (err) {
      console.error('Erro ao solicitar revisao:', err)
    } finally {
      setSolicitandoRevisao(false)
    }
  }

  const handleCategoryChange = (newCategory: DocumentCategory) => {
    setCategory(newCategory)
    setDocumentType(null)
    setResult(null)
    setValidationResult(null)
    setSubmissionError(null)
    setSubmissionStage('idle')
    setPendingTranslationId(null)
    setRequiresLocationConfirmation(false)
  }

  const handleConfirmLocation = async (
    municipio: string,
    estado: string,
    municipioIbgeId?: string
  ) => {
    if (!pendingTranslationId || !category) return

    try {
      setSubmissionError(null)
      setSubmissionStage('confirming-location')

      const processingResult = await confirmarLocalizacao(
        pendingTranslationId,
        municipio,
        estado,
        municipioIbgeId
      )

      if (!processingResult.success) {
        throw new Error(processingResult.error || 'Erro ao confirmar localizacao')
      }

      setResult(
        mapProcessingResultToTranslationResult(
          processingResult,
          category,
          result?.glossario || {}
        )
      )
      setRequiresLocationConfirmation(false)
    } catch (err) {
      if (err instanceof Error) {
        setSubmissionError(err.message)
      }
    } finally {
      setSubmissionStage('idle')
    }
  }

  const handleSkipLocationConfirmation = () => {
    setRequiresLocationConfirmation(false)
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
        <>
          <Card>
            <ProviderSelector 
              value={llmProvider} 
              onChange={setLlmProvider} 
              disabled={submissionStage !== 'idle'}
            />
          </Card>

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
        </>
      )}

      {submissionError && (
        <Alert variant="error" title="Erro">
          {submissionError}
        </Alert>
      )}

      {duplicateHistoryInfo && (
        <Alert variant="info" title="Documento ja traduzido">
          <div className="space-y-3">
            <p>
              Este arquivo ja foi traduzido anteriormente.
              {duplicateHistoryInfo.createdAt
                ? ` Ultimo acesso em ${formatBrazilDateTime(duplicateHistoryInfo.createdAt)}.`
                : ''}
            </p>
            <p className="text-sm">{duplicateHistoryInfo.translatedSummary}</p>
            {onOpenHistoryDocument && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onOpenHistoryDocument(duplicateHistoryInfo.id)}
              >
                Abrir documento salvo
              </Button>
            )}
          </div>
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

      {requiresLocationConfirmation && (
        <ConfirmacaoLocalizacao
          onConfirmar={handleConfirmLocation}
          onPular={handleSkipLocationConfirmation}
          isLoading={submissionStage === 'confirming-location'}
        />
      )}

      {documentType && (
        <div className="flex flex-col sm:flex-row justify-center gap-3">
          <Button
            onClick={handleSubmit}
            disabled={!canSubmit}
            isLoading={submissionStage === 'validating' || submissionStage === 'translating'}
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
        <ResultTabs result={result} />
      )}

      {result && user && pendingTranslationId && !embedded && (
        <Card className="mt-4">
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/50">
              <UserCheck className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-1">
                Solicitar revisao por especialista
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                Deseja que um profissional de saude revise esta traducao? O texto sera anonimizado para proteger sua privacidade.
              </p>
              {revisaoSolicitada ? (
                <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 text-sm">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Revisao solicitada! Voce sera notificado quando estiver pronta.
                </div>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleSolicitarRevisao}
                  isLoading={solicitandoRevisao}
                  leftIcon={<UserCheck className="w-4 h-4" />}
                >
                  Solicitar revisao
                </Button>
              )}
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
