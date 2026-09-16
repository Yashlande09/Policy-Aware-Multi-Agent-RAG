from fastapi import FastAPI, HTTPException
from app.models import ClaimCase
from app.service import run_analysis
app=FastAPI(title="Aptino Policy-Aware Multi-Agent RAG",version="1.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"aptino-claim-decision-engine"}

@app.post("/analyze")
def analyze_claim(case: ClaimCase):
    try:
        return run_analysis(case).model_dump()
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Analysis failed safely: {type(e).__name__}")
