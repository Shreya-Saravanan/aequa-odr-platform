from pydantic import BaseModel, Field


class Document(BaseModel):
    name: str
    doc_type: str
    uploaded_by: str
    content: str


class Submission(BaseModel):
    kind: str
    author: str
    content: str


class Case(BaseModel):
    case_id: str
    title: str
    claimant: str
    respondent: str
    current_stage: str = "Intake"
    documents: list[Document] = Field(default_factory=list)
    submissions: list[Submission] = Field(default_factory=list)
    hearing_transcript: str = ""
    structured_claim: dict | None = None
    draft_award: dict | None = None


LENDER_NARRATIVE = (
    "Pinewood Bank gave a $20,000 personal loan to Jordan Carter in March 2024. They paid for a "
    "while but have missed every payment since November 2025. We're owed about $14,800 plus a "
    "default fee and interest, and they haven't responded to our demand notice. We want to recover "
    "the outstanding amount through arbitration."
)

RAW_DEFENSE_NOTES = (
    "I did pay November and December - I have the bank receipts. That $750 fee was never in my "
    "contract, I checked. And back in October I called and a rep named Sarah told me I could skip "
    "three months because I'd lost my job. I'm not trying to dodge what I actually owe."
)

LOAN_AGREEMENT = """PERSONAL LOAN AGREEMENT
Lender: Pinewood Bank, N.A. (Boston, Massachusetts)
Borrower: Jordan Carter
Date: March 14, 2024

1. Principal. The Lender advances $20,000.00 to the Borrower.
2. Interest. Fixed Annual Percentage Rate of 12.5%.
3. Repayment. Forty-eight (48) equal monthly installments of $550.00, due on the 14th of each
   month, beginning April 14, 2024.
4. Fees. The only charges payable under this Agreement are the interest set forth in Section 2.
   No origination, servicing, or default fees of any kind apply.
5. Governing Law. This Agreement is governed by the laws of the Commonwealth of Massachusetts
   and the Federal Arbitration Act.
6. Arbitration. Any dispute arising out of or relating to this Agreement shall be resolved by
   binding arbitration administered by the American Arbitration Association under its Consumer
   Arbitration Rules. The seat of arbitration shall be Boston, Massachusetts.
7. Entire Agreement (Integration). This Agreement constitutes the entire agreement between the
   parties and supersedes all prior understandings. No modification, including any forbearance or
   change to the payment schedule, is valid unless made in writing and signed by both parties.

Signed: Pinewood Bank, N.A.  /  Jordan Carter"""

LEDGER = """PAYMENT LEDGER - Account AEQ-LN-20240314 (Pinewood Bank, N.A.)
Borrower: Jordan Carter | Original principal: $20,000.00 | Monthly installment: $550.00

Payments received on time: April 2024 through October 2025.
Status from November 2025 onward: NO PAYMENTS RECORDED.
  - Nov 2025: missed
  - Dec 2025: missed
  - Jan 2026: missed
  - Feb 2026: missed
  - Mar 2026: missed
  - Apr 2026: missed

Outstanding principal balance: $14,800.00
Default servicing fee assessed: $750.00
Total due (excluding accruing interest): $15,550.00"""

DEMAND_NOTICE = """NOTICE OF DEFAULT AND DEMAND
From: Pinewood Bank, N.A.   To: Jordan Carter   Date: May 2, 2026

You are in default under your Personal Loan Agreement dated March 14, 2024, having failed to make
payments since November 2025. Demand is hereby made for the outstanding balance of $14,800.00, a
default servicing fee of $750.00, and accruing interest - a total of $15,550.00 plus interest.

Pursuant to Section 6 of the Agreement, the Bank will refer this matter to binding arbitration
before the American Arbitration Association if payment is not received within fifteen (15) days."""

EVIDENCE_TRANSFERS = """BANK TRANSFER CONFIRMATIONS - submitted by Jordan Carter (Respondent)

Confirmation #TRX-558201: $550.00 transferred Nov 14, 2025 to Pinewood Bank,
  reference "Loan AEQ-LN-20240314". Status: Completed.
Confirmation #TRX-561744: $550.00 transferred Dec 13, 2025 to Pinewood Bank,
  reference "Loan AEQ-LN-20240314". Status: Completed.

Total: $1,100.00. Neither of these two payments appears on the Bank's payment ledger."""

HEARING = """VIRTUAL HEARING - EXCERPT (Case AEQ-2026-0417)

Arbitrator: Mr. Carter, the Bank says no payments since November. Your response?
Carter: I paid November and December - $550 each, by bank transfer. I have the confirmation
  numbers. They just never showed up on the Bank's statement.
Arbitrator: And the $750 fee?
Carter: That was never in my contract. I read it again.
Carter: Also, back in October I called and spoke to a representative, Sarah. I'd lost my job.
  She told me I could pause payments for three months. I believed her.
Bank's counsel: We have no record of any such call, and no written forbearance was ever issued.
  The agreement requires any change to be in writing.
Arbitrator: Noted. I will address each item in the award."""


def build_seed_case() -> Case:
    return Case(
        case_id="AEQ-2026-0417",
        title="Pinewood Bank, N.A. v. Jordan Carter - personal loan default",
        claimant="Pinewood Bank, N.A.",
        respondent="Jordan Carter",
        documents=[
            Document(name="Personal Loan Agreement", doc_type="loan_agreement",
                     uploaded_by="Claimant", content=LOAN_AGREEMENT),
            Document(name="Payment Ledger", doc_type="ledger",
                     uploaded_by="Claimant", content=LEDGER),
            Document(name="Notice of Default and Demand", doc_type="demand_notice",
                     uploaded_by="Claimant", content=DEMAND_NOTICE),
            Document(name="Bank Transfer Confirmations", doc_type="evidence",
                     uploaded_by="Respondent", content=EVIDENCE_TRANSFERS),
        ],
        hearing_transcript=HEARING,
    )


if __name__ == "__main__":
    print(build_seed_case().model_dump_json(indent=2))
