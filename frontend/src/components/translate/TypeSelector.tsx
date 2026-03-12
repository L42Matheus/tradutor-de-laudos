import type { DocumentCategory } from '../../types/api'
import {
  LAUDO_TYPE_LABELS,
  RECEITA_TYPE_LABELS,
  SAUDE_MENTAL_TYPE_LABELS,
} from '../../types/api'

interface TypeSelectorProps {
  category: DocumentCategory
  value: string | null
  onChange: (type: string) => void
}

const typesByCategory: Record<DocumentCategory, Record<string, string>> = {
  laudo: LAUDO_TYPE_LABELS,
  receita: RECEITA_TYPE_LABELS,
  saude_mental: SAUDE_MENTAL_TYPE_LABELS,
}

export function TypeSelector({ category, value, onChange }: TypeSelectorProps) {
  const types = typesByCategory[category] || {}

  return (
    <div>
      <label
        htmlFor="document-type"
        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
      >
        Especifique o tipo
      </label>
      <select
        id="document-type"
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600
                   bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
      >
        <option value="">Selecione o tipo...</option>
        {Object.entries(types).map(([key, label]) => (
          <option key={key} value={key}>
            {label}
          </option>
        ))}
      </select>
    </div>
  )
}
