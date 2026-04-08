// Enums
export type DocumentCategory = 'laudo' | 'receita' | 'saude_mental'
export type LaudoType = 'exame_sangue' | 'exame_imagem' | 'exame_urina' | 'biopsia' | 'outros'
export type ReceitaType = 'simples' | 'controlada' | 'antibiotico'
export type SaudeMentalType = 'antidepressivo' | 'ansiolitico' | 'laudo_psiquiatrico' | 'outros'

export type DocumentType = LaudoType | ReceitaType | SaudeMentalType

export type LLMProvider = 'claude' | 'openai' | 'gemini'

// Labels para o frontend
export const CATEGORY_LABELS: Record<DocumentCategory, string> = {
  laudo: 'Laudo/Exame',
  receita: 'Receita Médica',
  saude_mental: 'Saúde Mental',
}

export const PROVIDER_LABELS: Record<LLMProvider, string> = {
  claude: 'Claude 3.5 Sonnet (Anthropic)',
  openai: 'GPT-4o (OpenAI)',
  gemini: 'Gemini 1.5 Pro (Google)',
}

export const LAUDO_TYPE_LABELS: Record<LaudoType, string> = {
  exame_sangue: 'Exame de Sangue',
  exame_imagem: 'Exame de Imagem (Raio-X, Tomografia, etc)',
  exame_urina: 'Exame de Urina',
  biopsia: 'Biópsia/Anatomopatológico',
  outros: 'Outro tipo de laudo',
}

export const RECEITA_TYPE_LABELS: Record<ReceitaType, string> = {
  simples: 'Receita Simples',
  controlada: 'Receita Controlada',
  antibiotico: 'Receita de Antibiótico',
}

export const SAUDE_MENTAL_TYPE_LABELS: Record<SaudeMentalType, string> = {
  antidepressivo: 'Receita de Antidepressivo',
  ansiolitico: 'Receita de Ansiolítico',
  laudo_psiquiatrico: 'Laudo Psiquiátrico',
  outros: 'Outro documento de saúde mental',
}

// Request/Response types
export interface TranslateTextRequest {
  text: string
  category: DocumentCategory
  document_type: string
  provider?: LLMProvider
}

export interface TranslationResult {
  resumo: string
  detalhado: string
  entenda_facil: string
  glossario: Record<string, string>
  alertas: string[]
  is_saude_mental: boolean
  from_cache: boolean
  professional_authorship_detected: boolean
  professional_authorship_evidence: string[]
}

export interface EpidemiologyProcessingResult {
  success: boolean
  resumo?: string
  detalhado?: string
  entenda_facil?: string
  texto_traduzido?: string
  glossario?: Record<string, string>
  alertas?: string[]
  condicao_categoria?: string
  faixa_etaria?: string
  id?: string
  requer_confirmacao_localizacao: boolean
  from_cache: boolean
  documento_repetido?: boolean
  total_acessos?: number
  ultimo_acesso_em?: string
  error?: string
}

export interface TranslateResponse {
  success: boolean
  data: TranslationResult | null
  error: string | null
  anonymized_fields: string[]
}

export interface ValidationResult {
  is_valid: boolean
  document_type: string | null
  suggested_category: DocumentCategory | null
  message: string
  professional_authorship_detected: boolean
  professional_authorship_evidence: string[]
}

export interface ValidateResponse {
  success: boolean
  data: ValidationResult | null
  error: string | null
}

export interface UsageStatus {
  session_id: string
  translations_used: number
  translations_remaining: number
  translations_limit: number
  is_limit_reached: boolean
}

export interface UsageResponse {
  success: boolean
  data: UsageStatus | null
  error: string | null
}

export interface SupportQuote {
  quote: string
  author: string | null
}

export interface BreathingExercise {
  name: string
  description: string
  steps: string[]
}

export interface SupportResource {
  name: string
  description: string
  contact: string
  is_emergency: boolean
}

export interface SupportResponse {
  quotes: SupportQuote[]
  exercises: BreathingExercise[]
  resources: SupportResource[]
}

export type UserProfileType =
  | 'patient'
  | 'caregiver'
  | 'student'
  | 'health_professional'
  | 'researcher'
  | 'other'

export type AccountType = 'patient' | 'specialist'
export type ProfessionalRegistryType = 'CRM' | 'COREN' | 'CRO' | 'CRP' | 'CRF' | 'CREFITO' | 'CRN' | 'CRBM'
export type SpecialistVerificationStatus =
  | 'not_applicable'
  | 'pending'
  | 'verified'
  | 'rejected'

export interface AuthUser {
  id: string
  full_name: string
  email: string
  role: 'user' | 'specialist' | 'admin'
  account_type: AccountType
  profile_type: UserProfileType
  age: number | null
  city: string | null
  state: string | null
  institution: string | null
  specialty: string | null
  professional_registry_type: ProfessionalRegistryType | null
  professional_registry_number: string | null
  professional_registry_state: string | null
  specialist_verification_status: SpecialistVerificationStatus
  preferred_llm_provider: LLMProvider
  preferred_llm_model: string | null
  research_consent: boolean
  contact_consent: boolean
  created_at: string
}

export interface AuthPayload {
  token?: string
  user?: AuthUser
  logged_out?: boolean
}

export interface AuthResponse {
  success: boolean
  data: AuthPayload | null
  error: string | null
}

export interface RegisterRequest {
  full_name: string
  email: string
  password: string
  account_type: AccountType
  profile_type: UserProfileType
  age: number
  city: string
  state: string
  institution?: string
  specialty?: string
  professional_registry_type?: ProfessionalRegistryType
  professional_registry_number?: string
  professional_registry_state?: string
  terms_accepted: boolean
  privacy_accepted: boolean
  research_consent: boolean
  contact_consent: boolean
}

export interface LoginRequest {
  email: string
  password: string
}

export interface TranslationHistoryItem {
  id: string
  source: string
  input_type: string
  document_category: string | null
  document_type: string | null
  original_text: string | null
  original_image_base64: string | null
  original_image_media_type: string | null
  original_excerpt: string | null
  translated_summary: string
  result_payload: Record<string, unknown>
  total_accesses: number
  last_accessed_at: string
  created_at: string
}

export interface TranslationHistoryResponse {
  success: boolean
  data: TranslationHistoryItem[]
  error: string | null
}

export interface FileDuplicateCheckResponse {
  success: boolean
  duplicate: boolean
  history_item_id?: string | null
  translated_summary?: string | null
  created_at?: string | null
  error?: string | null
}
