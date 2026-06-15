import type {
  StructuredClaim, ValidationResult, Defense, ReviewAnswer, Award, SeedCase,
} from './types'

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }))
    throw new Error(err.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export const api = {
  getSeed: () => get<SeedCase>('/seed'),
  structureClaim: (text: string) =>
    post<StructuredClaim>('/intake/structure', { text }),
  validate: () =>
    post<ValidationResult>('/validate', {}),
  explain: (claim_text: string) =>
    post<{ explanation: string }>('/explain', { claim_text }),
  draftDefense: (notes: string) =>
    post<Defense>('/defense/draft', { notes }),
  askReview: (question: string, structured_claim?: StructuredClaim | null) =>
    post<ReviewAnswer>('/review/ask', { question, structured_claim }),
  draftAward: (structured_claim?: StructuredClaim | null) =>
    post<Award>('/award/draft', { structured_claim }),
}
