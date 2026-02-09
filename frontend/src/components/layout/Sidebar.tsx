import { X, Heart, Phone, ExternalLink } from 'lucide-react'
import { useUsage } from '../../context/UsageContext'
import { EmotionalSupport } from '../support/EmotionalSupport'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { usage } = useUsage()

  return (
    <>
      {/* Overlay mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
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
          {/* Botão fechar (mobile) */}
          <button
            onClick={onClose}
            className="lg:hidden absolute top-4 right-4 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            aria-label="Fechar menu"
          >
            <X size={20} />
          </button>

          {/* Status de uso */}
          {usage && (
            <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <h3 className="font-semibold text-sm mb-2">Traduções disponíveis</h3>
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
              {usage.is_limit_reached && (
                <p className="text-xs text-red-500 mt-2">
                  Limite atingido. Aguarde para mais traduções.
                </p>
              )}
            </div>
          )}

          {/* Apoio emocional */}
          <EmotionalSupport />

          {/* Linha de emergência */}
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
            <p className="text-xs text-red-500 dark:text-red-400 mt-1">
              CVV - 24 horas, gratuito
            </p>
          </div>
        </div>
      </aside>
    </>
  )
}
