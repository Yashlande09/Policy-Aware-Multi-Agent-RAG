# Final Submission Checklist

- [x] Supplied policy PDF indexed with page/section/chunk metadata
- [x] Dense + sparse retrieval
- [x] RRF fusion
- [x] Reranking stage
- [x] Five specialized agents
- [x] Structured state exchange
- [x] Structured API response
- [x] Citation metadata
- [x] Safe abstention
- [x] FastAPI health/analyze endpoints
- [x] Streamlit frontend
- [x] All 12 supplied public cases evaluated
- [x] Five additional candidate-created cases
- [x] At least two NEEDS_REVIEW cases
- [x] Failure analysis
- [x] Reproducible evaluation script
- [x] Unit tests
- [x] Dockerfile
- [x] Render blueprint
- [x] No secrets committed

## Before sending to Aptino

1. Push this folder to a public GitHub repository.
2. Deploy the API using `render.yaml`.
3. Deploy `streamlit_app.py` to Streamlit Community Cloud (or another host).
4. Replace/add the live URLs in your submission email/form.
5. Confirm `/health` returns HTTP 200.
6. Run `python scripts/evaluate.py` once on the deployment environment and commit the generated result if model versions changed.
