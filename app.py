import streamlit as st

from data.seed import build_seed_case, Submission, LENDER_NARRATIVE, RAW_DEFENSE_NOTES
from modules.llm import call_claude, MODEL_DEFAULT, MODEL_AWARD, USE_OPUS_FOR_AWARD
from modules.schemas import StructuredClaim, Award, ReviewAnswer, Defense, ValidationResult

st.set_page_config(page_title="Aequa ODR", page_icon="balance", layout="wide")

STAGES = ["Intake", "Validate", "Assign", "Respond", "Review", "Hearing", "Award"]
PERSONAS = ["Claimant (lender)", "Respondent (borrower)", "Arbitrator", "Admin"]
DISCLAIMER = ("AI-assisted - not legal advice. A human reviews and decides at every step. "
              "Aligned with ICODR Online Dispute Resolution Standards.")

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer { visibility: hidden !important; }
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; }

/* ── Page background ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(145deg, #eef0fa 0%, #f4f0ff 55%, #fef4f8 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #ebebf5 !important;
    box-shadow: 4px 0 24px rgba(80,80,180,0.06) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; padding-bottom: 1.5rem; }

/* ── Radio → nav items ── */
div[data-testid="stRadio"] > div { gap: 0 !important; }
div[data-testid="stRadio"] div[data-baseweb="radio"] > div:first-child { display: none !important; }
div[data-testid="stRadio"] label {
    display: flex !important; align-items: center; width: 100% !important;
    padding: 9px 16px !important; border-radius: 10px !important; margin: 1px 0 !important;
    cursor: pointer; font-size: 14px !important; font-weight: 500 !important;
    color: #7474a0 !important; background: transparent !important;
    transition: background 0.15s ease, color 0.15s ease !important; border: none !important;
}
div[data-testid="stRadio"] label:hover { background: #f0f0fa !important; color: #1a2b5e !important; }
div[data-testid="stRadio"] label:has(input:checked) {
    background: #eef0ff !important; color: #1a2b5e !important; font-weight: 700 !important;
}

/* ── Selectbox ── */
[data-testid="stSidebar"] .stSelectbox > div > div {
    border-radius: 10px !important; border: 1.5px solid #e8e8f5 !important;
    background: #fafafe !important; font-size: 13px !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#1a2b5e 0%,#253580 100%) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 14px !important; padding: 10px 22px !important;
    box-shadow: 0 4px 14px rgba(26,43,94,0.28) !important;
    transition: all 0.2s ease !important; letter-spacing: 0.2px !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(26,43,94,0.38) !important; transform: translateY(-1px) !important;
}

/* ── Secondary / outline button ── */
.stButton > button[kind="secondary"] {
    background: white !important; color: #1a2b5e !important;
    border: 1.5px solid #dde0f0 !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 14px !important; transition: all 0.2s ease !important;
}
.stButton > button[kind="secondary"]:hover { background: #f0f0fa !important; border-color: #1a2b5e !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: white !important; color: #1a2b5e !important;
    border: 1.5px solid #dde0f0 !important; border-radius: 10px !important;
    font-weight: 600 !important; transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover { background: #f0f0fa !important; border-color: #1a2b5e !important; }

/* ── Form submit ── */
div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg,#1a2b5e 0%,#253580 100%) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; padding: 10px 22px !important;
    box-shadow: 0 4px 14px rgba(26,43,94,0.28) !important; transition: all 0.2s ease !important;
}
div[data-testid="stFormSubmitButton"] > button:hover {
    box-shadow: 0 6px 20px rgba(26,43,94,0.38) !important; transform: translateY(-1px) !important;
}

/* ── Form container ── */
[data-testid="stForm"] {
    border: 1.5px solid #ebebf5 !important; border-radius: 14px !important;
    background: #fafafe !important; box-shadow: 0 2px 8px rgba(80,80,180,0.04) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    border-radius: 8px !important; border: 1.5px solid #e0e0f0 !important;
    background: white !important; font-size: 14px !important; color: #2a2a4a !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {
    border-color: #1a2b5e !important; box-shadow: 0 0 0 3px rgba(26,43,94,0.1) !important;
}
.stSelectbox > div > div { border-radius: 8px !important; border: 1.5px solid #e0e0f0 !important; background: white !important; }
.stTextInput label, .stTextArea label, .stNumberInput label,
.stSelectbox label, .stToggle label {
    font-size: 13px !important; font-weight: 600 !important; color: #5a5a7a !important;
}

/* ── Metric ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg,#1a2b5e 0%,#2d3f7a 100%) !important;
    border-radius: 14px !important; padding: 16px 20px !important;
    box-shadow: 0 4px 20px rgba(26,43,94,0.22) !important;
}
[data-testid="stMetric"] label { color: rgba(255,255,255,0.7) !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: white !important; }

/* ── Alerts ── */
.stSuccess { border-radius: 10px !important; }
.stInfo    { border-radius: 10px !important; }
.stWarning { border-radius: 10px !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    border: 1.5px solid #ebebf5 !important; border-radius: 10px !important; background: white !important;
}

/* ── Divider ── */
hr { border: none !important; border-top: 1.5px solid #ebebf5 !important; margin: 20px 0 !important; }

/* ── Typography ── */
h1,h2,h3 { color: #1a2b5e !important; font-weight: 700 !important; letter-spacing: -0.3px !important; }
h4,h5 { color: #2a2a4a !important; font-weight: 600 !important; }
p { color: #3a3a5a; line-height: 1.6; }
[data-testid="stCaptionContainer"] p { color: #9494b0 !important; font-size: 12.5px !important; }
[data-testid="stSidebar"] h1 {
    font-size: 20px !important; font-weight: 800 !important;
    color: #1a2b5e !important; letter-spacing: -0.5px !important;
}

/* ── Disabled textarea (hearing transcript) ── */
.stTextArea [disabled] { background: #f8f8fd !important; color: #4a4a6a !important; border-color: #ebebf5 !important; }
</style>
"""

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
if "award_finalized" not in st.session_state:
    st.session_state.award_finalized = False

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


def award_to_markdown(case) -> str:
    aw = case.draft_award
    lines = [
        "# ARBITRAL AWARD",
        "",
        f"**Case No.:** {case.case_id}  ",
        f"**{case.claimant} v. {case.respondent}**  ",
        "**Seat:** Boston, MA  ",
        "**Rules:** AAA Consumer Arbitration Rules  ",
        "**Governing Law:** Federal Arbitration Act and Massachusetts law  ",
        "",
        "---",
        "",
        "## I. Background",
        "",
        aw["background"],
        "",
        "## II. Issues for Determination",
        "",
    ]
    for i, issue in enumerate(aw["issues"], 1):
        lines.append(f"{i}. {issue}")
    lines += ["", "## III. Findings and Reasoning", ""]
    for i, f in enumerate(aw["findings"], 1):
        lines += [
            f"### {i}. {f['issue']}",
            "",
            f"**Ruling:** {f['ruling'].capitalize()}",
            "",
            f["reasoning"],
            "",
        ]
    lines += [
        "## IV. Decision",
        "",
        aw["decision"],
        "",
        f"**AMOUNT AWARDED: ${aw['amount_awarded']:,.2f}**",
        "",
        "---",
        "",
        "_________________  ",
        "**Arbitrator**  ",
        "Date: ____________________",
        "",
        "---",
        "",
        f"*{DISCLAIMER}*",
    ]
    return "\n".join(lines)


def render_stage_header():
    current_idx = STAGES.index(st.session_state.stage)
    segments = "".join(
        f'<div style="flex:1;height:4px;border-radius:4px;margin:0 3px;background:'
        f'{"#1a2b5e" if i < current_idx else ("#c9a227" if i == current_idx else "#dde0ec")}'
        f';transition:background 0.3s;"></div>'
        for i in range(len(STAGES))
    )
    st.markdown(
        f'<div style="display:flex;align-items:center;margin:-8px 0 6px 0;">{segments}</div>'
        f'<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px;">'
        f'<span style="font-size:24px;font-weight:800;color:#1a2b5e;letter-spacing:-0.5px;">'
        f'{st.session_state.stage}</span>'
        f'<span style="font-size:11px;font-weight:700;color:#b0b0c8;letter-spacing:1px;">'
        f'STEP {current_idx + 1} OF {len(STAGES)}</span></div>',
        unsafe_allow_html=True,
    )
    st.caption(
        f"{st.session_state.case.title}  ·  {st.session_state.case.case_id}"
        f"  ·  {st.session_state.persona}"
    )


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
        with st.form("intake_edit_form"):
            claim_type = st.text_input("Claim type", value=sc["claim_type"])
            col1, col2 = st.columns(2)
            principal_balance = col1.number_input("Principal balance ($)", value=float(sc["principal_balance"]), min_value=0.0, format="%.2f")
            fees_claimed = col2.number_input("Fees claimed ($)", value=float(sc["fees_claimed"]), min_value=0.0, format="%.2f")
            interest_note = st.text_input("Interest note", value=sc["interest_note"])
            key_dates = st.text_input("Key dates (comma-separated)", value=", ".join(sc["key_dates"]))
            relief_sought = st.text_area("Relief sought", value=sc["relief_sought"], height=80)
            intake_saved = st.form_submit_button("Save changes")
        if intake_saved:
            sc["claim_type"] = claim_type
            sc["principal_balance"] = principal_balance
            sc["fees_claimed"] = fees_claimed
            sc["interest_note"] = interest_note
            sc["key_dates"] = [d.strip() for d in key_dates.split(",") if d.strip()]
            sc["relief_sought"] = relief_sought.strip()
            st.session_state.case.structured_claim = sc
            st.toast("Saved")
        st.markdown("#### Completeness check")
        _items = st.session_state.case.structured_claim["completeness"]
        for item in sorted(_items, key=lambda x: x["status"] != "present"):
            icon = "✅" if item["status"] == "present" else "⚠️"
            st.markdown(f"{icon} &nbsp; **{item['label']}**")
            if item.get("note"):
                st.caption(f"    {item['note']}")


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
        with st.form("defense_edit_form"):
            admitted_text = st.text_area("Admitted (one item per line)", value="\n".join(d["admitted"]), height=120)
            disputed_text = st.text_area("Disputed (one item per line)", value="\n".join(d["disputed"]), height=120)
            relief_text = st.text_area("Requested relief", value=d["requested_relief"], height=80)
            defense_saved = st.form_submit_button("Save defense")
        if defense_saved:
            d["admitted"] = [line.strip() for line in admitted_text.splitlines() if line.strip()]
            d["disputed"] = [line.strip() for line in disputed_text.splitlines() if line.strip()]
            d["requested_relief"] = relief_text.strip()
            st.session_state.defense = d
            for sub in case.submissions:
                if sub.kind == "defense":
                    sub.content = str(d)
            st.toast("Saved")


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
        RULING_OPTIONS = ["credited", "disallowed", "rejected", "granted"]
        with st.form("award_edit_form"):
            st.markdown("**Background**")
            background = st.text_area("Background", value=aw["background"], height=120, label_visibility="collapsed")
            st.markdown("**Issues for determination**")
            for i in aw["issues"]:
                st.write("- " + i)
            st.markdown("**Findings and reasoning**")
            updated_findings = []
            for idx, f in enumerate(aw["findings"]):
                st.markdown(f"_Finding {idx + 1}_")
                col1, col2 = st.columns([3, 1])
                issue = col1.text_input("Issue", value=f["issue"], key=f"finding_issue_{idx}")
                ruling = col2.selectbox(
                    "Ruling", options=RULING_OPTIONS,
                    index=RULING_OPTIONS.index(f["ruling"]) if f["ruling"] in RULING_OPTIONS else 0,
                    key=f"finding_ruling_{idx}",
                )
                reasoning = st.text_area("Reasoning", value=f["reasoning"], key=f"finding_reasoning_{idx}", height=80)
                updated_findings.append({"issue": issue, "ruling": ruling, "reasoning": reasoning})
            st.markdown("**Decision**")
            decision = st.text_area("Decision", value=aw["decision"], height=130)
            amount = st.number_input("Amount awarded ($)", value=float(aw["amount_awarded"]), min_value=0.0, format="%.2f")
            award_saved = st.form_submit_button("Save award")
        if award_saved:
            aw["background"] = background
            aw["findings"] = updated_findings
            aw["decision"] = decision
            aw["amount_awarded"] = amount
            st.session_state.case.draft_award = aw
            st.toast("Saved")
        st.metric("Amount awarded", f"${st.session_state.case.draft_award['amount_awarded']:,.2f}")

        st.divider()
        if st.toggle("Preview final award"):
            aw = st.session_state.case.draft_award
            st.markdown(
                "<h1 style='text-align:center;'>ARBITRAL AWARD</h1>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='text-align:center;'>"
                f"<b>Case No.:</b> {case.case_id}&nbsp;&nbsp;|&nbsp;&nbsp;"
                f"<b>{case.claimant} v. {case.respondent}</b><br>"
                f"Seat: Boston, MA &nbsp;|&nbsp; AAA Consumer Arbitration Rules<br>"
                f"Governed by the FAA and Massachusetts law"
                f"</p>",
                unsafe_allow_html=True,
            )
            st.divider()
            st.markdown("## I. Background")
            st.write(aw["background"])
            st.markdown("## II. Issues for Determination")
            for i, issue in enumerate(aw["issues"], 1):
                st.write(f"{i}. {issue}")
            st.markdown("## III. Findings and Reasoning")
            for i, f in enumerate(aw["findings"], 1):
                st.markdown(f"### {i}. {f['issue']}")
                st.markdown(f"**Ruling:** {f['ruling'].capitalize()}")
                st.write(f["reasoning"])
            st.markdown("## IV. Decision")
            st.write(aw["decision"])
            st.markdown(f"**AMOUNT AWARDED: ${aw['amount_awarded']:,.2f}**")
            st.divider()
            st.markdown("\_________________  \n**Arbitrator**  \nDate: ____________________")
            st.divider()
            st.caption(DISCLAIMER)

        col_fin, col_dl = st.columns(2)
        with col_fin:
            if not st.session_state.award_finalized:
                if st.button("Finalize award"):
                    st.session_state.award_finalized = True
                    st.success("Award finalized.")
            else:
                st.success("Award finalized.")
        with col_dl:
            st.download_button(
                "Download award (Markdown)",
                data=award_to_markdown(st.session_state.case),
                file_name=f"award_{case.case_id}.md",
                mime="text/markdown",
            )


RENDERERS = {
    "Intake": render_intake, "Validate": render_validate, "Assign": render_assign,
    "Respond": render_respond, "Review": render_review, "Hearing": render_hearing, "Award": render_award,
}

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        '<div style="padding:0 8px 20px 8px;">'
        '<div style="font-size:19px;font-weight:900;color:#1a2b5e;letter-spacing:-0.5px;">'
        'AEQUA <span style="color:#c9a227;">⚖</span> ODR</div>'
        '<div style="font-size:10px;color:#b0b0c8;font-weight:600;margin-top:3px;letter-spacing:1px;">'
        'AI-ASSISTED DISPUTE RESOLUTION</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-size:10px;font-weight:700;color:#b0b0c8;letter-spacing:1.5px;'
        'padding:0 8px;margin:0 0 4px 0;">CASE LIFECYCLE</p>',
        unsafe_allow_html=True,
    )
    st.session_state.stage = st.radio(
        "stage", STAGES, index=STAGES.index(st.session_state.stage), label_visibility="collapsed"
    )
    st.divider()
    st.markdown(
        '<p style="font-size:10px;font-weight:700;color:#b0b0c8;letter-spacing:1.5px;'
        'padding:0 8px;margin:0 0 6px 0;">CASE FILE</p>',
        unsafe_allow_html=True,
    )
    _c = st.session_state.case
    _chk = lambda ok: "✅" if ok else "—"
    st.caption(f"📄 Documents: {len(_c.documents)}")
    st.caption(f"{_chk(_c.structured_claim)} Structured claim")
    _has_defense = any(s.kind == "defense" for s in _c.submissions)
    st.caption(f"{_chk(_has_defense)} Defense submitted")
    st.caption(f"💬 Review Q&A: {len(st.session_state.review_history)}")
    _award_ok = _c.draft_award is not None
    _finalized = st.session_state.award_finalized
    st.caption(f"{_chk(_award_ok)} Draft award{'  🔒 Finalized' if _finalized else ''}")
    st.divider()
    st.markdown(
        '<p style="font-size:10px;font-weight:700;color:#b0b0c8;letter-spacing:1.5px;'
        'padding:0 8px;margin:0 0 4px 0;">VIEWING AS</p>',
        unsafe_allow_html=True,
    )
    st.session_state.persona = st.selectbox(
        "persona", PERSONAS, index=PERSONAS.index(st.session_state.persona), label_visibility="collapsed"
    )
    st.markdown(
        f'<div style="margin-top:12px;padding:12px 14px;background:#f4f4fa;border-radius:10px;">'
        f'<div style="font-size:10px;color:#b0b0c8;font-weight:600;letter-spacing:0.5px;">CASE ID</div>'
        f'<div style="font-size:13px;font-weight:700;color:#1a2b5e;margin-top:2px;">'
        f'{st.session_state.case.case_id}</div>'
        f'<div style="font-size:11px;color:#9494b0;margin-top:2px;">'
        f'Stage {STAGES.index(st.session_state.stage) + 1} of {len(STAGES)}</div></div>',
        unsafe_allow_html=True,
    )

render_stage_header()
st.divider()
RENDERERS[st.session_state.stage]()
st.divider()
st.markdown(
    f'<p style="font-size:11.5px;color:#b0b0c8;text-align:center;padding:4px 0;">{DISCLAIMER}</p>',
    unsafe_allow_html=True,
)
