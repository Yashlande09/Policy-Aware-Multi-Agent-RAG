from functools import lru_cache
from app.config import POLICY_PATH
from app.retrieval.hybrid import HybridRetriever
from app.models import ClaimCase, AnalysisResponse
from app.agents.workflow import analyze

@lru_cache(maxsize=1)
def get_retriever():
    return HybridRetriever(POLICY_PATH)

def run_analysis(case: ClaimCase)->AnalysisResponse:
    return analyze(case,get_retriever())
