import { useState } from 'react'
import { Heart, RefreshCw, Wind, ExternalLink } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { getRandomQuote, getExercises } from '../../services/api'
import { Button } from '../ui/Button'

export function EmotionalSupport() {
  const [quoteKey, setQuoteKey] = useState(0)

  const { data: quote, isLoading: quoteLoading } = useQuery({
    queryKey: ['quote', quoteKey],
    queryFn: getRandomQuote,
    staleTime: Infinity,
  })

  const { data: exercises } = useQuery({
    queryKey: ['exercises'],
    queryFn: getExercises,
    staleTime: 1000 * 60 * 30, // 30 minutos
  })

  const handleNewQuote = () => {
    setQuoteKey((prev) => prev + 1)
  }

  // Escolher um exercício aleatório
  const randomExercise = exercises?.[Math.floor(Math.random() * (exercises?.length || 1))]

  return (
    <div className="space-y-4">
      {/* Título da seção */}
      <div className="flex items-center gap-2 text-primary-600 dark:text-primary-400">
        <Heart size={18} />
        <h3 className="font-semibold">Apoio Emocional</h3>
      </div>

      {/* Frase motivacional */}
      <div className="bg-gradient-to-br from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 rounded-lg p-4">
        {quoteLoading ? (
          <p className="text-sm text-gray-500 italic">Carregando...</p>
        ) : (
          <p className="text-sm text-gray-700 dark:text-gray-300 italic">
            "{quote?.quote}"
          </p>
        )}
        <Button
          variant="outline"
          size="sm"
          onClick={handleNewQuote}
          leftIcon={<RefreshCw size={14} />}
          className="mt-3"
        >
          Nova frase
        </Button>
      </div>

      {/* Exercício de respiração */}
      {randomExercise && (
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
          <div className="flex items-center gap-2 text-green-700 dark:text-green-400 font-medium mb-2">
            <Wind size={16} />
            <span>{randomExercise.name}</span>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {randomExercise.description}
          </p>
          <ol className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            {randomExercise.steps.map((step, index) => (
              <li key={index} className="flex gap-2">
                <span className="text-green-600 dark:text-green-400 font-medium">
                  {index + 1}.
                </span>
                {step}
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Links úteis */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Recursos de apoio
        </h4>
        <a
          href="https://open.spotify.com/playlist/37i9dQZF1DWXe9gFZP0gtP"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-sm text-primary-600 dark:text-primary-400 hover:underline"
        >
          <ExternalLink size={14} />
          Playlist de relaxamento
        </a>
        <a
          href="https://www.youtube.com/watch?v=inpok4MKVLM"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-sm text-primary-600 dark:text-primary-400 hover:underline"
        >
          <ExternalLink size={14} />
          Meditação guiada (10 min)
        </a>
      </div>
    </div>
  )
}
