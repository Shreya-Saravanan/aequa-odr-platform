from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from llm import call_claude, MODEL_AWARD, USE_OPUS_FOR_AWARD
from schemas import StructuredClaim, Award, ReviewAnswer, Defense, ValidationResult
from seed import (
    build_seed_case, LENDER_NARRATIVE, RAW_DEFENSE_NOTES,
    LOAN_AGREEMENT, LEDGER, DEMAND_NOTICE, EVIDENCE_TRANSFERS, HEARING,
)

app = FastAPI(title="Aequa ODR API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Seed case (read-only reference for AI context) ──
_SEED = build_seed_case()

# ── System prompts ──
INTAKE_SYSTEM = (
    "You are an intake assistant for an arbitration ODR platform. Convert the user's plain-English "
    "description into a structured claim, and assess completeness against what an arbitration filing "
    "needs: clear parties, claim type, amounts, key dates, relief sought, an arbitration-clause "
    "citation, and an itemized interest calculation. Mark items the user clearly provided as "
    "'present' and items not evidenced as 'missing'. Use the amounts the user states. You provide "
    "structuring and information, not legal advice."
)
AWARD_SYSTEM = (
    "You assist a neutral arbitrator in drafting a reasoned award under the U.S. Federal Arbitration "
    "Act and Massachusetts law. Review the full case record. For each disputed item, weigh the "
    "evidence and the contract terms, including any integration / entire-agreement clause. Be "
    "specific: cite amounts and documents in your reasoning. Set amount_awarded to the net principal "
    "the respondent must pay after your findings (exclude fees you disallow). A reasoned award is a "
    "party election under U.S. domestic practice; you produce a draft the arbitrator edits and "
    "finalizes. This is not legal advice."
)
REVIEW_SYSTEM = (
    "Answer the arbitrator's question using ONLY the supplied case record. Cite the specific document "
    "you relied on in source_document. If the record does not answer the question, say so plainly and "
    "set source_document to 'not in record'. This is not legal advice."
)
EXPLAIN_SYSTEM = (
    "Explain this claim to a non-lawyer respondent in plain, calm, reassuring English. Avoid jargon. "
    "Do not give legal advice or tell them what to do - just help them understand what is being "
    "claimed against them and why."
)
DEFENSE_SYSTEM = (
    "Turn the respondent's rough notes into a structured statement of defense: what they admit, what "
    "they dispute (each a clear point), and the relief they request. Structuring only, not legal "
    "advice. Do not invent facts beyond the notes."
)
VALIDATE_SYSTEM = (
    "You are an intake validation agent. Check the supplied documents against the required-documents "
    "checklist and locate the arbitration clause. Report what is present, what is missing, the exact "
    "clause text if found, whether the matter is arbitrable, and a short to-do list of what the filer "
    "must add. This is not legal advice."
)


def _build_record_text(structured_claim: Optional[dict] = None) -> str:
    parts = [
        f"CASE: {_SEED.title} ({_SEED.case_id})",
        f"Claimant: {_SEED.claimant}",
        f"Respondent: {_SEED.respondent}",
        "",
    ]
    for d in _SEED.documents:
        parts.append(f"--- DOCUMENT: {d.name} (type: {d.doc_type}, uploaded by {d.uploaded_by}) ---")
        parts.append(d.content)
        parts.append("")
    if structured_claim:
        parts.append("--- STRUCTURED CLAIM ---")
        parts.append(str(structured_claim))
        parts.append("")
    parts.append("--- RESPONDENT ROUGH NOTES ---")
    parts.append(RAW_DEFENSE_NOTES)
    parts.append("")
    parts.append("--- HEARING TRANSCRIPT ---")
    parts.append(_SEED.hearing_transcript)
    return "\n".join(parts)


# ── Request models ──
class StructureRequest(BaseModel):
    text: str

class ExplainRequest(BaseModel):
    claim_text: str

class DefenseRequest(BaseModel):
    notes: str

class ReviewRequest(BaseModel):
    question: str
    structured_claim: Optional[dict] = None

class AwardRequest(BaseModel):
    structured_claim: Optional[dict] = None


# ── Routes ──

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/seed")
def get_seed():
    return {
        "case_id": _SEED.case_id,
        "title": _SEED.title,
        "claimant": _SEED.claimant,
        "respondent": _SEED.respondent,
        "documents": [d.model_dump() for d in _SEED.documents],
        "hearing_transcript": _SEED.hearing_transcript,
        "lender_narrative": LENDER_NARRATIVE,
        "raw_defense_notes": RAW_DEFENSE_NOTES,
    }


@app.post("/intake/structure")
def structure_claim(req: StructureRequest):
    result = call_claude(system=INTAKE_SYSTEM, user=req.text, schema=StructuredClaim)
    return result.model_dump()


@app.post("/validate")
def validate_documents():
    required = "Required documents: loan agreement, payment ledger, demand notice, proof of default."
    docs = "\n\n".join(f"[{d.name}]\n{d.content}" for d in _SEED.documents)
    result = call_claude(system=VALIDATE_SYSTEM, user=required + "\n\nDOCUMENTS:\n" + docs,
                         schema=ValidationResult)
    return result.model_dump()


@app.post("/explain")
def explain_claim(req: ExplainRequest):
    explanation = call_claude(system=EXPLAIN_SYSTEM, user=req.claim_text)
    return {"explanation": explanation}


@app.post("/defense/draft")
def draft_defense(req: DefenseRequest):
    result = call_claude(system=DEFENSE_SYSTEM, user=req.notes, schema=Defense)
    return result.model_dump()


@app.post("/review/ask")
def ask_review(req: ReviewRequest):
    record = _build_record_text(req.structured_claim)
    result = call_claude(
        system=REVIEW_SYSTEM,
        user=f"QUESTION: {req.question}\n\n{record}",
        schema=ReviewAnswer,
    )
    return result.model_dump()


@app.post("/award/draft")
def draft_award(req: AwardRequest):
    record = _build_record_text(req.structured_claim)
    model = MODEL_AWARD if USE_OPUS_FOR_AWARD else "claude-sonnet-4-6"
    result = call_claude(system=AWARD_SYSTEM, user=record, schema=Award,
                         model=model, max_tokens=2500)
    return result.model_dump()
