install:
	pip install -r requirements.txt
api:
	uvicorn app.main:app --reload --port 8000
ui:
	streamlit run streamlit_app.py
test:
	pytest -q
evaluate:
	python scripts/evaluate.py
