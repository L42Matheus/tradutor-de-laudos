// Enums
export type DocumentCategory = 'laudo' | 'receita' | 'saude_mental'
export type LaudoType = 'exame_sangue' | 'exame_imagem' | 'exame_urina' | 'biopsia' | 'outros'
export type ReceitaType = 'simples' | 'controlada' | 'antibiotico'
export type SaudeMentalType = 'antidepressivo' | 'ansiolitico' | 'laudo_psiquiatrico' | 'outros'

export type DocumentType = LaudoType | ReceitaType | SaudeMentalType

// Labels para o frontend
export const CATEGORY_LABELS: Record<DocumentCategory, string> = {
  laudo: 'Laudo/Exame',
  receita: 'Receita Médica',
  saude_mental: 'Saúde Mental',
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
