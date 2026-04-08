import { useState, useEffect } from 'react'
import { ClipboardList, Eye, Clock, CheckCircle2, AlertTriangle } from 'lucide-react'
import { Card } from '../ui/Card'
import { Button } from '../ui/Button'
import { ModalRevisao } from './ModalRevisao'
import api from '../../services/api'
import { formatBrazilDateTime } from '../../utils/datetime'

interface TraducaoItem {
  id: string
  texto_original_preview: string
  condicao_categoria: string | null
  criado_em: string
}

interface FilaResponse {
  success: boolean
  total: number
  items: TraducaoItem[]
}

export function FilaRevisao() {
  const [fila, setFila] = useState<TraducaoItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const carregarFila = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get<FilaResponse>('/revisao/fila')
      if (response.data.success) {
        setFila(response.data.items)
        setTotal(response.data.total)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao carregar fila')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    carregarFila()
  }, [])

  const handleRevisaoConcluida = () => {
    setSelectedId(null)
    carregarFila()
  }

  const formatarData = (data: string) => {
    return formatBrazilDateTime(data)
  }

  const categoriaLabel: Record<string, string> = {
    cardiovascular: 'Cardiovascular',
    respiratorio: 'Respiratorio',
    neurologico: 'Neurologico',
    oncologico: 'Oncologico',
    ortopedico: 'Ortopedico',
    endocrinologico: 'Endocrinologico',
    outro: 'Outro'
  }

  if (loading) {
    return (
      <Card>
        <div className="flex items-center justify-center py-12 text-slate-500 dark:text-slate-400">
          <Clock className="w-5 h-5 animate-spin mr-2" />
          Carregando fila de revisao...
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <div className="flex items-center justify-center py-12 text-red-500">
          <AlertTriangle className="w-5 h-5 mr-2" />
          {error}
        </div>
      </Card>
    )
  }

  return (
    <>
      <Card>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/50">
              <ClipboardList className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                Fila de Revisao
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {total} {total === 1 ? 'laudo aguardando' : 'laudos aguardando'} revisao
              </p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={carregarFila}>
            Atualizar
          </Button>
        </div>

        {fila.length === 0 ? (
          <div className="text-center py-12 border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-xl">
            <CheckCircle2 className="w-12 h-12 mx-auto text-emerald-500 mb-3" />
            <p className="text-slate-600 dark:text-slate-400">
              Nenhum laudo pendente de revisao
            </p>
            <p className="text-sm text-slate-500 dark:text-slate-500 mt-1">
              Os laudos aparecerao aqui quando pacientes solicitarem revisao
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {fila.map((item) => (
              <div
                key={item.id}
                className="flex items-start justify-between p-4 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-700 transition-colors"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    {item.condicao_categoria && (
                      <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300">
                        {categoriaLabel[item.condicao_categoria] || item.condicao_categoria}
                      </span>
                    )}
                    <span className="text-xs text-slate-500 dark:text-slate-400">
                      {formatarData(item.criado_em)}
                    </span>
                  </div>
                  <p className="text-sm text-slate-700 dark:text-slate-300 line-clamp-2">
                    {item.texto_original_preview}
                  </p>
                </div>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => setSelectedId(item.id)}
                  leftIcon={<Eye className="w-4 h-4" />}
                  className="ml-4 flex-shrink-0"
                >
                  Revisar
                </Button>
              </div>
            ))}
          </div>
        )}
      </Card>

      {selectedId && (
        <ModalRevisao
          traducaoId={selectedId}
          onClose={() => setSelectedId(null)}
          onSuccess={handleRevisaoConcluida}
        />
      )}
    </>
  )
}
