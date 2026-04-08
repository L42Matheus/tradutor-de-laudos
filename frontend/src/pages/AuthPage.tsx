import { useState, type ChangeEvent, type FormEvent } from 'react'
import {
  ArrowRight,
  ChevronLeft,
  Lock,
  Mail,
  ShieldCheck,
  Stethoscope,
  User,
  UserCheck,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import type { AccountType, LoginRequest, RegisterRequest, UserProfileType } from '../types/api'

type AuthView = 'selection' | 'login' | 'register'

const PATIENT_PROFILE_OPTIONS: { value: UserProfileType; label: string }[] = [
  { value: 'patient', label: 'Paciente' },
  { value: 'caregiver', label: 'Cuidador(a)' },
  { value: 'student', label: 'Estudante' },
  { value: 'researcher', label: 'Pesquisador(a)' },
  { value: 'other', label: 'Outro' },
]

const ROLE_THEME: Record<
  AccountType,
  {
    label: string
    heading: string
    description: string
    icon: JSX.Element
    selectCardIconClass: string
    selectCardTextClass: string
    buttonClass: string
    buttonHoverClass: string
    buttonShadowClass: string
    focusClass: string
    linkClass: string
    subtlePanelClass: string
  }
> = {
  patient: {
    label: 'Paciente',
    heading: 'Sou paciente',
    description:
      'Acesse seus documentos, acompanhe seu historico e receba explicacoes mais claras sobre sua saude.',
    icon: <UserCheck className="h-6 w-6" />,
    selectCardIconClass:
      'bg-blue-100 text-blue-600 group-hover:bg-blue-600 group-hover:text-white dark:bg-blue-900/40 dark:text-blue-400 dark:group-hover:bg-blue-600',
    selectCardTextClass: 'text-blue-600 dark:text-blue-400',
    buttonClass: 'bg-blue-600 text-white',
    buttonHoverClass: 'hover:bg-blue-700 dark:hover:bg-blue-500',
    buttonShadowClass: 'shadow-blue-300/50 dark:shadow-blue-950/40',
    focusClass: 'focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 dark:focus:ring-blue-500/30',
    linkClass: 'text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300',
    subtlePanelClass: 'bg-blue-50 border-blue-200 dark:bg-blue-950/30 dark:border-blue-800/50',
  },
  specialist: {
    label: 'Especialista',
    heading: 'Sou especialista',
    description:
      'Revise laudos, valide a traducao e gere feedback tecnico para medir o impacto da LLM e dos prompts.',
    icon: <ShieldCheck className="h-6 w-6" />,
    selectCardIconClass:
      'bg-emerald-100 text-emerald-600 group-hover:bg-emerald-600 group-hover:text-white dark:bg-emerald-900/40 dark:text-emerald-400 dark:group-hover:bg-emerald-600',
    selectCardTextClass: 'text-emerald-600 dark:text-emerald-400',
    buttonClass: 'bg-emerald-600 text-white',
    buttonHoverClass: 'hover:bg-emerald-700 dark:hover:bg-emerald-500',
    buttonShadowClass: 'shadow-emerald-300/50 dark:shadow-emerald-950/40',
    focusClass:
      'focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500 dark:focus:ring-emerald-500/30',
    linkClass:
      'text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300',
    subtlePanelClass:
      'bg-emerald-50 border-emerald-200 dark:bg-emerald-950/30 dark:border-emerald-800/50',
  },
}

function Field({
  label,
  children,
  hint,
}: {
  label: string
  children: React.ReactNode
  hint?: React.ReactNode
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between px-1">
        <label className="text-sm font-semibold text-slate-700 dark:text-gray-200">{label}</label>
        {hint}
      </div>
      {children}
    </div>
  )
}

function FormInput({
  icon,
  focusClass,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & {
  icon?: React.ReactNode
  focusClass: string
}) {
  return (
    <div className="relative">
      {icon && (
        <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 dark:text-gray-500">
          {icon}
        </span>
      )}
      <input
        {...props}
        className={`w-full rounded-xl border border-slate-200 bg-slate-50 py-3.5 pr-4 text-slate-900 outline-none transition placeholder:text-slate-400 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:placeholder:text-gray-500 ${focusClass} ${
          icon ? 'pl-12' : 'pl-4'
        } ${props.className || ''}`}
      />
    </div>
  )
}

function FormSelect({
  focusClass,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement> & { focusClass: string }) {
  return (
    <select
      {...props}
      className={`w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3.5 text-slate-900 outline-none transition dark:border-gray-700 dark:bg-gray-900 dark:text-white ${focusClass} ${
        props.className || ''
      }`}
    />
  )
}

export function AuthPage() {
  const { login, register, error } = useAuth()
  const [view, setView] = useState<AuthView>('selection')
  const [accountType, setAccountType] = useState<AccountType>('patient')
  const [loading, setLoading] = useState(false)

  const [loginForm, setLoginForm] = useState<LoginRequest>({
    email: '',
    password: '',
  })

  const [registerForm, setRegisterForm] = useState<RegisterRequest>({
    full_name: '',
    email: '',
    password: '',
    account_type: 'patient',
    profile_type: 'patient',
    age: 0,
    city: '',
    state: '',
    institution: '',
    specialty: '',
    professional_registry_type: 'CRM',
    professional_registry_number: '',
    professional_registry_state: '',
    terms_accepted: false,
    privacy_accepted: false,
    research_consent: true,
    contact_consent: false,
  })

  const roleTheme = ROLE_THEME[accountType]
  const isSpecialist = accountType === 'specialist'

  const handleSelectRole = (role: AccountType) => {
    setAccountType(role)
    setRegisterForm((current) => ({
      ...current,
      account_type: role,
      profile_type: role === 'specialist' ? 'health_professional' : 'patient',
      specialty: role === 'specialist' ? current.specialty || '' : '',
      professional_registry_type: role === 'specialist' ? 'CRM' : undefined,
      professional_registry_number:
        role === 'specialist' ? current.professional_registry_number || '' : '',
      professional_registry_state:
        role === 'specialist' ? current.professional_registry_state || '' : '',
    }))
    setView('login')
  }

  const handleBack = () => {
    setView('selection')
  }

  const handleLoginChange =
    (field: keyof LoginRequest) => (event: ChangeEvent<HTMLInputElement>) => {
      setLoginForm((current) => ({ ...current, [field]: event.target.value }))
    }

  const handleRegisterChange =
    (field: keyof RegisterRequest) =>
    (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const value =
        event.target instanceof HTMLInputElement && event.target.type === 'checkbox'
          ? event.target.checked
          : event.target.value

      setRegisterForm((current) => ({ ...current, [field]: value }))
    }

  const handleLoginSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    try {
      await login(loginForm)
    } finally {
      setLoading(false)
    }
  }

  const handleRegisterSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    try {
      await register(registerForm)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800 flex flex-col items-center justify-center p-4 font-sans transition-colors">
      {view === 'selection' ? (
        <div className="w-full max-w-4xl flex flex-col items-center">
          <div className="mb-12 text-center">
            <h1 className="mb-2 text-4xl font-bold tracking-tight text-blue-600 dark:text-primary-400">
              Traduz <span className="text-emerald-500">Saude</span>
            </h1>
            <p className="text-lg text-slate-500 dark:text-gray-400">
              Escolha como deseja acessar a plataforma
            </p>
          </div>

          <div className="grid w-full grid-cols-1 gap-8 md:grid-cols-2">
            {(['patient', 'specialist'] as AccountType[]).map((role) => (
              <button
                key={role}
                type="button"
                onClick={() => handleSelectRole(role)}
                className="group relative flex flex-col items-center rounded-3xl border border-slate-100 bg-white p-8 text-center shadow-xl shadow-slate-200 transition-all hover:-translate-y-1 hover:shadow-2xl hover:shadow-slate-300/80 dark:border-gray-700 dark:bg-gray-800 dark:shadow-black/20 dark:hover:border-gray-600 dark:hover:shadow-black/30"
              >
                <div
                  className={`mb-6 flex h-20 w-20 items-center justify-center rounded-2xl transition-colors duration-300 ${ROLE_THEME[role].selectCardIconClass}`}
                >
                  {role === 'patient' ? (
                    <User className="h-10 w-10" />
                  ) : (
                    <Stethoscope className="h-10 w-10" />
                  )}
                </div>
                <h2 className="mb-3 text-2xl font-bold text-slate-800 dark:text-white">
                  {ROLE_THEME[role].heading}
                </h2>
                <p className="mb-8 leading-relaxed text-slate-500 dark:text-gray-400">
                  {ROLE_THEME[role].description}
                </p>
                <div
                  className={`mt-auto flex items-center font-semibold transition-all group-hover:gap-2 ${ROLE_THEME[role].selectCardTextClass}`}
                >
                  {role === 'patient' ? 'Acessar minha conta' : 'Portal do especialista'}
                  <ArrowRight className="ml-2 h-5 w-5" />
                </div>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="w-full max-w-md transition-all">
          <div
            className={`mb-8 flex items-center justify-between rounded-2xl border bg-white p-4 shadow-sm dark:bg-gray-800 ${roleTheme.subtlePanelClass}`}
          >
            <div className="flex items-center gap-3">
              <div
                className={`rounded-lg p-2 ${isSpecialist ? 'bg-emerald-50 dark:bg-emerald-950/40' : 'bg-blue-50 dark:bg-blue-950/40'}`}
              >
                {roleTheme.icon}
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-slate-400 dark:text-gray-500">
                  Acesso
                </p>
                <p className="font-bold text-slate-700 dark:text-white">{roleTheme.label}</p>
              </div>
            </div>
            <button
              type="button"
              onClick={handleBack}
              className={`flex items-center gap-1 text-sm font-semibold transition-colors ${roleTheme.linkClass}`}
            >
              Trocar <ChevronLeft className="h-4 w-4" />
            </button>
          </div>

          <div className="rounded-3xl border border-slate-100 bg-white p-8 shadow-2xl shadow-slate-200 dark:border-gray-700 dark:bg-gray-800 dark:shadow-black/30">
            <div className="mb-8">
              <h2 className="mb-2 text-3xl font-bold text-slate-800 dark:text-white">
                {view === 'login' ? 'Bem-vindo' : 'Criar conta'}
              </h2>
              <p className="text-slate-500 dark:text-gray-400">
                {view === 'login'
                  ? isSpecialist
                    ? 'Entre com suas credenciais de especialista'
                    : 'Entre para ver seus documentos e historico'
                  : isSpecialist
                    ? 'Cadastre seu acesso profissional para validacao clinica'
                    : 'Crie sua conta para traduzir documentos e acompanhar seu historico'}
              </p>
            </div>

            {error && (
              <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-600 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300">
                {error}
              </div>
            )}

            {view === 'login' ? (
              <form className="space-y-6" onSubmit={handleLoginSubmit}>
                <Field label="E-mail">
                  <FormInput
                    type="email"
                    placeholder="seu@email.com"
                    value={loginForm.email}
                    onChange={handleLoginChange('email')}
                    focusClass={roleTheme.focusClass}
                    icon={<Mail className="h-5 w-5" />}
                  />
                </Field>

                <Field
                  label="Senha"
                  hint={
                    <button
                      type="button"
                      className={`text-xs font-semibold transition-colors ${roleTheme.linkClass}`}
                    >
                      Esqueceu a senha?
                    </button>
                  }
                >
                  <FormInput
                    type="password"
                    placeholder="Digite sua senha"
                    value={loginForm.password}
                    onChange={handleLoginChange('password')}
                    focusClass={roleTheme.focusClass}
                    icon={<Lock className="h-5 w-5" />}
                  />
                </Field>

                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full rounded-xl py-4 font-bold transition-all active:scale-[0.98] disabled:opacity-60 ${roleTheme.buttonClass} ${roleTheme.buttonHoverClass} shadow-lg ${roleTheme.buttonShadowClass}`}
                >
                  {loading
                    ? 'Entrando...'
                    : isSpecialist
                      ? 'Entrar no Portal'
                      : 'Acessar minha conta'}
                </button>

                <div className="border-t border-slate-100 pt-8 text-center dark:border-gray-700">
                  <p className="text-sm text-slate-500 dark:text-gray-400">
                    {isSpecialist
                      ? 'Ainda nao e um especialista parceiro?'
                      : 'Ainda nao tem uma conta?'}
                  </p>
                  <button
                    type="button"
                    onClick={() => setView('register')}
                    className={`mt-2 font-bold transition-colors ${roleTheme.linkClass}`}
                  >
                    {isSpecialist ? 'Solicitar Cadastro' : 'Criar conta agora'}
                  </button>
                </div>
              </form>
            ) : (
              <form className="space-y-5" onSubmit={handleRegisterSubmit}>
                <Field label="Nome completo">
                  <FormInput
                    type="text"
                    placeholder="Seu nome completo"
                    value={registerForm.full_name}
                    onChange={handleRegisterChange('full_name')}
                    focusClass={roleTheme.focusClass}
                    icon={<User className="h-5 w-5" />}
                  />
                </Field>

                <Field label="E-mail">
                  <FormInput
                    type="email"
                    placeholder="seu@email.com"
                    value={registerForm.email}
                    onChange={handleRegisterChange('email')}
                    focusClass={roleTheme.focusClass}
                    icon={<Mail className="h-5 w-5" />}
                  />
                </Field>

                <Field label="Senha">
                  <FormInput
                    type="password"
                    placeholder="Crie uma senha"
                    value={registerForm.password}
                    onChange={handleRegisterChange('password')}
                    focusClass={roleTheme.focusClass}
                    icon={<Lock className="h-5 w-5" />}
                  />
                </Field>

                <div className="grid grid-cols-[120px,1fr,96px] gap-3">
                  <Field label="Idade">
                    <FormInput
                      type="number"
                      min={0}
                      max={120}
                      placeholder="30"
                      value={registerForm.age || ''}
                      onChange={(event) =>
                        setRegisterForm((current) => ({
                          ...current,
                          age: Number(event.target.value),
                        }))
                      }
                      focusClass={roleTheme.focusClass}
                    />
                  </Field>

                  <Field label="Cidade">
                    <FormInput
                      type="text"
                      placeholder="Sua cidade"
                      value={registerForm.city}
                      onChange={handleRegisterChange('city')}
                      focusClass={roleTheme.focusClass}
                    />
                  </Field>

                  <Field label="UF">
                    <FormInput
                      type="text"
                      maxLength={2}
                      placeholder="PA"
                      value={registerForm.state}
                      onChange={(event) =>
                        setRegisterForm((current) => ({
                          ...current,
                          state: event.target.value.toUpperCase(),
                        }))
                      }
                      focusClass={roleTheme.focusClass}
                      className="uppercase"
                    />
                  </Field>
                </div>

                {isSpecialist ? (
                  <>
                    <Field label="Especialidade">
                      <FormInput
                        type="text"
                        placeholder="Ex: Radiologia"
                        value={registerForm.specialty}
                        onChange={handleRegisterChange('specialty')}
                        focusClass={roleTheme.focusClass}
                      />
                    </Field>

                    <div className="grid grid-cols-[1fr,96px] gap-3">
                      <Field label="Registro">
                        <FormInput
                          type="text"
                          value={registerForm.professional_registry_type}
                          readOnly
                          focusClass={roleTheme.focusClass}
                          className="font-semibold text-slate-500 dark:text-gray-400"
                        />
                      </Field>
                      <Field label="UF">
                        <FormInput
                          type="text"
                          maxLength={2}
                          placeholder="PB"
                          value={registerForm.professional_registry_state}
                          onChange={(event) =>
                            setRegisterForm((current) => ({
                              ...current,
                              professional_registry_state: event.target.value.toUpperCase(),
                            }))
                          }
                          focusClass={roleTheme.focusClass}
                          className="uppercase"
                        />
                      </Field>
                    </div>

                    <Field label="Numero do CRM">
                      <FormInput
                        type="text"
                        placeholder="123456"
                        value={registerForm.professional_registry_number}
                        onChange={handleRegisterChange('professional_registry_number')}
                        focusClass={roleTheme.focusClass}
                      />
                    </Field>
                  </>
                ) : (
                  <Field label="Perfil">
                    <FormSelect
                      value={registerForm.profile_type}
                      onChange={handleRegisterChange('profile_type')}
                      focusClass={roleTheme.focusClass}
                    >
                      {PATIENT_PROFILE_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </FormSelect>
                  </Field>
                )}

                <Field label="Instituicao">
                  <FormInput
                    type="text"
                    placeholder="Opcional"
                    value={registerForm.institution}
                    onChange={handleRegisterChange('institution')}
                    focusClass={roleTheme.focusClass}
                  />
                </Field>

                <div className="space-y-3 rounded-xl border border-slate-100 bg-slate-50 p-4 text-sm text-slate-600 dark:border-gray-700 dark:bg-gray-900/50 dark:text-gray-300">
                  <label className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={registerForm.terms_accepted}
                      onChange={handleRegisterChange('terms_accepted')}
                      className="mt-1"
                    />
                    <span>
                      Aceito os termos de uso e reconheco que o sistema nao substitui avaliacao medica.
                    </span>
                  </label>
                  <label className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={registerForm.privacy_accepted}
                      onChange={handleRegisterChange('privacy_accepted')}
                      className="mt-1"
                    />
                    <span>
                      Aceito a politica de privacidade e o tratamento dos dados necessarios para uso da plataforma.
                    </span>
                  </label>
                  <label className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={registerForm.research_consent}
                      onChange={handleRegisterChange('research_consent')}
                      className="mt-1"
                    />
                    <span>
                      Autorizo o uso anonimizado dos dados para pesquisa vinculada ao projeto.
                    </span>
                  </label>
                  <label className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={registerForm.contact_consent}
                      onChange={handleRegisterChange('contact_consent')}
                      className="mt-1"
                    />
                    <span>
                      Aceito contato futuro para estudos, validacoes e evolucao do produto.
                    </span>
                  </label>
                </div>

                {isSpecialist && (
                  <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700 dark:border-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-300">
                    O acesso do especialista entra com verificacao pendente a partir do CRM, UF e especialidade informados.
                  </div>
                )}

                <button
                  type="submit"
                  disabled={
                    loading || !registerForm.terms_accepted || !registerForm.privacy_accepted
                  }
                  className={`w-full rounded-xl py-4 font-bold transition-all active:scale-[0.98] disabled:opacity-60 ${roleTheme.buttonClass} ${roleTheme.buttonHoverClass} shadow-lg ${roleTheme.buttonShadowClass}`}
                >
                  {loading ? 'Criando...' : 'Criar conta'}
                </button>

                <div className="border-t border-slate-100 pt-6 text-center dark:border-gray-700">
                  <p className="text-sm text-slate-500 dark:text-gray-400">Ja tem conta?</p>
                  <button
                    type="button"
                    onClick={() => setView('login')}
                    className={`mt-2 font-bold transition-colors ${roleTheme.linkClass}`}
                  >
                    Entrar agora
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
