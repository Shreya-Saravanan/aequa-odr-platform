'use client'
import { usePathname } from 'next/navigation'
import { STAGES, STAGE_LABELS, type Stage } from '@/lib/types'

export default function StepBar() {
  const pathname = usePathname()
  const currentStage = (STAGES.find(s => pathname.endsWith(s)) ?? 'intake') as Stage
  const currentIdx = STAGES.indexOf(currentStage)

  return (
    <div className="mb-6">
      {/* Segment bar */}
      <div className="flex gap-1 mb-2">
        {STAGES.map((s, i) => (
          <div
            key={s}
            className="flex-1 h-1 rounded-full transition-all duration-500"
            style={{
              background: i < currentIdx ? '#1a2b5e' : i === currentIdx ? '#c9a227' : '#e0e0ec',
            }}
          />
        ))}
      </div>
      {/* Title row */}
      <div className="flex items-baseline justify-between">
        <h1 className="text-2xl font-extrabold text-navy tracking-tight">
          {STAGE_LABELS[currentStage]}
        </h1>
        <span className="text-xs font-bold text-gray-400 tracking-widest">
          STEP {currentIdx + 1} OF {STAGES.length}
        </span>
      </div>
    </div>
  )
}
