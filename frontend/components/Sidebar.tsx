'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  FileText, ShieldCheck, UserCheck, MessageSquare,
  Search, Mic, Award, ChevronRight, CheckCircle2, Circle,
} from 'lucide-react'
import { useCase } from '@/context/CaseContext'
import { STAGES, STAGE_LABELS, PERSONAS, type Persona, type Stage } from '@/lib/types'

const ICONS: Record<Stage, React.ElementType> = {
  intake: FileText, validate: ShieldCheck, assign: UserCheck,
  respond: MessageSquare, review: Search, hearing: Mic, award: Award,
}

export default function Sidebar() {
  const pathname = usePathname()
  const ctx = useCase()

  const currentStage = STAGES.find(s => pathname.endsWith(s)) ?? 'intake'
  const currentIdx = STAGES.indexOf(currentStage)

  // Case file status
  const hasDefense = ctx.seed != null && ctx.defense != null
  const statusRows = [
    { label: `Documents`, value: `${ctx.seed?.documents.length ?? 0}`, done: true },
    { label: 'Structured claim', done: !!ctx.structuredClaim },
    { label: 'Defense submitted', done: hasDefense },
    { label: `Review Q&A`, value: `${ctx.reviewHistory.length}`, done: ctx.reviewHistory.length > 0 },
    { label: 'Draft award', done: !!ctx.draftAward, extra: ctx.awardFinalized ? '🔒' : undefined },
  ]

  return (
    <aside className="w-64 shrink-0 h-screen sticky top-0 bg-white border-r border-indigo-100
                      flex flex-col overflow-y-auto shadow-[4px_0_24px_rgba(80,80,180,0.05)]">
      {/* Logo */}
      <div className="px-6 pt-7 pb-5">
        <div className="text-lg font-black tracking-tight text-navy">
          AEQUA <span className="text-gold">⚖</span> ODR
        </div>
        <div className="text-[10px] font-semibold text-gray-400 tracking-widest mt-0.5">
          AI-ASSISTED DISPUTE RESOLUTION
        </div>
      </div>

      {/* Nav */}
      <div className="px-3">
        <p className="text-[10px] font-bold text-gray-400 tracking-widest px-3 mb-2">
          CASE LIFECYCLE
        </p>
        {STAGES.map((stage, i) => {
          const Icon = ICONS[stage]
          const isActive = stage === currentStage
          const isDone = i < currentIdx
          return (
            <Link
              key={stage}
              href={`/case/${stage}`}
              className={`
                flex items-center gap-3 px-3 py-2.5 rounded-xl mb-0.5 text-sm font-medium
                transition-all duration-150 group
                ${isActive
                  ? 'bg-navy-50 text-navy font-bold'
                  : isDone
                    ? 'text-gray-500 hover:bg-gray-50 hover:text-gray-800'
                    : 'text-gray-400 hover:bg-gray-50 hover:text-gray-600'}
              `}
            >
              <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 transition-colors
                ${isActive ? 'bg-navy text-white' : isDone ? 'bg-gray-100 text-gray-500' : 'bg-gray-100 text-gray-400'}`}>
                <Icon size={14} />
              </div>
              <span className="flex-1">{STAGE_LABELS[stage]}</span>
              {isDone && <CheckCircle2 size={13} className="text-emerald-500" />}
              {isActive && <ChevronRight size={13} className="text-navy" />}
            </Link>
          )
        })}
      </div>

      <div className="mx-5 my-4 border-t border-indigo-100" />

      {/* Case file */}
      <div className="px-6">
        <p className="text-[10px] font-bold text-gray-400 tracking-widest mb-3">CASE FILE</p>
        <div className="space-y-2">
          {statusRows.map(({ label, value, done, extra }) => (
            <div key={label} className="flex items-center gap-2 text-xs">
              {done
                ? <CheckCircle2 size={13} className="text-emerald-500 shrink-0" />
                : <Circle size={13} className="text-gray-300 shrink-0" />}
              <span className={done ? 'text-gray-700' : 'text-gray-400'}>
                {label}{value ? `: ${value}` : ''}{extra ? ` ${extra}` : ''}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1" />
      <div className="mx-5 my-4 border-t border-indigo-100" />

      {/* Persona selector */}
      <div className="px-6 pb-6">
        <p className="text-[10px] font-bold text-gray-400 tracking-widest mb-2">VIEWING AS</p>
        <select
          value={ctx.persona}
          onChange={e => ctx.setPersona(e.target.value as Persona)}
          className="w-full rounded-xl border border-indigo-100 bg-surface px-3 py-2 text-sm
                     font-medium text-navy outline-none focus:border-navy focus:ring-2 focus:ring-navy/10"
        >
          {PERSONAS.map(p => <option key={p}>{p}</option>)}
        </select>

        {/* Case chip */}
        <div className="mt-3 bg-surface rounded-xl border border-indigo-100 px-3.5 py-3">
          <div className="text-[10px] font-bold text-gray-400 tracking-widest">CASE ID</div>
          <div className="text-sm font-bold text-navy mt-0.5">
            {ctx.seed?.case_id ?? '—'}
          </div>
          <div className="text-[11px] text-gray-400 mt-0.5">
            Stage {currentIdx + 1} of {STAGES.length}
          </div>
        </div>
      </div>
    </aside>
  )
}
