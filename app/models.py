from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

DecisionStatus = Literal[
    "ADMISSIBLE", "ADMISSIBLE_WITH_LIMITS", "PARTIALLY_ADMISSIBLE",
    "NOT_ADMISSIBLE", "NEEDS_REVIEW"
]

class ClaimCase(BaseModel):
    case_id: str
    policy_id: str
    policy_start_date: str
    claim_date: str
    sum_insured_inr: float
    continuous_coverage_months: int = 0
    prior_insurer_continuous_years: int = 0
    patient: Dict[str, Any]
    hospital: Dict[str, Any]
    treatment: Dict[str, Any]
    expenses_inr: Dict[str, float]
    documents: List[str] = Field(default_factory=list)
    task: str
    evidence_context: Optional[Dict[str, Any]] = None
    expense_timing: Optional[Dict[str, Any]] = None
    prior_policy: Optional[Dict[str, Any]] = None

class Citation(BaseModel):
    claim: str
    source: str = "policy.pdf"
    page: int
    section: str
    chunk_id: str

class Finding(BaseModel):
    dimension: str
    conclusion: str
    citations: List[str] = Field(default_factory=list)

class AgentTrace(BaseModel):
    agent: str
    action: str
    result_count: Optional[int] = None
    elapsed_ms: float

class Validation(BaseModel):
    status: Literal["PASS", "FAIL"]
    unsupported_claims: List[str] = Field(default_factory=list)

class AnalysisResponse(BaseModel):
    case_id: str
    decision: DecisionStatus
    confidence: float
    key_findings: List[str]
    applicable_limits: List[str]
    missing_evidence: List[str]
    citations: List[Citation]
    validation: Validation
    trace: List[AgentTrace]
    payable_amount_inr: Optional[float] = None
