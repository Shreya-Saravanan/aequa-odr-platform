'use client'
import { useState } from 'react'
import { Sparkles, Save, Lock, Download, Eye, EyeOff, CheckCircle2 } from 'lucide-react'
import StepBar from '@/components/StepBar'
import { useCase } from '@/context/CaseContext'
import { api } from '@/lib/api'
import type { Award, Finding } from '@/lib/types'

const RULING_OPTIONS: Finding['ruling'][] = ['credited', 'disallowed', 'rejected', 'granted']

const DISCLAIMER =
  'AI-assisted — not legal advice. A human reviews and decides at every step. ' +
  'Aligned with ICODR Online Dispute Resolution Standards.'

function buildMarkdown(ctx: ReturnType<typeof useCase>): string {
  const aw = ctx.draftAward!
  const seed = ctx.seed!
  const lines = [
    '# ARBITRAL AWARD',
    '',
    `**Case No.:** ${seed.case_id}  `,
    `**${seed.claimant} v. ${seed.respondent}**  `,
    '**Seat:** Boston, MA  ',
    '**Rules:** AAA Consumer Arbitration Rules  ',
    '**Governing Law:** Federal Arbitration Act and Massachusetts law  ',
    '',
    '---',
    '',
    '## I. Background',
    '',
    aw.background,
    '',
    '## II. Issues for Determination',
    '',
    ...aw.issues.map((issue, i) => `${i + 1}. ${issue}`),
    '',
    '## III. Findings and Reasoning',
    '',
    ...aw.findings.flatMap((f, i) => [
      `### ${i + 1}. ${f.issue}`,
      '',
      `**Ruling:** ${f.ruling.charAt(0).toUpperCase() + f.ruling.slice(1)}`,
      '',
      f.reasoning,
      '',
    ]),
    '## IV. Decision',
    '',
    aw.decision,
    '',
    `**AMOUNT AWARDED: $${aw.amount_awarded.toLocaleString('en-US', { minimumFractionDigits: 2 })}**`,
    '',
    '---',
    '',
    '_________________  ',
    '**Arbitrator**  ',
    'Date: ____________________',
    '',
    '---',
    '',
    `*${DISCLAIMER}*`,
  ]
  return lines.join('\n')
}

