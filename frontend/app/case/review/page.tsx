'use client'
import { useState } from 'react'
import { Search, FileText } from 'lucide-react'
import StepBar from '@/components/StepBar'
import { useCase } from '@/context/CaseContext'
import { api } from '@/lib/api'

export default function ReviewPage() {
  const ctx = useCase()
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function ask() {
    if (!question.trim()) return
    setLoading(true); setError(null)
    try {
      const result = await api.askReview(question, ctx.structuredClaim)
      ctx.addReviewEntry({ q: question, a: result.answer, src: result.source_document })
      setQuestion('')
    } catch (e: any) { setError(e.message) }
    finally { setLoading(false) }
  }

  return (
    <div className="max-w-3xl animate-slide-up">
      <StepBar />
      <p className="text-sm text-gray-500 mb-6">
        Ask the case record anything. Answers cite the source document.
      </p>

      <div className="card mb-5">
        <label className="label">Question about the case</label>
        <div className="flex gap-3">
          <input
            className="input flex-1"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && ask()}
            placeholder="e.g. When did the borrower last make a credited payment?"
          />
          <button onClick={ask} disabled={loading || !question.trim()}
            className="btn-primary flex items-center gap-2 shrink-0 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none">
            <Search size={14} />
            {loading ? 'Searching…' : 'Ask'}
          </button>
        </div>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      </div>

      {/* History */}
      <div className="space-y-4">
        {ctx.reviewHistory.map((item, i) => (
          <div key={i} className="card animate-slide-up">
            <div className="flex items-start gap-2 mb-3">
              <Search size={14} className="text-navy mt-0.5 shrink-0" />
              <p className="text-sm font-semibold text-gray-800">{item.q}</p>
            </div>
            <p className="text-sm text-gray-700 leading-relaxed pl-5 mb-3">{item.a}</p>
            <div className="flex items-center gap-1.5 pl-5">
              <FileText size={12} className="text-gray-400" />
              <span className="text-xs text-gray-400">Source: {item.src}</span>
            </div>
          </div>
        ))}
        {ctx.reviewHistory.length === 0 && (
          <div className="text-center py-12 text-gray-400 text-sm">
            No questions yet — ask something above.
          </div>
        )}
      </div>
    </div>
  )
}
