'use client'
import { useState } from 'react'
import { Sparkles, CheckCircle2, AlertTriangle, ChevronDown, ChevronUp, Save } from 'lucide-react'
import StepBar from '@/components/StepBar'
import { useCase } from '@/context/CaseContext'
import { api } from '@/lib/api'
import type { StructuredClaim } from '@/lib/types'

export default function IntakePage() {
  const ctx = useCase()
  const [text, setText] = useState(ctx.seed?.lender_narrative ?? '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editDraft, setEditDraft] = useState<StructuredClaim | null>(null)
  const [saved, setSaved] = useState(false)

  const sc = ctx.structuredClaim

  async function structure() {
    setLoading(true); setError(null)
    try {
      const result = await api.structureClaim(text)
      ctx.setStructuredClaim(result)
      setEditDraft(result)
      setSaved(false)
    } catch (e: any) { setError(e.message) }
    finally { setLoading(false) }
  }

  function saveEdits() {
    if (!editDraft) return
    ctx.setStructuredClaim(editDraft)
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  const draft = editDraft ?? sc

  return (
    <div className="max-w-3xl animate-slide-up">
      <StepBar />
      <p className="text-sm text-gray-500 mb-6">
        Describe the dispute in plain English. The AI structures it and checks completeness.
      </p>

      {/* Input card */}
      <div className="card mb-5">
        <label className="label">Your claim, in your own words</label>
        <textarea
          className="input min-h-[120px] resize-y"
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="Describe the dispute…"
        />
        <button
          onClick={structure}
          disabled={loading || !text.trim()}
          className="btn-primary mt-4 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none"
        >
          <Sparkles size={15} />
          {loading ? 'Structuring…' : 'Structure my claim'}
        </button>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      </div>

      {/* Structured claim */}
      {draft && (
        <div className="card animate-slide-up">
          <div className="flex items-center justify-between mb-5">
            <h3 className="text-base font-bold text-navy">Structured Claim</h3>
            {saved && (
              <span className="flex items-center gap-1.5 text-xs text-emerald-600 font-semibold">
                <CheckCircle2 size={13} /> Saved
              </span>
            )}
          </div>

          {/* Parties (read-only) */}
          <div className="grid grid-cols-2 gap-4 mb-5 pb-5 border-b border-indigo-50">
            <div>
              <div className="label">Claimant</div>
              <div className="text-sm font-semibold text-gray-800">{draft.claimant}</div>
            </div>
            <div>
              <div className="label">Respondent</div>
              <div className="text-sm font-semibold text-gray-800">{draft.respondent}</div>
            </div>
          </div>

          {/* Editable fields */}
          <div className="space-y-4">
            <div>
              <label className="label">Claim type</label>
              <input className="input" value={draft.claim_type}
                onChange={e => setEditDraft(d => d ? { ...d, claim_type: e.target.value } : d)} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Principal balance ($)</label>
                <input type="number" className="input" value={draft.principal_balance}
                  onChange={e => setEditDraft(d => d ? { ...d, principal_balance: parseFloat(e.target.value) || 0 } : d)} />
              </div>
              <div>
                <label className="label">Fees claimed ($)</label>
                <input type="number" className="input" value={draft.fees_claimed}
                  onChange={e => setEditDraft(d => d ? { ...d, fees_claimed: parseFloat(e.target.value) || 0 } : d)} />
              </div>
            </div>
            <div>
              <label className="label">Interest note</label>
              <input className="input" value={draft.interest_note}
                onChange={e => setEditDraft(d => d ? { ...d, interest_note: e.target.value } : d)} />
            </div>
            <div>
              <label className="label">Key dates (comma-separated)</label>
              <input className="input" value={draft.key_dates.join(', ')}
                onChange={e => setEditDraft(d => d ? { ...d, key_dates: e.target.value.split(',').map(s => s.trim()).filter(Boolean) } : d)} />
            </div>
            <div>
              <label className="label">Relief sought</label>
              <textarea className="input min-h-[72px] resize-y" value={draft.relief_sought}
                onChange={e => setEditDraft(d => d ? { ...d, relief_sought: e.target.value } : d)} />
            </div>
          </div>

          <button onClick={saveEdits} className="btn-primary mt-5 flex items-center gap-2">
            <Save size={14} /> Save changes
          </button>

          {/* Completeness */}
          <div className="mt-6 pt-5 border-t border-indigo-50">
            <h4 className="text-sm font-bold text-gray-700 mb-3">Completeness check</h4>
            <div className="space-y-2">
              {[...draft.completeness]
                .sort((a, b) => (a.status === b.status ? 0 : a.status === 'present' ? -1 : 1))
                .map(item => (
                  <div key={item.label} className="flex items-start gap-2">
                    {item.status === 'present'
                      ? <CheckCircle2 size={15} className="text-emerald-500 mt-0.5 shrink-0" />
                      : <AlertTriangle size={15} className="text-amber-500 mt-0.5 shrink-0" />}
                    <div>
                      <span className="text-sm font-semibold text-gray-700">{item.label}</span>
                      {item.note && <p className="text-xs text-gray-400 mt-0.5">{item.note}</p>}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
