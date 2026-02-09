import { FileText, List, Lightbulb, BookOpen, Copy, Check, Heart } from 'lucide-react'
import { useState } from 'react'
import { Tabs } from '../ui/Tabs'
import { Alert } from '../ui/Alert'
import { Card } from '../ui/Card'
import type { TranslationResult } from '../../types/api'
import { EmotionalSupportInline } from '../support/EmotionalSupportInline'

interface ResultTabsProps {
  result: TranslationResult
  anonymizedFields?: string[]
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button
      onClick={handleCopy}
      className="inline-flex items-center gap-1 px-2 py-1 text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
    >
      {copied ? (
        <>
          <Check size={14} />
          Copiado!
        </>
      ) : (
        <>
          <Copy size={14} />
          Copiar
        </>
      )}
    </button>
  )
}

function TabContent({ content, title }: { content: string; title: string }) {
  return (
    <div>
      <div className="flex justify-between items-center mb-3">
        <h4 className="font-medium text-gray-900 dark:text-white">{title}</h4>
        <CopyButton text={content} />
      </div>
      <div className="prose prose-sm dark:prose-invert max-w-none">
        <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{content}</p>
      </div>
    </div>
  )
}

function GlossaryContent({ glossario }: { glossario: Record<string, string> }) {
  const entries = Object.entries(glossario)

  if (entries.length === 0) {
    return (
      <p className="text-gray-500 dark:text-gray-400 italic">
        Nenhum termo técnico identificado neste documento.
      </p>
    )
  }

  return (
    <div className="space-y-3">
      {entries.map(([term, definition]) => (
        <div
          key={term}
          className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
        >
          <dt className="font-medium text-primary-600 dark:text-primary-400">
            {term}
          </dt>
          <dd className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {definition}
          </dd>
        </div>
      ))}
    </div>
  )
}

export function ResultTabs({ result, anonymizedFields }: ResultTabsProps) {
  const tabs = [
    {
      id: 'resumo',
      label: 'Resumo',
      icon: <FileText size={16} />,
      content: <TabContent content={result.resumo} title="Resumo do documento" />,
    },
    {
      id: 'detalhado',
      label: 'Detalhado',
      icon: <List size={16} />,
      content: <TabContent content={result.detalhado} title="Explicação detalhada" />,
    },
    {
      id: 'entenda_facil',
      label: 'Entenda Fácil',
      icon: <Lightbulb size={16} />,
      content: <TabContent content={result.entenda_facil} title="Explicação simplificada" />,
    },
    {
      id: 'glossario',
      label: 'Termos',
      icon: <BookOpen size={16} />,
      content: <GlossaryContent glossario={result.glossario} />,
    },
  ]

  return (
    <Card>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Resultado da Tradução
      </h3>

      {/* Alertas */}
      {result.alertas && result.alertas.length > 0 && (
        <div className="mb-4 space-y-2">
          {result.alertas.map((alerta, index) => (
            <Alert key={index} variant="warning">
              {alerta}
            </Alert>
          ))}
        </div>
      )}

      {/* Campos anonimizados */}
      {anonymizedFields && anonymizedFields.length > 0 && (
        <Alert variant="info" className="mb-4">
          <strong>Dados removidos para sua privacidade:</strong>{' '}
          {anonymizedFields.join(', ')}
        </Alert>
      )}

      {/* Tabs com resultado */}
      <Tabs tabs={tabs} />

      {/* Apoio emocional para documentos de saúde mental */}
      {result.is_saude_mental && (
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 text-purple-600 dark:text-purple-400 mb-4">
            <Heart size={20} />
            <h4 className="font-semibold">Apoio Emocional</h4>
          </div>
          <EmotionalSupportInline />
        </div>
      )}
    </Card>
  )
}
