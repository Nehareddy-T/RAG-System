# =========================
# Tiny-RAG Makefile
# =========================

# === Environment Variables ===
ENV_FILE=.env
PYTHON=python3

# Detect OS (Windows_NT for Windows)
ifeq ($(OS),Windows_NT)
	ACTIVATE = venv\Scripts\activate
else
	ACTIVATE = . venv/bin/activate
endif

# === Setup Commands ===
install:
	$(PYTHON) -m venv venv
	$(ACTIVATE) && pip install -r requirements.txt

# === Start Database (pgvector via Docker) ===
db-up:
	docker compose up -d

db-down:
	docker compose down

# === Run the FastAPI server ===
run-api:
	$(ACTIVATE) && uvicorn src.serving.api:app --host 0.0.0.0 --port 8080 --reload

# === CLI: Ingest a document ===
ingest:
	$(ACTIVATE) && $(PYTHON) -m src.cli.ingest_one --doc_id resume --path data/sample.pdf

# === CLI: Query the system ===
query:
	$(ACTIVATE) && $(PYTHON) -m src.cli.query --q "What experience does Neha have?" --k 5

# === Run all (full startup flow) ===
run-all: db-up install run-api
