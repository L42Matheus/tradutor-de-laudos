import { Brain, Sparkles, Zap } from 'lucide-react'
import type { LLMProvider } from '../../types/api'
import { PROVIDER_LABELS } from '../../types/api'

interface ProviderSelectorProps {
  value: LLMProvider
  onChange: (provider: LLMProvider) => void
  disabled?: boolean
}

export function ProviderSelector({ value, onChange, disabled }: ProviderSelectorProps) {
  const providers: { id: LLMProvider; icon: any; color: string }[] = [
    { id: 'claude', icon: Brain, color: 'text-orange-500' },
    { id: 'openai', icon: Zap, color: 'text-emerald-500' },
    { id: 'gemini', icon: Sparkles, color: 'text-blue-500' },
  ]

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Selecione a Inteligencia Artificial para traduzir
      </label>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {providers.map((provider) => {
          const Icon = provider.icon
          const isActive = value === provider.id

          return (
            <button
              key={provider.id}
              type="button"
              disabled={disabled}
              onClick={() => onChange(provider.id)}
              className={`flex items-center gap-3 p-3 rounded-xl border-2 transition-all text-left ${
                isActive
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 shadow-sm'
                  : 'border-gray-100 dark:border-gray-800 hover:border-gray-200 dark:hover:border-gray-700 bg-white dark:bg-slate-900'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <div className={`p-2 rounded-lg ${isActive ? 'bg-white dark:bg-slate-800 shadow-sm' : 'bg-gray-50 dark:bg-gray-800'}`}>
                <Icon size={20} className={provider.color} />
              </div>
              <div>
                <p className={`text-sm font-semibold ${isActive ? 'text-primary-700 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300'}`}>
                  {provider.id.charAt(0).toUpperCase() + provider.id.slice(1)}
                </p>
                <p className="text-[10px] text-gray-500 dark:text-gray-400 line-clamp-1">
                  {PROVIDER_LABELS[provider.id].split('(')[1].replace(')', '')}
                </p>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
