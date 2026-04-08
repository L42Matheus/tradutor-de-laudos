import { useQuery } from '@tanstack/react-query'
import { FileClock, FolderOpen, Home, LogOut, Phone, X } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { useUsage } from '../../context/UsageContext'
import { getMyTranslationHistory } from '../../services/api'
import { formatBrazilDateTime } from '../../utils/datetime'
import { EmotionalSupport } from '../support/EmotionalSupport'
import { Button } from '../ui/Button'

type PatientView = 'home' | 'history'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
  activeView?: PatientView
  onNavigate?: (view: PatientView, historyId?: string) => void
}

export function Sidebar({ isOpen, onClose, activeView = 'home', onNavigate }: SidebarProps) {
  const { usage } = useUsage()
  const { user, logout } = useAuth()
  const { data: historyResponse } = useQuery({
    queryKey: ['translation-history', 3],
    queryFn: () => getMyTranslationHistory(3),
    staleTime: 1000 * 60,
    enabled: Boolean(user && user.account_type !== 'specialist'),
  })

  const history = historyResponse?.success ? historyResponse.data : []

  return (
    <>
      {isOpen && <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={onClose} />}

      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          w-80 bg-white dark:bg-gray-900
          border-r border-gray-200 dark:border-gray-800
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          overflow-y-auto
        `}
      >
        <div className="p-4">
          <button
            onClick={onClose}
            className="lg:hidden absolute top-4 right-4 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            aria-label="Fechar menu"
          >
            <X size={20} />
          </button>

          {user && (
            <div className="mb-6 p-4 bg-sky-50 dark:bg-sky-900/20 rounded-lg border border-sky-100 dark:border-sky-900/40">
              <p className="text-xs uppercase tracking-wide text-sky-700 dark:text-sky-300 mb-1">
                Conta ativa
              </p>
              <p className="font-semibold text-gray-900 dark:text-white">{user.full_name}</p>
              <p className="text-sm text-gray-600 dark:text-gray-300">{user.email}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                Acesso: {user.account_type === 'specialist' ? 'especialista' : 'paciente'}
              </p>
              {user.account_type === 'specialist' && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Verificacao: {user.specialist_verification_status}
                </p>
              )}
              <Button
                onClick={logout}
                variant="outline"
                size="sm"
                className="mt-3 w-full"
                leftIcon={<LogOut size={16} />}
              >
                Sair
              </Button>
            </div>
          )}

          {usage && user?.account_type !== 'specialist' && (
            <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <h3 className="font-semibold text-sm mb-2">Traducoes disponiveis</h3>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary-500 transition-all duration-300"
                    style={{
                      width: `${((usage.translations_limit - usage.translations_remaining) / usage.translations_limit) * 100}%`,
                    }}
                  />
                </div>
                <span className="text-sm font-medium">
                  {usage.translations_remaining}/{usage.translations_limit}
                </span>
              </div>
            </div>
          )}

          {user?.account_type !== 'specialist' && (
            <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg space-y-2">
              <button
                type="button"
                onClick={() => {
                  onNavigate?.('home')
                  onClose()
                }}
                className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  activeView === 'home'
                    ? 'bg-white text-primary-700 shadow-sm dark:bg-slate-700 dark:text-primary-300'
                    : 'text-gray-600 hover:bg-white hover:text-gray-900 dark:text-gray-300 dark:hover:bg-slate-700 dark:hover:text-white'
                }`}
              >
                <Home size={16} />
                Traduzir documento
              </button>
              <button
                type="button"
                onClick={() => {
                  onNavigate?.('history')
                  onClose()
                }}
                className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  activeView === 'history'
                    ? 'bg-white text-primary-700 shadow-sm dark:bg-slate-700 dark:text-primary-300'
                    : 'text-gray-600 hover:bg-white hover:text-gray-900 dark:text-gray-300 dark:hover:bg-slate-700 dark:hover:text-white'
                }`}
              >
                <FolderOpen size={16} />
                Meus documentos
              </button>
            </div>
          )}

          {user?.account_type !== 'specialist' && (
            <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                <FileClock size={18} />
                <h3 className="font-semibold text-sm">Historico recente</h3>
              </div>
              {history.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Suas traducoes aparecerao aqui apos o primeiro uso.
                </p>
              ) : (
                <div className="space-y-3">
                  {history.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => {
                        onNavigate?.('history', item.id)
                        onClose()
                      }}
                      className="w-full rounded-lg border border-gray-200 p-3 text-left transition-colors hover:border-primary-300 hover:bg-white dark:border-gray-700 dark:hover:border-primary-700 dark:hover:bg-slate-700"
                    >
                      <p className="text-xs text-primary-600 dark:text-primary-400 font-medium">
                        {item.document_category || item.source}
                      </p>
                      <p className="text-sm text-gray-800 dark:text-gray-200 line-clamp-3">
                        {item.translated_summary}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                        {formatBrazilDateTime(item.created_at)}
                      </p>
                    </button>
                  ))}
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full"
                    onClick={() => {
                      onNavigate?.('history')
                      onClose()
                    }}
                    leftIcon={<FolderOpen size={16} />}
                  >
                    Ver todos os documentos
                  </Button>
                </div>
              )}
            </div>
          )}

          <EmotionalSupport />

          <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <div className="flex items-center gap-2 text-red-600 dark:text-red-400 font-semibold mb-2">
              <Phone size={18} />
              <span>Em crise? Ligue agora</span>
            </div>
            <a
              href="tel:188"
              className="text-2xl font-bold text-red-600 dark:text-red-400 hover:underline"
            >
              188
            </a>
            <p className="text-xs text-red-500 dark:text-red-400 mt-1">CVV - 24 horas, gratuito</p>
          </div>
        </div>
      </aside>
    </>
  )
}
