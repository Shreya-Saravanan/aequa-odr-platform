export interface CompletenessItem {
  label: string
  status: 'present' | 'missing'
  note?: string
}

export interface StructuredClaim {
  claimant: string
  respondent: string
  claim_type: string
  principal_balance: number
  fees_claimed: number
  interest_note: string
  key_dates: string[]
  relief_sought: string
  completeness: CompletenessItem[]
}

export interface Finding {
  issue: string
  ruling: 'credited' | 'disallowed' | 'rejected' | 'granted'
  reasoning: string
}

export interface Award {
  background: string
  issues: string[]
  findings: Finding[]
  decision: string
  amount_awarded: number
}

export interface ReviewAnswer {
  answer: string
  source_document: string
}

export interface Defense {
  admitted: string[]
  disputed: string[]
  requested_relief: string
}

export interface ValidationResult {
  present: string[]
  missing: string[]
  clause_found: boolean
  clause_text: string
  arbitrable: boolean
  todo: string[]
}

export interface CaseDocument {
  name: string
  doc_type: string
  uploaded_by: string
  content: string
}

export interface SeedCase {
  case_id: string
  title: string
  claimant: string
  respondent: string
  documents: CaseDocument[]
  hearing_transcript: string
  lender_narrative: string
  raw_defense_notes: string
}

export interface ReviewEntry {
  q: string
  a: string
  src: string
}

export type Persona = 'Claimant (lender)' | 'Respondent (borrower)' | 'Arbitrator' | 'Admin'
export type Stage = 'intake' | 'validate' | 'assign' | 'respond' | 'review' | 'hearing' | 'award'

export const STAGES: Stage[] = ['intake', 'validate', 'assign', 'respond', 'review', 'hearing', 'award']
export const STAGE_LABELS: Record<Stage, string> = {
  intake: 'Intake',
  validate: 'Validate',
  assign: 'Assign',
  respond: 'Respond',
  review: 'Review',
  hearing: 'Hearing',
  award: 'Award',
}
export const PERSONAS: Persona[] = [
  'Claimant (lender)',
  'Respondent (borrower)',
  'Arbitrator',
  'Admin',
]
