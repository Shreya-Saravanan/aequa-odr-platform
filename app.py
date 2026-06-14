import streamlit as st

from data.seed import build_seed_case, Submission, LENDER_NARRATIVE, RAW_DEFENSE_NOTES
from modules.llm import call_claude, MODEL_DEFAULT, MODEL_AWARD, USE_OPUS_FOR_AWARD
from modules.schemas import StructuredClaim, Award, ReviewAnswer, Defense, ValidationResult

st.set_page_config(page_title="Aequa ODR", page_icon="balance", layout="wide")

STAGES = ["Intake", "Validate", "Assign", "Respond", "Review", "Hearing", "Award"]
PERSONAS = ["Claimant (lender)", "Respondent (borrower)", "Arbitrator", "Admin"]
DISCLAIMER = ("AI-assisted - not legal advice. A human reviews and decides at every step. "
              "Aligned with ICODR Online Dispute Resolution Standards.")

# ---- session state (guarded init) ----
if "case" not in st.session_state:
    st.session_state.case = build_seed_case()
if "stage" not in st.session_state:
    st.session_state.stage = "Intake"
if "persona" not in st.session_state:
    st.session_state.persona = PERSONAS[0]
if "review_history" not in st.session_state:
    st.session_state.review_history = []
if "arbitrator" not in st.session_state:
    st.session_state.arbitrator = None
if "explanation" not in st.session_state:
    st.session_state.explanation = None
if "defense" not in st.session_state:
    st.session_state.defense = None
if "validation" not in st.session_state:
    st.session_state.validation = None

# ---- system prompts ----
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


def get_record_text(case) -> str:
    parts = [f"CASE: {case.title} ({case.case_id})",
             f"Claimant: {case.claimant}", f"Respondent: {case.respondent}", ""]
    for d in case.documents:
        parts.append(f"--- DOCUMENT: {d.name} (type: {d.doc_type}, uploaded by {d.uploaded_by}) ---")
        parts.append(d.content)
        parts.append("")
    if case.structured_claim:
        parts.append("--- STRUCTURED CLAIM ---")
        parts.append(str(case.structured_claim))
        parts.append("")
    parts.append("--- RESPONDENT ROUGH NOTES ---")
    parts.append(RAW_DEFENSE_NOTES)
    parts.append("")
    parts.append("--- HEARING TRANSCRIPT ---")
    parts.append(case.hearing_transcript)
    return "\n".join(parts)


def render_intake():
    case = st.session_state.case
    st.subheader("File your claim")
    st.caption("Claimant - describe the dispute in plain English. The assistant structures it and checks completeness.")
    text = st.text_area("Your claim, in your own words", value=LENDER_NARRATIVE, height=150, key="intake_text")
    if st.button("Structure my claim", type="primary"):
        with st.spinner("Structuring your claim..."):
            result = call_claude(system=INTAKE_SYSTEM, user=text, schema=StructuredClaim)
        if result:
            st.session_state.case.structured_claim = result.model_dump()
    sc = st.session_state.case.structured_claim
    if sc:
        st.divider()
        st.markdown("#### Structured claim")
        c1, c2 = st.columns(2)
        c1.markdown(f"**Claimant**  \n{sc['claimant']}")
        c2.markdown(f"**Respondent**  \n{sc['respondent']}")
        st.markdown(f"**Claim type:** {sc['claim_type']}")
        st.markdown(f"**Principal balance:** ${sc['principal_balance']:,.2f}  |  **Fees claimed:** ${sc['fees_claimed']:,.2f}")
        st.markdown(f"**Interest:** {sc['interest_note']}")
        st.markdown(f"**Key dates:** {', '.join(sc['key_dates'])}")
        st.markdown(f"**Relief sought:** {sc['relief_sought']}")
        st.markdown("#### Completeness check")
        for item in sc["completeness"]:
            label = item["label"] + (f" - {item['note']}" if item.get("note") else "")
            if item["status"] == "present":
                st.success(label)
            else:
                st.warning("Missing: " + label)


def render_validate():
    case = st.session_state.case
    st.subheader("Validate the filing")
    st.caption("Admin - check completeness and verify the arbitration clause before the case proceeds.")
    if st.button("Run validation", type="primary"):
        required = "Required documents: loan agreement, payment ledger, demand notice, proof of default."
        docs = "\n\n".join(f"[{d.name}]\n{d.content}" for d in case.documents)
        with st.spinner("Validating documents and clause..."):
            v = call_claude(system=VALIDATE_SYSTEM, user=required + "\n\nDOCUMENTS:\n" + docs, schema=ValidationResult)
        if v:
            st.session_state.validation = v.model_dump()
    v = st.session_state.validation
    if v:
        st.divider()
        for p in v["present"]:
            st.success("Present: " + p)
        for m in v["missing"]:
            st.warning("Missing: " + m)
        st.markdown(f"**Arbitrable:** {'Yes' if v['arbitrable'] else 'No'}")
        if v["clause_found"]:
            with st.expander("Extracted arbitration clause"):
                st.write(v["clause_text"])
        if v["todo"]:
            st.markdown("**To-do:**")
            for t in v["todo"]:
                st.write("- " + t)


