# Aequa ODR - AI-assisted Online Dispute Resolution

A working prototype of an end-to-end **Online Dispute Resolution (ODR)** platform for
arbitration, built for the Code the Future of Justice hackathon (vibeodr.com, Suffolk Law School).
One real dispute moves through the full lifecycle, and Claude assists at every stage where the
quality of justice usually depends on whether a party can afford a lawyer.

## The problem
Arbitration is hard to navigate for ordinary people: they struggle to interpret legal
requirements, submit the wrong or incomplete documents, and the strength of their case depends on
their ability to articulate it. Arbitrators, meanwhile, drown in unstructured documents and spend
hours consolidating a reasoned award. These pain points were drawn from real persona and
journey-map research across five roles - Claimant, Respondent, Arbitrator, Advocate, and
Administrator.

## What it does
A single case - *Pinewood Bank, N.A. v. Jordan Carter*, a $20,000 personal loan default -
travels through seven lifecycle stages with a persona switcher. Five AI features:

- **Intake (Claimant):** plain-English description -> structured claim + completeness check.
- **Validate (Admin):** checks document completeness and verifies the arbitration clause.
- **Respond (Respondent):** explains the claim in plain English, then turns rough notes into a
  structured statement of defense.
- **Review (Arbitrator):** ask the case file any question; answers cite the source document.
- **Award (Arbitrator):** drafts a *reasoned* award - weighing each disputed item against the
  contract - which the arbitrator edits and finalizes.

The sample dispute has three contested items the award must reason through: $1,100 in unposted
payments (credited), a $750 default fee not in the contract (disallowed), and an alleged verbal
forbearance (rejected under the agreement's integration clause) - landing on a net $13,700.

## Design principles
- **Not legal advice.** The AI structures and informs; a human (party, then arbitrator) reviews
  and decides at every step - a deliberate guard against unauthorized practice of law.
- **US / Massachusetts framing.** Governed by the Federal Arbitration Act and MA law; AAA
  Consumer Arbitration Rules; aligned with ICODR ODR Standards.
- **Jurisdiction-configurable.** The legal layer is configuration, not core - the same engine
  generalizes to other arbitral regimes.

## Tech stack
Python, Streamlit, the Anthropic Claude API (Sonnet 4.6 by default; Opus 4.8 optional for the
award), Pydantic for typed, validated AI outputs.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# add your key: copy .streamlit/secrets.toml.example to .streamlit/secrets.toml and paste it in
streamlit run app.py
```

## Deploy
Push to GitHub, then deploy on Streamlit Community Cloud and add `ANTHROPIC_API_KEY` under the
app's Secrets settings.

## Cost
AI cost is roughly $0.17 per full case on Claude Sonnet 4.6.
