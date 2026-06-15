'use client'
import { UserCheck, CheckCircle2 } from 'lucide-react'
import StepBar from '@/components/StepBar'
import { useCase } from '@/context/CaseContext'

export default function AssignPage() {
  const ctx = useCase()

  return (
    <div className="max-w-3xl animate-slide-up">
      <StepBar />
      <p className="text-sm text-gray-500 mb-6">
        Assign a neutral arbitrator from the AAA panel.
      </p>

      <div className="card">
        {!ctx.arbitrator ? (
          <>
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-navy-50 flex items-center justify-center">
                <UserCheck size={18} className="text-navy" />
              </div>
              <div>
                <div className="font-semibold text-gray-800">Auto-assign arbitrator</div>
                <div className="text-xs text-gray-400">Conflict check will run automatically</div>
              </div>
            </div>
            <button
              onClick={() => ctx.setArbitrator('Hon. A. Mehta (AAA panel — consumer finance)')}
              className="btn-primary flex items-center gap-2"
            >
              <UserCheck size={15} /> Assign arbitrator
            </button>
          </>
        ) : (
          <div className="animate-slide-up">
            <div className="flex items-start gap-3">
              <CheckCircle2 size={20} className="text-emerald-500 mt-0.5 shrink-0" />
              <div>
                <div className="font-semibold text-gray-800">{ctx.arbitrator}</div>
                <div className="text-xs text-gray-500 mt-1">
                  Conflict check passed · Both parties notified
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
