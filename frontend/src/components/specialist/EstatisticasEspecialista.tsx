import { useState, useEffect } from 'react'
import { BarChart3, CheckCircle, Target, Shield, Star, TrendingUp } from 'lucide-react'
import { Card } from '../ui/Card'
import api from '../../services/api'

interface Estatisticas {
  success: boolean
  total_revisoes: number
  media_fidelidade: number
  media_clareza: number
  media_risco: number
  media_geral: number
}

export function EstatisticasEspecialista() {
  const [stats, setStats] = useState<Estatisticas | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const carregar = async () => {
      try {
        const response = await api.get<Estatisticas>('/revisao/estatisticas')
        setStats(response.data)
      } catch (err) {
        console.error('Erro ao carregar estatisticas:', err)
      } finally {
        setLoading(false)
      }
    }
    carregar()
  }, [])

  const StatCard = ({
    icon,
    label,
    value,
    color,
    subtitle
  }: {
    icon: React.ReactNode
    label: string
    value: string | number
    color: string
    subtitle?: string
  }) => (
    <div className={`p-5 rounded-xl border ${color}`}>
      <div className="flex items-center gap-3 mb-3">
        {icon}
        <span className="text-sm font-medium text-slate-600 dark:text-slate-400">{label}</span>
      </div>
      <p className="text-3xl font-bold text-slate-900 dark:text-white">{value}</p>
      {subtitle && (
        <p className="text-xs text-slate-500 dark:text-slate-500 mt-1">{subtitle}</p>
      )}
    </div>
  )

  const NotaBar = ({
    label,
    value,
    maxValue = 5
  }: {
    label: string
    value: number
    maxValue?: number
  }) => {
    const percentage = (value / maxValue) * 100
    const color = value >= 4 ? 'bg-emerald-500' : value >= 3 ? 'bg-amber-500' : 'bg-red-500'

    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-600 dark:text-slate-400">{label}</span>
          <span className="font-semibold text-slate-900 dark:text-white">{value.toFixed(1)}</span>
        </div>
        <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
          <div
            className={`h-full ${color} rounded-full transition-all duration-500`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <Card>
        <div className="flex items-center justify-center py-12 text-slate-500 dark:text-slate-400">
          Carregando estatisticas...
        </div>
      </Card>
    )
  }

  if (!stats || stats.total_revisoes === 0) {
    return (
      <Card>
        <div className="text-center py-12">
          <BarChart3 className="w-16 h-16 mx-auto text-slate-300 dark:text-slate-600 mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            Sem estatisticas ainda
          </h3>
          <p className="text-slate-500 dark:text-slate-400">
            Suas metricas aparecerao aqui apos realizar a primeira revisao
          </p>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Cards de resumo */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<CheckCircle className="w-5 h-5 text-emerald-500" />}
          label="Revisoes Realizadas"
          value={stats.total_revisoes}
          color="border-emerald-200 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-900/20"
          subtitle="laudos revisados"
        />
        <StatCard
          icon={<Star className="w-5 h-5 text-amber-500" />}
          label="Media Geral"
          value={stats.media_geral.toFixed(1)}
          color="border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-900/20"
          subtitle="de 5.0"
        />
        <StatCard
          icon={<Target className="w-5 h-5 text-blue-500" />}
          label="Fidelidade"
          value={stats.media_fidelidade.toFixed(1)}
          color="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/20"
          subtitle="preservacao dos achados"
        />
        <StatCard
          icon={<Shield className="w-5 h-5 text-purple-500" />}
          label="Seguranca"
          value={stats.media_risco.toFixed(1)}
          color="border-purple-200 bg-purple-50 dark:border-purple-800 dark:bg-purple-900/20"
          subtitle="baixo risco clinico"
        />
      </div>

      {/* Grafico de barras */}
      <Card>
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/50">
            <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
              Detalhamento das Notas
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Media por criterio de avaliacao
            </p>
          </div>
        </div>

        <div className="space-y-5">
          <NotaBar label="Fidelidade ao Laudo Original" value={stats.media_fidelidade} />
          <NotaBar label="Clareza para o Paciente" value={stats.media_clareza} />
          <NotaBar label="Seguranca Clinica (5=baixo risco)" value={stats.media_risco} />
        </div>

        <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-600 dark:text-slate-400">
              Impacto das suas revisoes no sistema
            </span>
            <span className="text-sm font-medium text-emerald-600 dark:text-emerald-400">
              Contribuindo para melhoria dos prompts
            </span>
          </div>
        </div>
      </Card>
    </div>
  )
}
