import { Heart, Shield, AlertTriangle } from 'lucide-react'

export function Footer() {
  return (
    <footer className="bg-gray-100 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
      <div className="container mx-auto px-4 py-6">
        {/* Aviso importante */}
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="text-yellow-600 dark:text-yellow-400 flex-shrink-0" size={20} />
            <p className="text-sm text-yellow-800 dark:text-yellow-200">
              <strong>Importante:</strong> Este serviço tem fins educativos e não substitui
              consulta médica profissional. Sempre consulte um profissional de saúde para
              interpretação oficial dos seus exames.
            </p>
          </div>
        </div>

        {/* Informações */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center gap-2">
            <Shield size={16} />
            <span>Seus dados são anonimizados e não são armazenados</span>
          </div>

          <div className="flex items-center gap-2">
            <span>Feito com</span>
            <Heart size={16} className="text-red-500" fill="currentColor" />
            <span>para democratizar a saúde</span>
          </div>
        </div>

        {/* Copyright */}
        <div className="text-center mt-4 text-xs text-gray-500 dark:text-gray-500">
          &copy; {new Date().getFullYear()} Traduz Saúde. Todos os direitos reservados.
        </div>
      </div>
    </footer>
  )
}