export default function AwardPage() {
  const ctx = useCase()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editDraft, setEditDraft] = useState<Award | null>(null)
  const [saved, setSaved] = useState(false)
  const [preview, setPreview] = useState(false)

  const aw = editDraft ?? ctx.draftAward

  async function generate() {
    setLoading(true); setError(null)
    try {
      const result = await api.draftAward(ctx.structuredClaim)
      ctx.setDraftAward(result)
      setEditDraft({ ...result, findings: result.findings.map(f => ({ ...f })) })
    } catch (e: any) { setError(e.message) }
    finally { setLoading(false) }
  }

  function saveAward() {
    if (!editDraft) return
    ctx.setDraftAward(editDraft)
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  function updateFinding(idx: number, key: keyof Finding, value: string) {
    setEditDraft(d => {
      if (!d) return d
      const findings = d.findings.map((f, i) => i === idx ? { ...f, [key]: value } : f)
      return { ...d, findings }
    })
  }

  function downloadMd() {
    if (!ctx.draftAward || !ctx.seed) return
    const md = buildMarkdown(ctx)
    const blob = new Blob([md], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `award_${ctx.seed.case_id}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="max-w-3xl animate-slide-up">
      <StepBar />
      <p className="text-sm text-gray-500 mb-6">
        Generate a reasoned draft award, edit every finding, then finalize and download.
      </p>

      <div className="card mb-5">
        <button onClick={generate} disabled={loading}
          className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none">
          <Sparkles size={15} />
          {loading ? 'Drafting award…' : 'Generate draft award'}
        </button>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      </div>

      {aw && (
        <>
          {/* Edit section */}
          <div className="card mb-5">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-base font-bold text-navy">Draft Award</h3>
              <div className="flex items-center gap-3">
                {saved && (
                  <span className="flex items-center gap-1.5 text-xs text-emerald-600 font-semibold">
                    <CheckCircle2 size={13} /> Saved
                  </span>
                )}
                {ctx.awardFinalized && (
                  <span className="flex items-center gap-1.5 bg-navy text-white text-xs font-bold px-3 py-1 rounded-full">
                    <Lock size={11} /> Finalized
                  </span>
                )}
              </div>
            </div>

            <div className="space-y-5">
              {/* Background */}
              <div>
                <label className="label">Background</label>
                <textarea className="input min-h-[96px] resize-y" value={aw.background}
                  onChange={e => setEditDraft(d => d ? { ...d, background: e.target.value } : d)} />
              </div>

              {/* Issues (read-only) */}
              <div>
                <div className="label">Issues for determination</div>
                <ul className="space-y-1">
                  {aw.issues.map((issue, i) => (
                    <li key={i} className="text-sm text-gray-700 flex gap-2">
                      <span className="text-navy font-bold">{i + 1}.</span> {issue}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Findings */}
              <div>
                <div className="label mb-3">Findings and reasoning</div>
                <div className="space-y-4">
                  {aw.findings.map((f, idx) => (
                    <div key={idx} className="bg-surface rounded-xl border border-indigo-100 p-4 space-y-3">
                      <div className="text-xs font-bold text-gray-400 tracking-wide">FINDING {idx + 1}</div>
                      <div className="grid grid-cols-3 gap-3">
                        <div className="col-span-2">
                          <label className="label">Issue</label>
                          <input className="input" value={f.issue}
                            onChange={e => updateFinding(idx, 'issue', e.target.value)} />
                        </div>
                        <div>
                          <label className="label">Ruling</label>
                          <select className="input" value={f.ruling}
                            onChange={e => updateFinding(idx, 'ruling', e.target.value as Finding['ruling'])}>
                            {RULING_OPTIONS.map(r => (
                              <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      <div>
                        <label className="label">Reasoning</label>
                        <textarea className="input min-h-[72px] resize-y" value={f.reasoning}
                          onChange={e => updateFinding(idx, 'reasoning', e.target.value)} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Decision */}
              <div>
                <label className="label">Decision</label>
                <textarea className="input min-h-[96px] resize-y" value={aw.decision}
                  onChange={e => setEditDraft(d => d ? { ...d, decision: e.target.value } : d)} />
              </div>

              {/* Amount */}
              <div>
                <label className="label">Amount awarded ($)</label>
                <input type="number" className="input max-w-[220px]" value={aw.amount_awarded}
                  onChange={e => setEditDraft(d => d ? { ...d, amount_awarded: parseFloat(e.target.value) || 0 } : d)} />
              </div>
            </div>

            <button onClick={saveAward} className="btn-primary mt-5 flex items-center gap-2">
              <Save size={14} /> Save award
            </button>
          </div>

          {/* Amount metric */}
          <div className="bg-navy-gradient rounded-2xl p-5 mb-5 text-white">
            <div className="text-xs font-bold text-white/60 tracking-widest mb-1">AMOUNT AWARDED</div>
            <div className="text-3xl font-extrabold tracking-tight">
              ${ctx.draftAward!.amount_awarded.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </div>
          </div>

          {/* Preview toggle */}
          <div className="card mb-5">
            <button
              onClick={() => setPreview(p => !p)}
              className="flex items-center gap-2 text-sm font-semibold text-navy hover:opacity-80 transition-opacity"
            >
              {preview ? <EyeOff size={15} /> : <Eye size={15} />}
              {preview ? 'Hide preview' : 'Preview final award'}
            </button>

            {preview && (
              <div className="mt-5 pt-5 border-t border-indigo-50 animate-slide-up">
                <h1 className="text-2xl font-black text-center text-navy mb-1">ARBITRAL AWARD</h1>
                <p className="text-center text-sm text-gray-500 mb-5">
                  <strong>Case No.:</strong> {ctx.seed?.case_id} &nbsp;|&nbsp;
                  <strong>{ctx.seed?.claimant} v. {ctx.seed?.respondent}</strong><br />
                  Seat: Boston, MA &nbsp;|&nbsp; AAA Consumer Arbitration Rules<br />
                  Governed by the FAA and Massachusetts law
                </p>
                <hr className="border-indigo-100 mb-5" />
                <h2 className="text-base font-bold text-navy mb-2">I. Background</h2>
                <p className="text-sm text-gray-700 leading-relaxed mb-5">{aw.background}</p>
                <h2 className="text-base font-bold text-navy mb-2">II. Issues for Determination</h2>
                <ol className="list-decimal list-inside space-y-1 mb-5">
                  {aw.issues.map((issue, i) => <li key={i} className="text-sm text-gray-700">{issue}</li>)}
                </ol>
                <h2 className="text-base font-bold text-navy mb-3">III. Findings and Reasoning</h2>
                {aw.findings.map((f, i) => (
                  <div key={i} className="mb-4">
                    <h3 className="text-sm font-bold text-gray-800">{i + 1}. {f.issue}</h3>
                    <p className="text-xs font-semibold text-navy mt-0.5 mb-1">
                      Ruling: {f.ruling.charAt(0).toUpperCase() + f.ruling.slice(1)}
                    </p>
                    <p className="text-sm text-gray-700 leading-relaxed">{f.reasoning}</p>
                  </div>
                ))}
                <h2 className="text-base font-bold text-navy mb-2 mt-5">IV. Decision</h2>
                <p className="text-sm text-gray-700 leading-relaxed mb-4">{aw.decision}</p>
                <p className="text-sm font-bold text-navy">
                  AMOUNT AWARDED: ${aw.amount_awarded.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </p>
                <hr className="border-indigo-100 my-5" />
                <p className="text-sm text-gray-500">_________________&nbsp;&nbsp; <strong>Arbitrator</strong> &nbsp;&nbsp; Date: ____________________</p>
                <hr className="border-indigo-100 my-5" />
                <p className="text-xs text-gray-400">{DISCLAIMER}</p>
              </div>
            )}
          </div>

          {/* Finalize + Download */}
          <div className="flex items-center gap-3">
            {!ctx.awardFinalized ? (
              <button onClick={ctx.finalizeAward} className="btn-primary flex items-center gap-2">
                <Lock size={14} /> Finalize award
              </button>
            ) : (
              <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 text-emerald-700 font-semibold text-sm rounded-xl px-4 py-2.5">
                <CheckCircle2 size={15} /> Award finalized
              </div>
            )}
            <button onClick={downloadMd} className="btn-outline flex items-center gap-2">
              <Download size={14} /> Download (.md)
            </button>
          </div>
        </>
      )}
    </div>
  )
}
