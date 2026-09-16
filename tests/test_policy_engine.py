import json
from pathlib import Path
from app.models import ClaimCase
from app.service import run_analysis
ROOT=Path(__file__).resolve().parents[1]
CASES=json.load(open(ROOT/"data/public_test_cases.json"))
EXPECTED=json.load(open(ROOT/"data/expected_decisions.json"))

def test_all_public_cases_have_decisions():
    for c in CASES:
        r=run_analysis(ClaimCase.model_validate(c))
        assert r.decision in {"ADMISSIBLE","ADMISSIBLE_WITH_LIMITS","PARTIALLY_ADMISSIBLE","NOT_ADMISSIBLE","NEEDS_REVIEW"}
        assert r.citations or r.decision=="NEEDS_REVIEW"

def test_required_abstentions():
    by={c["case_id"]:c for c in CASES}
    assert run_analysis(ClaimCase.model_validate(by["PUB-006"])).decision=="NEEDS_REVIEW"
    assert run_analysis(ClaimCase.model_validate(by["PUB-011"])).decision=="NEEDS_REVIEW"
