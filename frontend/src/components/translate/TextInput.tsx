interface TextInputProps {
  value: string
  onChange: (text: string) => void
  maxLength?: number
}

export function TextInput({ value, onChange, maxLength = 10000 }: TextInputProps) {
  const charCount = value.length
  const isNearLimit = charCount > maxLength * 0.9

  return (
    <div>
      <label
        htmlFor="medical-text"
        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
      >
        Cole o texto do documento
      </label>
      <textarea
        id="medical-text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        maxLength={maxLength}
        rows={8}
        placeholder="Cole aqui o texto do seu exame, receita ou laudo médico..."
        className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600
                   bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                   placeholder-gray-400 dark:placeholder-gray-500
                   focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                   resize-none"
      />
      <div className="flex justify-between items-center mt-1">
        <p className="text-xs text-gray-500">
          Seus dados pessoais serão removidos automaticamente
        </p>
        <span
          className={`text-xs ${
            isNearLimit ? 'text-red-500' : 'text-gray-500'
          }`}
        >
          {charCount.toLocaleString()}/{maxLength.toLocaleString()}
        </span>
      </div>
    </div>
  )
}
