'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { User, Building2, Scale, ArrowRight, CheckCircle2 } from 'lucide-react'

const ROLES = [
  {
    id: 'Claimant (lender)',
    icon: Building2,
    label: 'CLAIMANT',
    sub: 'Filing a claim or initiating arbitration',
  },
  {
    id: 'Respondent (borrower)',
    icon: User,
    label: 'RESPONDENT',
    sub: 'Responding to a claim against you',
  },
  {
    id: 'Arbitrator',
    icon: Scale,
    label: 'ARBITRATOR',
    sub: 'Neutral decision-maker reviewing the case',
  },
]

export default function LandingPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const router = useRouter()

  function proceed() {
    if (!selected) return
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('aequa_persona', selected)
    }
    router.push('/case/intake')
  }

  return (
    <div className="min-h-screen bg-landing-gradient flex flex-col">
      {/* Header */}
      <header className="px-10 pt-8 pb-0 flex items-center justify-between">
        <span className="text-xl font-black tracking-tight text-navy">
          AEQUA <span className="text-gold">⚖</span> ODR
        </span>
        <span className="text-xs font-bold text-gray-400 tracking-widest">STEP 1 OF 4</span>
      </header>

      {/* Step bar */}
      <div className="px-10 pt-3 flex gap-1.5">
        {[0, 1, 2, 3].map(i => (
          <div
            key={i}
            className="flex-1 h-1 rounded-full transition-all duration-500"
            style={{ background: i === 0 ? '#c9a227' : '#e0e0ec' }}
          />
        ))}
      </div>

      {/* Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-12 animate-slide-up">
        <h1 className="text-2xl font-bold text-gray-800 text-center mb-1">
          Who are you filing as?
        </h1>
        <p className="text-sm text-gray-500 text-center mb-10">
          Choose the option that best describes you.
        </p>

        <div className="flex flex-col sm:flex-row gap-5 w-full max-w-2xl">
          {ROLES.map(({ id, icon: Icon, label, sub }) => {
            const active = selected === id
            return (
              <button
                key={id}
                onClick={() => setSelected(id)}
                className={`
                  relative flex-1 flex flex-col items-start gap-4 p-6 rounded-2xl border-2
                  text-left transition-all duration-200 cursor-pointer bg-white
                  ${active
                    ? 'border-navy shadow-navy scale-[1.02]'
                    : 'border-gray-200 hover:border-navy/30 hover:shadow-card'}
                `}
              >
                {/* Radio indicator */}
                <div className={`absolute top-4 right-4 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors
                  ${active ? 'border-navy bg-navy' : 'border-gray-300'}`}>
                  {active && <div className="w-2 h-2 rounded-full bg-white" />}
                </div>

                <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors
                  ${active ? 'bg-navy text-white' : 'bg-gray-100 text-gray-600'}`}>
                  <Icon size={22} />
                </div>

                <div>
                  <div className="text-base font-black tracking-wide text-gray-900">{label}</div>
                  <div className="text-xs text-gray-500 mt-0.5 leading-snug">{sub}</div>
                </div>
              </button>
            )
          })}
        </div>

        <button
          onClick={proceed}
          disabled={!selected}
          className={`
            mt-10 flex items-center gap-2.5 px-8 py-3 rounded-xl font-semibold text-sm
            transition-all duration-200
            ${selected
              ? 'bg-navy text-white shadow-navy hover:shadow-navy-lg hover:-translate-y-0.5'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'}
          `}
        >
          <ArrowRight size={16} />
          Continue
        </button>

        <p className="mt-6 text-xs text-gray-400">
          Already have an account?{' '}
          <span className="text-navy font-semibold cursor-pointer hover:underline">Sign in</span>
        </p>
      </main>

      <footer className="text-center text-xs text-gray-400 pb-6">
        AI-assisted · not legal advice · ICODR Standards
      </footer>
    </div>
  )
}
