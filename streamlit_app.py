import json, os, sys, time
import streamlit as st
sys.path.insert(0, os.path.dirname(__file__))
from app.models import ClaimCase
from app.service import run_analysis
from app.config import PUBLIC_CASES

st.set_page_config(page_title="Aptino Claim Decision Engine",layout="wide")
st.title("Policy-Aware Multi-Agent RAG Claim Decision Engine")
st.caption("Evidence-grounded insurance claim analysis • no hidden chain-of-thought")

@st.cache_data
def load_cases():
    return json.load(open(PUBLIC_CASES,encoding="utf-8"))

cases=load_cases()
mode=st.radio("Input",["Public case","Paste JSON"],horizontal=True)
if mode=="Public case":
    cid=st.selectbox("Select case", [c["case_id"] for c in cases])
    case=next(c for c in cases if c["case_id"]==cid)
    st.json(case,expanded=False)
else:
    raw=st.text_area("Claim JSON",height=300,placeholder='{"case_id":"CUSTOM-001", ...}')
    case=json.loads(raw) if raw else None

if st.button("Analyze claim",type="primary") and case:
    try:
        result=run_analysis(ClaimCase.model_validate(case)).model_dump()
        st.subheader("Decision")
        cols=st.columns(3)
        cols[0].metric("Status",result["decision"])
        cols[1].metric("Confidence",f'{result["confidence"]:.0%}')
        cols[2].metric("Payable", "—" if result["payable_amount_inr"] is None else f'₹{result["payable_amount_inr"]:,.0f}')
        if result["decision"]=="NEEDS_REVIEW":
            st.warning("ABSTAINED: the supplied evidence is insufficient for a safe final decision.")
        st.subheader("Key findings")
        for x in result["key_findings"]: st.write("•",x)
        st.subheader("Applicable limits / deductions")
        for x in result["applicable_limits"]: st.write("•",x)
        st.subheader("Missing evidence")
        if result["missing_evidence"]:
            for x in result["missing_evidence"]: st.write("•",x)
        else: st.success("No material missing evidence identified.")
        st.subheader("Policy evidence")
        for c in result["citations"]:
            with st.expander(f'Page {c["page"]} • {c["section"]} • {c["chunk_id"]}'):
                st.write(c["claim"])
        st.subheader("Validation")
        st.write(result["validation"])
        st.subheader("Execution trace")
        st.dataframe(result["trace"],use_container_width=True)
    except Exception as e:
        st.error(f"Invalid input or analysis error: {type(e).__name__}: {e}")
