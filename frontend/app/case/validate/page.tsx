'use client'
import { useState } from 'react'
import { ShieldCheck, CheckCircle2, AlertTriangle, ChevronDown } from 'lucide-react'
import StepBar from '@/components/StepBar'
import { useCase } from '@/context/CaseContext'
import { api } from '@/lib/api'

export default function ValidatePage() {
  const ctx = useCase()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [clauseOpen, setClauseOpen] = useState(false)
  const v = ctx.validation

  async function run() {
    setLoading(true); setError(null)
    try { ctx.setValidation(await api.validate()) }
    catch (e: any) { setError(e.message) }
    finally { setLoading(false) }
  }

  return (
    <div className="max-w-3xl animate-slide-up">
      <StepBar />
      <p className="text-sm text-gray-500 mb-6">
        Check document completeness and verify the arbitration clause before the case proceeds.
      </p>

      <div className="card mb-5">
        <button onClick={run} disabled={loading}
          className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none">
          <ShieldCheck size={15} />
          {loading ? 'Validating…' : 'Run validation'}
        </button>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      </div>

      {v && (
        <div className="card animate-slide-up space-y-5">
          {/* Present */}
          {v.present.length > 0 && (
            <div>
              <h4 className="text-sm font-bold text-gray-700 mb-2">Present</h4>
              <div className="space-y-1.5">
                {v.present.map(p => (
                  <div key={p} className="badge-present">{p}</div>
                ))}
              </div>
            </div>
          )}

          {/* Missing */}
          {v.missing.length > 0 && (
            <div>
              <h4 className="text-sm font-bold text-gray-700 mb-2">Missing</h4>
              <div className="space-y-1.5">
                {v.missing.map(m => (
                  <div key={m} className="badge-missing"><AlertTriangle size={13} />{m}</div>
                ))}
              </div>
            </div>
          )}

          {/* Arbitrable */}
          <div className="flex items-center gap-2">
            {v.arbitrable
              ? <CheckCircle2 size={16} className="text-emerald-500" />
              : <AlertTriangle size={16} className="text-red-500" />}
            <span className="text-sm font-semibold text-gray-700">
              {v.arbitrable ? 'Matter is arbitrable' : 'Matter may not be arbitrable'}
            </span>
          </div>

          {/* Clause */}
          {v.clause_found && (
            <div>
              <button
                onClick={() => setClauseOpen(o => !o)}
                className="flex items-center gap-2 text-sm font-semibold text-navy hover:opacity-80 transition-opacity"
              >
                <ChevronDown size={16} className={`transition-transform ${clauseOpen ? 'rotate-180' : ''}`} />
                Extracted arbitration clause
              </button>
              {clauseOpen && (
                <div className="mt-2 bg-surface rounded-xl border border-indigo-100 p-4 text-sm text-gray-700 leading-relaxed animate-slide-up">
                  {v.clause_text}
                </div>
              )}
            </div>
          )}

          {/* To-do */}
          {v.todo.length > 0 && (
            <div>
              <h4 className="text-sm font-bold text-gray-700 mb-2">To-do for filer</h4>
              <ul className="space-y-1">
                {v.todo.map(t => (
                  <li key={t} className="flex items-start gap-2 text-sm text-gray-600">
                    <span className="text-amber-500 mt-0.5">•</span>{t}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
