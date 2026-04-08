import { useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { FileImage, FileText, FolderOpen, History, ScanText } from 'lucide-react'
import { getMyTranslationHistory } from '../services/api'
import type { TranslationHistoryItem, TranslationResult } from '../types/api'
import { formatBrazilDateTime } from '../utils/datetime'
import { Card } from '../components/ui/Card'
import { Alert } from '../components/ui/Alert'
import { Button } from '../components/ui/Button'
import { ResultTabs } from '../components/translate/ResultTabs'

interface HistoryPageProps {
  selectedHistoryId?: string | null
  onBackToHome: () => void
}

function getHistoryLabel(item: TranslationHistoryItem) {
  return item.document_category || item.document_type || item.source
}

function getDetailedTranslation(item: TranslationHistoryItem) {
  const detalhado = item.result_payload?.detalhado
  return typeof detalhado === 'string' && detalhado.trim()
    ? detalhado
    : item.translated_summary
}

function getStringValue(payload: Record<string, unknown>, key: string) {
  const value = payload[key]
  return typeof value === 'string' && value.trim() ? value : null
}

function getGlossaryValue(payload: Record<string, unknown>) {
  const value = payload.glossario
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return {}
  }

  return Object.entries(value).reduce<Record<string, string>>((acc, [term, definition]) => {
    if (typeof definition === 'string' && definition.trim()) {
      acc[term] = definition
    }
    return acc
  }, {})
}

function getAlertsValue(payload: Record<string, unknown>) {
  const value = payload.alertas
  if (!Array.isArray(value)) {
    return []
  }

  return value.filter((item): item is string => typeof item === 'string' && item.trim().length > 0)
}

function buildHistoryResult(item: TranslationHistoryItem): TranslationResult {
  const payload = item.result_payload
  const resumo =
    getStringValue(payload, 'resumo') ||
    getStringValue(payload, 'texto_traduzido') ||
    item.translated_summary
  const detalhado = getStringValue(payload, 'detalhado') || getDetailedTranslation(item)
  const entendaFacil = getStringValue(payload, 'entenda_facil') || resumo

  return {
    resumo,
    detalhado,
    entenda_facil: entendaFacil,
    glossario: getGlossaryValue(payload),
    alertas: getAlertsValue(payload),
    is_saude_mental: Boolean(payload.is_saude_mental),
    from_cache: Boolean(payload.from_cache),
    professional_authorship_detected: Boolean(payload.professional_authorship_detected),
    professional_authorship_evidence: Array.isArray(payload.professional_authorship_evidence)
      ? payload.professional_authorship_evidence.filter(
          (item): item is string => typeof item === 'string' && item.trim().length > 0
        )
      : [],
  }
}

function getOriginalText(item: TranslationHistoryItem) {
  if (item.original_text?.trim()) {
    return item.original_text
  }

  if (item.original_image_base64) {
    return 'Este documento foi enviado como imagem. A visualizacao esta disponivel abaixo.'
  }

  return 'Conteudo original nao disponivel para este item.'
}

function getImageSrc(item: TranslationHistoryItem) {
  if (!item.original_image_base64 || !item.original_image_media_type) {
    return null
  }

  return `data:${item.original_image_media_type};base64,${item.original_image_base64}`
}

