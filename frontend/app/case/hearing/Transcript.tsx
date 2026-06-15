'use client'
import { useCase } from '@/context/CaseContext'
import StepBar from '@/components/StepBar'

export default function HearingTranscript() {
  const ctx = useCase()
  return (
    <div className="card">
      <pre className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap font-mono bg-surface rounded-xl p-5 border border-indigo-50">
        {ctx.seed?.hearing_transcript ?? 'Loading…'}
      </pre>
    </div>
  )
}
