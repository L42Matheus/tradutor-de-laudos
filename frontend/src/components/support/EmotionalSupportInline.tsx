import { Phone, ExternalLink, Heart, Shield } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { getResources, getRandomQuote } from '../../services/api'

export function EmotionalSupportInline() {
  const { data: resources } = useQuery({
    queryKey: ['resources'],
    queryFn: getResources,
  })

  const { data: quote } = useQuery({
    queryKey: ['inline-quote'],
    queryFn: getRandomQuote,
  })

  return (
    <div className="space-y-4">
      {/* Mensagem de apoio */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Heart className="text-purple-500 flex-shrink-0 mt-1" size={20} />
          <div>
            <p className="text-gray-700 dark:text-gray-300 mb-2">
              Entendemos que documentos relacionados à saúde mental podem trazer sentimentos intensos.
              <strong> Você não está sozinho(a).</strong>
            </p>
            {quote && (
              <p className="text-sm italic text-purple-700 dark:text-purple-300">
                "{quote.quote}"
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Recursos de apoio */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {resources?.map((resource) => (
          <div
            key={resource.name}
            className={`p-4 rounded-lg border ${
              resource.is_emergency
                ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                : 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700'
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              {resource.is_emergency ? (
                <Phone className="text-red-500" size={18} />
              ) : (
                <Shield className="text-primary-500" size={18} />
              )}
              <h5 className={`font-medium text-sm ${
                resource.is_emergency
                  ? 'text-red-700 dark:text-red-300'
                  : 'text-gray-900 dark:text-white'
              }`}>
                {resource.name}
              </h5>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
              {resource.description}
            </p>
            {resource.is_emergency ? (
              <a
                href={`tel:${resource.contact}`}
                className="text-lg font-bold text-red-600 dark:text-red-400 hover:underline"
              >
                {resource.contact}
              </a>
            ) : (
              <p className="text-sm text-gray-700 dark:text-gray-300">
                {resource.contact}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Links adicionais */}
      <div className="flex flex-wrap gap-4 text-sm">
        <a
          href="https://open.spotify.com/playlist/37i9dQZF1DWXe9gFZP0gtP"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-primary-600 dark:text-primary-400 hover:underline"
        >
          <ExternalLink size={14} />
          Músicas relaxantes
        </a>
        <a
          href="https://www.youtube.com/watch?v=inpok4MKVLM"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-primary-600 dark:text-primary-400 hover:underline"
        >
          <ExternalLink size={14} />
          Meditação guiada
        </a>
      </div>
    </div>
  )
}