export function HistoryPage({ selectedHistoryId, onBackToHome }: HistoryPageProps) {
  const { data: historyResponse, isLoading } = useQuery({
    queryKey: ['translation-history', 100],
    queryFn: () => getMyTranslationHistory(100),
    staleTime: 1000 * 60,
  })

  const history = historyResponse?.success ? historyResponse.data : []
  const [selectedId, setSelectedId] = useState<string | null>(selectedHistoryId ?? null)

  useEffect(() => {
    if (selectedHistoryId) {
      setSelectedId(selectedHistoryId)
      return
    }

    if (!selectedId && history.length > 0) {
      setSelectedId(history[0].id)
    }
  }, [history, selectedHistoryId, selectedId])

  const selectedItem = useMemo(() => {
    if (history.length === 0) {
      return null
    }

    return history.find((item) => item.id === selectedId) ?? history[0]
  }, [history, selectedId])

  if (isLoading) {
    return <div className="max-w-6xl mx-auto py-16 text-center text-gray-500">Carregando historico...</div>
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card className="bg-gradient-to-br from-sky-50 via-white to-blue-50 border-0 shadow-xl dark:from-sky-950/30 dark:via-slate-900 dark:to-blue-950/30">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="rounded-xl bg-sky-100 p-3 dark:bg-sky-900/50">
              <History className="h-6 w-6 text-sky-600 dark:text-sky-400" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-sky-600 dark:text-sky-400">
                Historico do paciente
              </p>
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
                Seus documentos e traducoes
              </h2>
              <p className="mt-2 max-w-2xl text-sm text-slate-600 dark:text-slate-400">
                Aqui voce encontra todos os documentos processados, o texto salvo do laudo e a traducao detalhada.
              </p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={onBackToHome} leftIcon={<ScanText size={16} />}>
            Nova traducao
          </Button>
        </div>
      </Card>

      {history.length === 0 ? (
        <Alert variant="info" title="Nenhum documento encontrado">
          Seu historico ficara disponivel aqui depois da primeira traducao.
        </Alert>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[320px,1fr]">
          <Card className="p-0 overflow-hidden">
            <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
              <h3 className="font-semibold text-slate-900 dark:text-white">Todos os documentos</h3>
            </div>
            <div className="max-h-[720px] overflow-y-auto p-3 space-y-3">
              {history.map((item) => {
                const isActive = selectedItem?.id === item.id

                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setSelectedId(item.id)}
                    className={`w-full rounded-xl border p-3 text-left transition-colors ${
                      isActive
                        ? 'border-primary-400 bg-primary-50 dark:border-primary-700 dark:bg-primary-900/20'
                        : 'border-gray-200 hover:border-primary-300 hover:bg-white dark:border-gray-700 dark:hover:border-primary-700 dark:hover:bg-slate-800'
                    }`}
                  >
                    <p className="text-xs font-semibold uppercase tracking-wide text-primary-600 dark:text-primary-400">
                      {getHistoryLabel(item)}
                    </p>
                    <p className="mt-2 line-clamp-3 text-sm text-slate-800 dark:text-slate-200">
                      {item.translated_summary}
                    </p>
                    <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                      {formatBrazilDateTime(item.created_at)}
                    </p>
                  </button>
                )
              })}
            </div>
          </Card>

          {selectedItem && (
            <div className="space-y-6">
              <Card>
                <div className="flex items-start gap-3">
                  <div className="rounded-lg bg-primary-100 p-2 dark:bg-primary-900/30">
                    {selectedItem.original_image_base64 ? (
                      <FileImage className="h-5 w-5 text-primary-600 dark:text-primary-400" />
                    ) : (
                      <FileText className="h-5 w-5 text-primary-600 dark:text-primary-400" />
                    )}
                  </div>
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-primary-600 dark:text-primary-400">
                      Documento selecionado
                    </p>
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white">
                      {getHistoryLabel(selectedItem)}
                    </h3>
                    <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                      {formatBrazilDateTime(selectedItem.created_at)}
                    </p>
                  </div>
                </div>
              </Card>

              <Card>
                <div className="flex items-center gap-2">
                  <FolderOpen className="h-5 w-5 text-slate-500 dark:text-slate-400" />
                  <h4 className="font-semibold text-slate-900 dark:text-white">Laudo salvo</h4>
                </div>
                <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-slate-700 dark:text-slate-300">
                  {getOriginalText(selectedItem)}
                </p>
                {getImageSrc(selectedItem) && (
                  <img
                    src={getImageSrc(selectedItem)!}
                    alt="Documento original enviado pelo paciente"
                    className="mt-4 max-h-[520px] w-full rounded-xl border border-gray-200 object-contain dark:border-gray-700"
                  />
                )}
              </Card>

              <Card>
                <div className="flex items-center gap-2">
                  <ScanText className="h-5 w-5 text-slate-500 dark:text-slate-400" />
                  <h4 className="font-semibold text-slate-900 dark:text-white">Resultado salvo</h4>
                </div>
                <div className="mt-4">
                  <ResultTabs result={buildHistoryResult(selectedItem)} embedded />
                </div>
              </Card>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
