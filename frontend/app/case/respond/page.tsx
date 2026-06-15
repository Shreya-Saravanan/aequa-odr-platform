'use client'
import { useState } from 'react'
import { Sparkles, Save, CheckCircle2 } from 'lucide-react'
import StepBar from '@/components/StepBar'
import { useCase } from '@/context/CaseContext'
import { api } from '@/lib/api'
import type { Defense } from '@/lib/types'

export default function RespondPage() {
  const ctx = useCase()
  const [notes, setNotes] = useState(ctx.seed?.raw_defense_notes ?? '')
  const [loadingExplain, setLoadingExplain] = useState(false)
  const [loadingDefense, setLoadingDefense] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editDraft, setEditDraft] = useState<Defense | null>(null)
  const [saved, setSaved] = useState(false)

  const defense = editDraft ?? ctx.defense

  async function explain() {
    setLoadingExplain(true); setError(null)
    try {
      const claimText = ctx.structuredClaim
        ? JSON.stringify(ctx.structuredClaim)
        : ctx.seed?.lender_narrative ?? ''
      const { explanation } = await api.explain(claimText)
      ctx.setExplanation(explanation)
    } catch (e: any) { setError(e.message) }
    finally { setLoadingExplain(false) }
  }

  async function draftDefense() {
    setLoadingDefense(true); setError(null)
    try {
      const result = await api.draftDefense(notes)
      ctx.setDefense(result)
      setEditDraft({ ...result })
    } catch (e: any) { setError(e.message) }
    finally { setLoadingDefense(false) }
  }

  function saveDefense() {
    if (!editDraft) return
    ctx.setDefense(editDraft)
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  return (
    <div className="max-w-3xl animate-slide-up">
      <StepBar />
      <p className="text-sm text-gray-500 mb-6">
        Understand the claim against you, then build your defense.
      </p>

      {/* Explain */}
      <div className="card mb-5">
        <h3 className="text-sm font-bold text-navy mb-3">1. Understand the claim</h3>
        <button onClick={explain} disabled={loadingExplain}
          className="btn-outline flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
          <Sparkles size={14} />
          {loadingExplain ? 'Explaining…' : 'Explain this claim in plain English'}
        </button>
        {ctx.explanation && (
          <div className="mt-4 bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-900 leading-relaxed animate-slide-up">
            {ctx.explanation}
          </div>
        )}
      </div>

      {/* Draft defense */}
      <div className="card mb-5">
        <h3 className="text-sm font-bold text-navy mb-3">2. Draft your defense</h3>
        <label className="label">Your rough notes</label>
        <textarea className="input min-h-[100px] resize-y mb-4" value={notes}
          onChange={e => setNotes(e.target.value)} />
        <button onClick={draftDefense} disabled={loadingDefense}
          className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none">
          <Sparkles size={14} />
          {loadingDefense ? 'Drafting…' : 'Draft my defense'}
        </button>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      </div>

      {/* Editable defense */}
      {defense && (
        <div className="card animate-slide-up">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-navy">Defense Statement</h3>
            {saved && (
              <span className="flex items-center gap-1.5 text-xs text-emerald-600 font-semibold">
                <CheckCircle2 size={13} /> Saved
              </span>
            )}
          </div>

          <div className="space-y-4">
            <div>
              <label className="label">Admitted (one item per line)</label>
              <textarea className="input min-h-[88px] resize-y"
                value={defense.admitted.join('\n')}
                onChange={e => setEditDraft(d => d
                  ? { ...d, admitted: e.target.value.split('\n').filter(Boolean) }
                  : ctx.defense ? { ...ctx.defense, admitted: e.target.value.split('\n').filter(Boolean) } : null
                )} />
            </div>
            <div>
              <label className="label">Disputed (one item per line)</label>
              <textarea className="input min-h-[88px] resize-y"
                value={defense.disputed.join('\n')}
                onChange={e => setEditDraft(d => d
                  ? { ...d, disputed: e.target.value.split('\n').filter(Boolean) }
                  : ctx.defense ? { ...ctx.defense, disputed: e.target.value.split('\n').filter(Boolean) } : null
                )} />
            </div>
            <div>
              <label className="label">Requested relief</label>
              <textarea className="input min-h-[64px] resize-y"
                value={defense.requested_relief}
                onChange={e => setEditDraft(d => d
                  ? { ...d, requested_relief: e.target.value }
                  : ctx.defense ? { ...ctx.defense, requested_relief: e.target.value } : null
                )} />
            </div>
          </div>

          <button onClick={saveDefense} className="btn-primary mt-5 flex items-center gap-2">
            <Save size={14} /> Save defense
          </button>
        </div>
      )}
    </div>
  )
}
