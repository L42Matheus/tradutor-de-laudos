import { useState } from 'react'
import { FileText, ClipboardCheck, BarChart3, AlertCircle } from 'lucide-react'
import { Alert } from '../components/ui/Alert'
import { Card } from '../components/ui/Card'
import { useAuth } from '../context/AuthContext'
import { HomePage } from './HomePage'
import { FilaRevisao } from '../components/specialist/FilaRevisao'
import { EstatisticasEspecialista } from '../components/specialist/EstatisticasEspecialista'

type TabId = 'traduzir' | 'revisar' | 'estatisticas'

interface Tab {
  id: TabId
  label: string
  icon: React.ReactNode
}

const TABS: Tab[] = [
  { id: 'traduzir', label: 'Traduzir Laudo', icon: <FileText className="w-5 h-5" /> },
  { id: 'revisar', label: 'Fila de Revisao', icon: <ClipboardCheck className="w-5 h-5" /> },
  { id: 'estatisticas', label: 'Estatisticas', icon: <BarChart3 className="w-5 h-5" /> },
]

export function SpecialistPage() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState<TabId>('traduzir')

  const isVerified = user?.specialist_verification_status === 'verified'

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <Card className="bg-gradient-to-br from-emerald-50 via-white to-blue-50 dark:from-emerald-950/30 dark:via-slate-900 dark:to-blue-950/30 border-0 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-emerald-100 dark:bg-emerald-900/50">
            <ClipboardCheck className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
              Area do Especialista
            </p>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
              Bem-vindo, {user?.full_name?.split(' ')[0]}
            </h2>
          </div>
        </div>
        <p className="mt-4 text-sm text-slate-600 dark:text-slate-400 max-w-2xl">
          Traduza seus proprios laudos ou revise traducoes de outros usuarios para validar
          a qualidade do sistema e contribuir com feedback tecnico.
        </p>
      </Card>

      {/* Verificacao pendente */}
      {!isVerified && (
        <Alert variant="warning" title="Verificacao pendente">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>
              Seu cadastro esta com status <strong>{user?.specialist_verification_status}</strong>.
              A fila de revisao sera liberada apos a verificacao do seu registro profissional.
            </span>
          </div>
        </Alert>
      )}

      {/* Tabs */}
      <div className="border-b border-slate-200 dark:border-slate-700">
        <nav className="flex gap-1 -mb-px">
          {TABS.map((tab) => {
            const isActive = activeTab === tab.id
            const isDisabled = !isVerified && tab.id === 'revisar'

            return (
              <button
                key={tab.id}
                onClick={() => !isDisabled && setActiveTab(tab.id)}
                disabled={isDisabled}
                className={`
                  flex items-center gap-2 px-5 py-3 text-sm font-medium rounded-t-lg transition-all
                  ${isActive
                    ? 'bg-white dark:bg-slate-800 text-blue-600 dark:text-blue-400 border border-b-0 border-slate-200 dark:border-slate-700'
                    : isDisabled
                      ? 'text-slate-400 dark:text-slate-600 cursor-not-allowed'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800/50'
                  }
                `}
              >
                {tab.icon}
                {tab.label}
                {tab.id === 'revisar' && !isVerified && (
                  <span className="ml-1 text-xs text-amber-500">(bloqueado)</span>
                )}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {activeTab === 'traduzir' && (
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <HomePage embedded />
          </div>
        )}

        {activeTab === 'revisar' && isVerified && (
          <FilaRevisao />
        )}

        {activeTab === 'estatisticas' && (
          <EstatisticasEspecialista />
        )}
      </div>
    </div>
  )
}
