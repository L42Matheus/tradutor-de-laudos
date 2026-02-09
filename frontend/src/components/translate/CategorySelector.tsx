import { clsx } from 'clsx'
import { FileText, Pill, Brain } from 'lucide-react'
import type { DocumentCategory } from '../../types/api'
import { CATEGORY_LABELS } from '../../types/api'

interface CategorySelectorProps {
  value: DocumentCategory | null
  onChange: (category: DocumentCategory) => void
}

const categories: { id: DocumentCategory; icon: typeof FileText; color: string }[] = [
  { id: 'laudo', icon: FileText, color: 'blue' },
  { id: 'receita', icon: Pill, color: 'green' },
  { id: 'saude_mental', icon: Brain, color: 'purple' },
]

export function CategorySelector({ value, onChange }: CategorySelectorProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Tipo de documento
      </label>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {categories.map(({ id, icon: Icon, color }) => (
          <button
            key={id}
            onClick={() => onChange(id)}
            className={clsx(
              'p-4 rounded-lg border-2 transition-all duration-200',
              'flex flex-col items-center gap-2 text-center',
              value === id
                ? `border-${color}-500 bg-${color}-50 dark:bg-${color}-900/20`
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600',
              value === id
                ? `text-${color}-700 dark:text-${color}-400`
                : 'text-gray-600 dark:text-gray-400'
            )}
            style={{
              borderColor: value === id
                ? color === 'blue' ? '#3b82f6' : color === 'green' ? '#22c55e' : '#a855f7'
                : undefined,
              backgroundColor: value === id
                ? color === 'blue' ? '#eff6ff' : color === 'green' ? '#f0fdf4' : '#faf5ff'
                : undefined,
            }}
          >
            <Icon size={24} />
            <span className="text-sm font-medium">{CATEGORY_LABELS[id]}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
