import { useState, useEffect } from 'react'
import { MapPin, X } from 'lucide-react'
import { Button } from '../ui/Button'
import { listarEstados, listarMunicipios, type Estado, type Municipio } from '../../services/api'

interface ConfirmacaoLocalizacaoProps {
  onConfirmar: (municipio: string, estado: string, municipioIbgeId?: string) => void
  onPular: () => void
  isLoading?: boolean
}

export function ConfirmacaoLocalizacao({
  onConfirmar,
  onPular,
  isLoading = false,
}: ConfirmacaoLocalizacaoProps) {
  const [estados, setEstados] = useState<Estado[]>([])
  const [municipios, setMunicipios] = useState<Municipio[]>([])
  const [estadoSelecionado, setEstadoSelecionado] = useState('')
  const [municipioSelecionado, setMunicipioSelecionado] = useState('')
  const [carregandoEstados, setCarregandoEstados] = useState(true)
  const [carregandoMunicipios, setCarregandoMunicipios] = useState(false)
  const [erroLocalizacao, setErroLocalizacao] = useState<string | null>(null)

  useEffect(() => {
    const carregarEstados = async () => {
      try {
        setErroLocalizacao(null)
        const response = await listarEstados()
        if (response.success) {
          setEstados(response.data)
        } else {
          setErroLocalizacao('Nao foi possivel carregar os estados.')
        }
      } catch (error) {
        console.error('Erro ao carregar estados:', error)
        setErroLocalizacao('Nao foi possivel carregar os estados.')
      } finally {
        setCarregandoEstados(false)
      }
    }

    carregarEstados()
  }, [])

  useEffect(() => {
    if (!estadoSelecionado) {
      setMunicipios([])
      setMunicipioSelecionado('')
      return
    }

    const carregarMunicipios = async () => {
      setCarregandoMunicipios(true)
      setMunicipioSelecionado('')
      try {
        setErroLocalizacao(null)
        const response = await listarMunicipios(estadoSelecionado)
        if (response.success) {
          setMunicipios(response.data)
          if (response.data.length === 0) {
            setErroLocalizacao('Nenhum municipio foi retornado para este estado.')
          }
        } else {
          setMunicipios([])
          setErroLocalizacao('Nao foi possivel carregar os municipios.')
        }
      } catch (error) {
        console.error('Erro ao carregar municipios:', error)
        setMunicipios([])
        setErroLocalizacao('Nao foi possivel carregar os municipios.')
      } finally {
        setCarregandoMunicipios(false)
      }
    }

    carregarMunicipios()
  }, [estadoSelecionado])

  const handleConfirmar = () => {
    if (municipioSelecionado && estadoSelecionado) {
      const municipio = municipios.find((m) => m.id === municipioSelecionado)
      if (municipio) {
        onConfirmar(municipio.nome, estadoSelecionado, municipio.id)
      }
    }
  }

  return (
    <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <MapPin className="w-5 h-5 text-amber-600 dark:text-amber-400" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-medium text-amber-800 dark:text-amber-200">
            Confirme sua localização
          </h3>
          <p className="mt-1 text-sm text-amber-700 dark:text-amber-300">
            Não conseguimos identificar a localização automaticamente. Por favor, informe o
            município onde o laudo foi emitido para contribuir com dados epidemiológicos
            anonimizados.
          </p>

          <div className="mt-4 space-y-3">
            <div>
              <label
                htmlFor="estado"
                className="block text-sm font-medium text-amber-800 dark:text-amber-200 mb-1"
              >
                Estado
              </label>
              <select
                id="estado"
                value={estadoSelecionado}
                onChange={(e) => setEstadoSelecionado(e.target.value)}
                disabled={carregandoEstados || isLoading}
                className="w-full px-3 py-2 border border-amber-300 dark:border-amber-700 rounded-md
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-amber-500 focus:border-transparent
                           disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="">
                  {carregandoEstados ? 'Carregando...' : 'Selecione o estado'}
                </option>
                {estados.map((estado) => (
                  <option key={estado.sigla} value={estado.sigla}>
                    {estado.nome} ({estado.sigla})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                htmlFor="municipio"
                className="block text-sm font-medium text-amber-800 dark:text-amber-200 mb-1"
              >
                Município
              </label>
              <select
                id="municipio"
                value={municipioSelecionado}
                onChange={(e) => setMunicipioSelecionado(e.target.value)}
                disabled={!estadoSelecionado || carregandoMunicipios || isLoading}
                className="w-full px-3 py-2 border border-amber-300 dark:border-amber-700 rounded-md
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-amber-500 focus:border-transparent
                           disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="">
                  {carregandoMunicipios
                    ? 'Carregando...'
                    : estadoSelecionado
                      ? 'Selecione o município'
                      : 'Selecione um estado primeiro'}
                </option>
                {municipios.map((municipio) => (
                  <option key={municipio.id} value={municipio.id}>
                    {municipio.nome}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {erroLocalizacao && (
            <p className="mt-3 text-sm text-red-600 dark:text-red-400">{erroLocalizacao}</p>
          )}

          <div className="mt-4 flex gap-3">
            <Button
              variant="primary"
              size="sm"
              onClick={handleConfirmar}
              disabled={!municipioSelecionado || isLoading}
              isLoading={isLoading}
              leftIcon={<MapPin className="w-4 h-4" />}
            >
              Confirmar
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onPular}
              disabled={isLoading}
              leftIcon={<X className="w-4 h-4" />}
            >
              Pular
            </Button>
          </div>

          <p className="mt-3 text-xs text-amber-600 dark:text-amber-400">
            Esta informação é usada apenas para fins de pesquisa epidemiológica. Nenhum dado
            pessoal é armazenado.
          </p>
        </div>
      </div>
    </div>
  )
}
