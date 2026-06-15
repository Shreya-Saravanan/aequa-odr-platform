from pydantic import BaseModel


class CompletenessItem(BaseModel):
    label: str
    status: str  # "present" | "missing"
    note: str = ""


class StructuredClaim(BaseModel):
    claimant: str
    respondent: str
    claim_type: str
    principal_balance: float
    fees_claimed: float
    interest_note: str
    key_dates: list[str]
    relief_sought: str
    completeness: list[CompletenessItem]


class Finding(BaseModel):
    issue: str
    ruling: str  # "credited" | "disallowed" | "rejected" | "granted"
    reasoning: str


class Award(BaseModel):
    background: str
    issues: list[str]
    findings: list[Finding]
    decision: str
    amount_awarded: float


class ReviewAnswer(BaseModel):
    answer: str
    source_document: str


class Defense(BaseModel):
    admitted: list[str]
    disputed: list[str]
    requested_relief: str


class ValidationResult(BaseModel):
    present: list[str]
    missing: list[str]
    clause_found: bool
    clause_text: str
    arbitrable: bool
    todo: list[str]
