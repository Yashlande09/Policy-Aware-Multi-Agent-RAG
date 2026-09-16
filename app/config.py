from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "policy" / "USGIC-CSCIndividualHealthInsurance_2017-2018.pdf"
PUBLIC_CASES = ROOT / "data" / "public_test_cases.json"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL","sentence-transformers/all-MiniLM-L6-v2")
RERANKER_MODEL = os.getenv("RERANKER_MODEL","cross-encoder/ms-marco-MiniLM-L-6-v2")
TOP_K_DENSE = int(os.getenv("TOP_K_DENSE","8"))
TOP_K_SPARSE = int(os.getenv("TOP_K_SPARSE","8"))
TOP_K_FINAL = int(os.getenv("TOP_K_FINAL","6"))
