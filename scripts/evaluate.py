import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.models import ClaimCase
from app.service import run_analysis
ROOT=Path(__file__).resolve().parents[1]
public=json.load(open(ROOT/"data/public_test_cases.json"))
extra=json.load(open(ROOT/"data/generated_cases/additional_cases.json"))
expected=json.load(open(ROOT/"data/expected_decisions.json"))
rows=[]
for c in public+extra:
    r=run_analysis(ClaimCase.model_validate(c))
    rows.append({"case_id":c["case_id"],"expected":expected[c["case_id"]],"actual":r.decision,
                 "correct":r.decision==expected[c["case_id"]],"confidence":r.confidence,
                 "validation":r.validation.status,"citations":len(r.citations),
                 "payable_amount_inr":r.payable_amount_inr})
n=len(rows); accuracy=sum(x["correct"] for x in rows)/n
citation_hit=sum(x["citations"]>0 for x in rows)/n
validation_pass=sum(x["validation"]=="PASS" for x in rows)/n
abstain=sum(x["actual"]=="NEEDS_REVIEW" for x in rows)
out={"summary":{"cases":n,"decision_accuracy":accuracy,"citation_hit_rate":citation_hit,
                "validation_pass_rate":validation_pass,"abstentions":abstain},
     "results":rows}
json.dump(out,open(ROOT/"evaluation_results.json","w"),indent=2)
print(json.dumps(out["summary"],indent=2))
for x in rows:
    print(x)
