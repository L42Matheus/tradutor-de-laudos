import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { translateText, translateFile, validateText, validateFile } from '../services/api'
import { useUsage } from '../context/UsageContext'
import type { DocumentCategory, TranslationResult } from '../types/api'

interface UseTranslateOptions {
  onSuccess?: (result: TranslationResult) => void
  onError?: (error: Error) => void
}

export function useTranslate(options?: UseTranslateOptions) {
  const { canTranslate, incrementTranslation } = useUsage()
  const [anonymizedFields, setAnonymizedFields] = useState<string[]>([])

  const translateTextMutation = useMutation({
    mutationFn: async ({
      text,
      category,
      documentType,
    }: {
      text: string
      category: DocumentCategory
      documentType: string
    }) => {
      if (!canTranslate) {
        throw new Error('Limite de traduções atingido')
      }

      const response = await translateText({
        text,
        category,
        document_type: documentType,
      })

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Erro ao traduzir documento')
      }

      await incrementTranslation()
      setAnonymizedFields(response.anonymized_fields)

      return response.data
    },
    onSuccess: options?.onSuccess,
    onError: options?.onError,
  })

  const translateFileMutation = useMutation({
    mutationFn: async ({
      file,
      category,
      documentType,
    }: {
      file: File
      category: DocumentCategory
      documentType: string
    }) => {
      if (!canTranslate) {
        throw new Error('Limite de traduções atingido')
      }

      const response = await translateFile(file, category, documentType)

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Erro ao traduzir arquivo')
      }

      await incrementTranslation()
      setAnonymizedFields(response.anonymized_fields)

      return response.data
    },
    onSuccess: options?.onSuccess,
    onError: options?.onError,
  })

  const validateTextMutation = useMutation({
    mutationFn: async (text: string) => {
      const response = await validateText(text)

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Erro ao validar documento')
      }

      return response.data
    },
  })

  const validateFileMutation = useMutation({
    mutationFn: async (file: File) => {
      const response = await validateFile(file)

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Erro ao validar arquivo')
      }

      return response.data
    },
  })

  return {
    // Translate functions
    translateText: translateTextMutation.mutateAsync,
    translateFile: translateFileMutation.mutateAsync,

    // Validate functions
    validateText: validateTextMutation.mutateAsync,
    validateFile: validateFileMutation.mutateAsync,

    // State
    isTranslating: translateTextMutation.isPending || translateFileMutation.isPending,
    isValidating: validateTextMutation.isPending || validateFileMutation.isPending,
    error: translateTextMutation.error || translateFileMutation.error,
    anonymizedFields,

    // Reset
    reset: () => {
      translateTextMutation.reset()
      translateFileMutation.reset()
      validateTextMutation.reset()
      validateFileMutation.reset()
      setAnonymizedFields([])
    },
  }
}
