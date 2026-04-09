import { useState, type FormEvent } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Lock, CheckCircle2, AlertCircle, ArrowLeft } from 'lucide-react'
import { confirmPasswordReset } from '../services/api'

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!token) {
      setError('Token de recuperação ausente.')
      return
    }

    if (password !== confirmPassword) {
      setError('As senhas não coincidem.')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const response = await confirmPasswordReset(token, password)
      if (response.success) {
        setSuccess(true)
      } else {
        setError(response.error || 'Erro ao redefinir senha.')
      }
    } catch (err) {
      setError('Erro ao processar solicitação.')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-xl text-center">
          <div className="mb-6 flex justify-center">
            <div className="rounded-full bg-emerald-100 p-3 dark:bg-emerald-900/30">
              <CheckCircle2 className="h-12 w-12 text-emerald-600 dark:text-emerald-400" />
            </div>
          </div>
          <h2 className="mb-2 text-2xl font-bold text-slate-800 dark:text-white">Senha alterada!</h2>
          <p className="mb-8 text-slate-500 dark:text-gray-400">
            Sua nova senha foi salva com sucesso. Você já pode acessar sua conta.
          </p>
          <a
            href="/login"
            className="block w-full rounded-xl bg-blue-600 py-4 font-bold text-white hover:bg-blue-700 transition-all shadow-lg shadow-blue-300/50"
          >
            Ir para o Login
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex items-center justify-center p-4 font-sans">
      <div className="w-full max-w-md bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-xl">
        <div className="mb-8">
          <h2 className="mb-2 text-3xl font-bold text-slate-800 dark:text-white">Nova senha</h2>
          <p className="text-slate-500 dark:text-gray-400">
            Crie uma senha forte para sua conta
          </p>
        </div>

        {!token && (
          <div className="mb-6 flex items-center gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700 dark:border-amber-800 dark:bg-amber-900/20 dark:text-amber-300">
            <AlertCircle className="h-5 w-5 shrink-0" />
            <span>Link de recuperação inválido ou quebrado. Por favor, solicite um novo link.</span>
          </div>
        )}

        {error && (
          <div className="mb-6 flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-600 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300">
            <AlertCircle className="h-5 w-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700 dark:text-gray-200 px-1">Nova senha</label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
                <Lock className="h-5 w-5" />
              </span>
              <input
                type="password"
                required
                minLength={8}
                placeholder="No mínimo 8 caracteres"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3.5 pl-12 pr-4 text-slate-900 outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700 dark:text-gray-200 px-1">Confirmar senha</label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
                <Lock className="h-5 w-5" />
              </span>
              <input
                type="password"
                required
                placeholder="Repita a nova senha"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3.5 pl-12 pr-4 text-slate-900 outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !token}
            className="w-full rounded-xl bg-blue-600 py-4 font-bold text-white transition-all hover:bg-blue-700 active:scale-[0.98] disabled:opacity-60 shadow-lg shadow-blue-300/50 dark:shadow-blue-950/40"
          >
            {loading ? 'Salvando...' : 'Salvar nova senha'}
          </button>

          <div className="text-center">
            <a
              href="/login"
              className="inline-flex items-center gap-2 text-sm font-semibold text-blue-600 hover:text-blue-700 dark:text-blue-400"
            >
              <ArrowLeft className="h-4 w-4" />
              Voltar para o Login
            </a>
          </div>
        </form>
      </div>
    </div>
  )
}
