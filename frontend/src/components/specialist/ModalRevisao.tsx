import { useState, useEffect } from 'react'
import { X, FileText, MessageSquare, Send, Star, AlertTriangle, CheckCircle } from 'lucide-react'
import { Button } from '../ui/Button'
import api from '../../services/api'

interface TraducaoDetalhe {
  id: string
  texto_original: string
  texto_traduzido: string
  condicao_categoria: string | null
  criado_em: string
}

interface ModalRevisaoProps {
  traducaoId: string
  onClose: () => void
  onSuccess: () => void
}

export function ModalRevisao({ traducaoId, onClose, onSuccess }: ModalRevisaoProps) {
  const [traducao, setTraducao] = useState<TraducaoDetalhe | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const [notaFidelidade, setNotaFidelidade] = useState(3)
  const [notaClareza, setNotaClareza] = useState(3)
  const [notaRisco, setNotaRisco] = useState(3)
  const [comentario, setComentario] = useState('')
  const [sugestao, setSugestao] = useState('')

  useEffect(() => {
    const carregarTraducao = async () => {
      try {
        const response = await api.get<TraducaoDetalhe>(`/revisao/traducao/${traducaoId}`)
        setTraducao(response.data)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Erro ao carregar traducao')
      } finally {
        setLoading(false)
      }
    }
    carregarTraducao()
  }, [traducaoId])

  const handleSubmit = async () => {
    setSubmitting(true)
    setError(null)
    try {
      await api.post('/revisao/parecer', {
        traducao_id: traducaoId,
        nota_fidelidade: notaFidelidade,
        nota_clareza: notaClareza,
        nota_risco: notaRisco,
        comentario_tecnico: comentario || null,
        sugestao_correcao: sugestao || null
      })
      setSuccess(true)
      setTimeout(() => {
        onSuccess()
      }, 1500)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao enviar parecer')
    } finally {
      setSubmitting(false)
    }
  }

  const NotaSelector = ({
    label,
    value,
    onChange,
    description
  }: {
    label: string
    value: number
    onChange: (v: number) => void
    description: string
  }) => (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
          {label}
        </label>
        <span className="text-xs text-slate-500 dark:text-slate-400">{description}</span>
      </div>
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            type="button"
            onClick={() => onChange(n)}
            className={`
              flex-1 py-2 rounded-lg text-sm font-medium transition-all
              ${value === n
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600'
              }
            `}
          >
            {n}
          </button>
        ))}
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-8">
          <p className="text-slate-600 dark:text-slate-400">Carregando...</p>
        </div>
      </div>
    )
  }

  if (success) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-8 text-center">
          <CheckCircle className="w-16 h-16 mx-auto text-emerald-500 mb-4" />
          <p className="text-lg font-semibold text-slate-900 dark:text-white">
            Parecer registrado!
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-500" />
            Revisao de Laudo
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
          >
            <X className="w-5 h-5 text-slate-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              {error}
            </div>
          )}

          <div className="grid lg:grid-cols-2 gap-4 mb-6">
            {/* Texto Original */}
            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                Laudo Original (Anonimizado)
              </h3>
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 h-64 overflow-auto">
                <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
                  {traducao?.texto_original}
                </p>
              </div>
            </div>

            {/* Traducao */}
            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wide">
                Traducao do Sistema
              </h3>
              <div className="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 h-64 overflow-auto">
                <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
                  {traducao?.texto_traduzido}
                </p>
              </div>
            </div>
          </div>

          {/* Notas */}
          <div className="grid sm:grid-cols-3 gap-4 mb-6">
            <NotaSelector
              label="Fidelidade"
              value={notaFidelidade}
              onChange={setNotaFidelidade}
              description="1=ruim, 5=excelente"
            />
            <NotaSelector
              label="Clareza"
              value={notaClareza}
              onChange={setNotaClareza}
              description="1=confuso, 5=claro"
            />
            <NotaSelector
              label="Risco Clinico"
              value={notaRisco}
              onChange={setNotaRisco}
              description="1=alto, 5=baixo"
            />
          </div>

          {/* Comentarios */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                <MessageSquare className="w-4 h-4 inline mr-1" />
                Comentario Tecnico (opcional)
              </label>
              <textarea
                value={comentario}
                onChange={(e) => setComentario(e.target.value)}
                rows={3}
                className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder:text-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Observacoes sobre a qualidade da traducao..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Sugestao de Correcao (opcional)
              </label>
              <textarea
                value={sugestao}
                onChange={(e) => setSugestao(e.target.value)}
                rows={3}
                className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder:text-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Como a traducao poderia ser melhorada..."
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900">
          <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
            <Star className="w-4 h-4 text-amber-500" />
            Media: {((notaFidelidade + notaClareza + notaRisco) / 3).toFixed(1)}
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button
              variant="primary"
              onClick={handleSubmit}
              isLoading={submitting}
              leftIcon={<Send className="w-4 h-4" />}
            >
              Enviar Parecer
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
