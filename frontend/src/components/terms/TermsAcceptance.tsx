import { useState } from 'react'
import { Shield, FileText, AlertTriangle, Check } from 'lucide-react'
import { Button } from '../ui/Button'
import { Card } from '../ui/Card'

interface TermsAcceptanceProps {
  onAccept: () => void
}

export function TermsAcceptance({ onAccept }: TermsAcceptanceProps) {
  const [agreed, setAgreed] = useState(false)

  return (
    <div className="max-w-2xl mx-auto">
      <Card className="text-center">
        <div className="mb-6">
          <div className="w-16 h-16 mx-auto bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center mb-4">
            <Shield className="text-primary-600 dark:text-primary-400" size={32} />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Bem-vindo ao Traduz Saúde
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Transformamos documentos médicos em linguagem que todos entendem
          </p>
        </div>

        {/* Termos de uso */}
        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 mb-6 text-left">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <FileText size={18} />
            Termos de Uso e Privacidade
          </h3>

          <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex gap-2">
              <Check size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
              <p>
                <strong>Fins educativos:</strong> Este serviço tem objetivo educacional e
                NÃO substitui consulta médica profissional.
              </p>
            </div>

            <div className="flex gap-2">
              <Check size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
              <p>
                <strong>Privacidade:</strong> Seus documentos são processados de forma anônima.
                Dados pessoais (CPF, nome, etc.) são removidos automaticamente.
              </p>
            </div>

            <div className="flex gap-2">
              <Check size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
              <p>
                <strong>Sem armazenamento:</strong> Não guardamos seus documentos.
                Todas as informações são descartadas após o processamento.
              </p>
            </div>

            <div className="flex gap-2">
              <Check size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
              <p>
                <strong>LGPD:</strong> Estamos em conformidade com a Lei Geral de
                Proteção de Dados.
              </p>
            </div>
          </div>
        </div>

        {/* Aviso importante */}
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-3 text-left">
            <AlertTriangle className="text-yellow-600 dark:text-yellow-400 flex-shrink-0" size={20} />
            <p className="text-sm text-yellow-800 dark:text-yellow-200">
              <strong>Importante:</strong> Sempre consulte um profissional de saúde para
              interpretação oficial dos seus exames e condutas médicas.
            </p>
          </div>
        </div>

        {/* Checkbox de concordância */}
        <label className="flex items-center justify-center gap-3 mb-6 cursor-pointer">
          <input
            type="checkbox"
            checked={agreed}
            onChange={(e) => setAgreed(e.target.checked)}
            className="w-5 h-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-gray-700 dark:text-gray-300">
            Li e concordo com os termos de uso e política de privacidade
          </span>
        </label>

        {/* Botão de aceitar */}
        <Button
          onClick={onAccept}
          disabled={!agreed}
          size="lg"
          className="w-full sm:w-auto"
        >
          Continuar para o Traduz Saúde
        </Button>
      </Card>
    </div>
  )
}
