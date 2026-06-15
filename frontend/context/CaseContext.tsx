'use client'
import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import type {
  SeedCase, StructuredClaim, ValidationResult, Defense, Award, ReviewEntry, Persona,
} from '@/lib/types'
import { api } from '@/lib/api'

interface CaseState {
  seed: SeedCase | null
  structuredClaim: StructuredClaim | null
  validation: ValidationResult | null
  defense: Defense | null
  explanation: string | null
  draftAward: Award | null
  reviewHistory: ReviewEntry[]
  arbitrator: string | null
  awardFinalized: boolean
  persona: Persona
  loading: boolean
  error: string | null
}

interface CaseActions {
  setStructuredClaim: (c: StructuredClaim) => void
  setValidation: (v: ValidationResult) => void
  setDefense: (d: Defense) => void
  setExplanation: (e: string) => void
  setDraftAward: (a: Award) => void
  addReviewEntry: (entry: ReviewEntry) => void
  setArbitrator: (a: string) => void
  finalizeAward: () => void
  setPersona: (p: Persona) => void
  clearError: () => void
}

const CaseContext = createContext<(CaseState & CaseActions) | null>(null)

export function CaseProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<CaseState>({
    seed: null,
    structuredClaim: null,
    validation: null,
    defense: null,
    explanation: null,
    draftAward: null,
    reviewHistory: [],
    arbitrator: null,
    awardFinalized: false,
    persona: 'Claimant (lender)',
    loading: true,
    error: null,
  })

  useEffect(() => {
    api.getSeed()
      .then(seed => setState(s => ({ ...s, seed, loading: false })))
      .catch(e => setState(s => ({ ...s, loading: false, error: e.message })))
  }, [])

  const set = <K extends keyof CaseState>(key: K, value: CaseState[K]) =>
    setState(s => ({ ...s, [key]: value }))

  return (
    <CaseContext.Provider value={{
      ...state,
      setStructuredClaim: c => set('structuredClaim', c),
      setValidation: v => set('validation', v),
      setDefense: d => set('defense', d),
      setExplanation: e => set('explanation', e),
      setDraftAward: a => set('draftAward', a),
      addReviewEntry: entry => setState(s => ({ ...s, reviewHistory: [entry, ...s.reviewHistory] })),
      setArbitrator: a => set('arbitrator', a),
      finalizeAward: () => set('awardFinalized', true),
      setPersona: p => set('persona', p),
      clearError: () => set('error', null),
    }}>
      {children}
    </CaseContext.Provider>
  )
}

export function useCase() {
  const ctx = useContext(CaseContext)
  if (!ctx) throw new Error('useCase must be used inside CaseProvider')
  return ctx
}