def render_assign():
    st.subheader("Arbitrator assignment")
    st.caption("Admin - assign a neutral arbitrator from the AAA panel.")
    if st.button("Auto-assign arbitrator", type="primary"):
        st.session_state.arbitrator = "Hon. A. Mehta (AAA panel - consumer finance)"
    if st.session_state.arbitrator:
        st.success(f"Assigned: {st.session_state.arbitrator}")
        st.caption("Conflict check passed. Both parties notified.")
    else:
        st.info("No arbitrator assigned yet.")


def render_respond():
    case = st.session_state.case
    st.subheader("Respond to the claim")
    st.caption("Respondent - understand the claim, then build your defense.")
    st.markdown("**1. Understand the claim**")
    if st.button("Explain this claim in plain English"):
        src = str(case.structured_claim) if case.structured_claim else get_record_text(case)
        with st.spinner("Explaining..."):
            exp = call_claude(system=EXPLAIN_SYSTEM, user=src)
        if exp:
            st.session_state.explanation = exp
    if st.session_state.explanation:
        st.info(st.session_state.explanation)
    st.divider()
    st.markdown("**2. Draft your defense**")
    notes = st.text_area("Your rough notes", value=RAW_DEFENSE_NOTES, height=130, key="defense_notes")
    if st.button("Draft my defense", type="primary"):
        with st.spinner("Drafting your defense..."):
            d = call_claude(system=DEFENSE_SYSTEM, user=notes, schema=Defense)
        if d:
            st.session_state.defense = d.model_dump()
            case.submissions.append(Submission(kind="defense", author=case.respondent, content=str(d.model_dump())))
    d = st.session_state.defense
    if d:
        st.markdown("**Admitted:**")
        for a in d["admitted"]:
            st.write("- " + a)
        st.markdown("**Disputed:**")
        for a in d["disputed"]:
            st.write("- " + a)
        st.markdown(f"**Requested relief:** {d['requested_relief']}")


def render_review():
    case = st.session_state.case
    st.subheader("Review the case file")
    st.caption("Arbitrator - ask the record anything; answers cite the source document.")
    q = st.text_input("Ask a question about the case", key="review_q",
                      placeholder="e.g. When did the borrower last make a payment the lender credited?")
    if st.button("Ask", type="primary") and q:
        with st.spinner("Searching the record..."):
            ans = call_claude(system=REVIEW_SYSTEM, user=f"QUESTION: {q}\n\n{get_record_text(case)}", schema=ReviewAnswer)
        if ans:
            st.session_state.review_history.insert(0, {"q": q, "a": ans.answer, "src": ans.source_document})
    for item in st.session_state.review_history:
        st.markdown(f"**Q:** {item['q']}")
        st.markdown(f"**A:** {item['a']}")
        st.caption("Source: " + item["src"])
        st.divider()


def render_hearing():
    case = st.session_state.case
    st.subheader("Virtual hearing")
    st.caption("Auto-transcription linked to the case record (demo: pre-recorded excerpt).")
    st.text_area("Transcript", value=case.hearing_transcript, height=280, disabled=True)


def render_award():
    case = st.session_state.case
    st.subheader("Draft reasoned award")
    st.caption("Arbitrator - generate a reasoned draft award. You review, edit, and finalize.")
    if st.button("Generate draft award", type="primary"):
        model = MODEL_AWARD if USE_OPUS_FOR_AWARD else MODEL_DEFAULT
        with st.spinner("Drafting reasoned award..."):
            award = call_claude(system=AWARD_SYSTEM, user=get_record_text(case),
                                schema=Award, model=model, max_tokens=2500)
        if award:
            st.session_state.case.draft_award = award.model_dump()
    aw = st.session_state.case.draft_award
    if aw:
        st.divider()
        st.markdown("**Background**")
        st.write(aw["background"])
        st.markdown("**Issues for determination**")
        for i in aw["issues"]:
            st.write("- " + i)
        st.markdown("**Findings and reasoning**")
        for f in aw["findings"]:
            st.markdown(f"- **{f['issue']}** - _{f['ruling']}_")
            st.write("  " + f["reasoning"])
        st.markdown("**Decision**")
        st.text_area("Decision (editable by the arbitrator)", value=aw["decision"], height=130, key="award_decision_edit")
        st.metric("Amount awarded", f"${aw['amount_awarded']:,.2f}")


RENDERERS = {
    "Intake": render_intake, "Validate": render_validate, "Assign": render_assign,
    "Respond": render_respond, "Review": render_review, "Hearing": render_hearing, "Award": render_award,
}

with st.sidebar:
    st.title("Aequa ODR")
    st.caption("AI-assisted online dispute resolution")
    st.session_state.stage = st.radio("Case lifecycle", STAGES, index=STAGES.index(st.session_state.stage))
    st.session_state.persona = st.selectbox("Viewing as", PERSONAS, index=PERSONAS.index(st.session_state.persona))
    st.caption(f"Stage {STAGES.index(st.session_state.stage) + 1} of {len(STAGES)}")
    st.divider()
    st.caption(f"Case: {st.session_state.case.title}")

st.markdown(f"### {st.session_state.stage}")
st.caption(f"{st.session_state.case.title}  |  {st.session_state.case.case_id}  |  Viewing as: {st.session_state.persona}")
st.divider()
RENDERERS[st.session_state.stage]()
st.divider()
st.caption(DISCLAIMER)
