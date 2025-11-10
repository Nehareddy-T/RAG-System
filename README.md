# 🧠 Tiny RAG System – Mini Retrieval-Augmented Generation (RAG) --- 'NEHA THOKALA'

This project implements a **minimal Retrieval-Augmented Generation (RAG) system** that ingests a single PDF, splits it into chunks, embeds them using **Google Gemini Embeddings**, stores them in **Postgres + pgvector**, and answers natural-language questions grounded in the document with explicit source citations.

---
## 🔍 Overview
This system demonstrates the **core mechanics of a Retrieval-Augmented Generation pipeline** designed for clarity, observability, and modularity.

**Text extraction strategy (primary + fallback):**
- **Primary:** Extract clean plaintext from PDFs/images using **Gemini Text Extraction** (high accuracy on mixed/complex layouts).
- **Fallback:** If the API is unavailable or errors (rate limits, network, model changes, offline dev), we **fall back to `pdfplumber`** for local parsing to keep ingestion reliable.

After extraction, the system:
1) **Splits** text into overlapping chunks  
2) **Embeds** chunks with **Gemini `text-embedding-004`**  
3) **Stores** chunks + vectors in **Postgres + pgvector** for similarity search  
4) On query, **embeds** the user question, **retrieves** top-K similar chunks, and **generates grounded, cited answers** using **Gemini 2.0 Flash** Returns **"I don't know"** when evidence is insufficient


### Why Gemini extraction first, and a local parser fallback?

**Gemini Text Extraction (primary)**
- ✅ Pros: Excellent at complex layouts (columns, headers/footers), handles images/OCR, fewer layout artifacts, higher semantic fidelity.
- ⚠️ Cons: Requires API key/network, subject to costs, model changes can affect outputs.

**Local Parser – `pdfplumber` (fallback)**
- ✅ Pros: Fully local (offline), deterministic, zero API cost, great for dev/test and resilience.
- ⚠️ Cons: May struggle with complex layouts (multi-column tables, text order), no OCR by default.

**Why `pdfplumber` over `PyPDF` here?**
- `pdfplumber` provides consistently cleaner plaintext on many real-world PDFs (esp. resumes/reports), with convenient page/char layout access.  
- `PyPDF` (formerly PyPDF2) excels at splitting/merging/metadata but its text extraction is often less reliable for semantic ingestion.  
- Given our goal (clean, chunk-ready text), `pdfplumber` is the better fallback.


---
## 🏗️ Architecture


                                ┌──────────┐
                                │ PDF File │
                                └─────┬────┘
                                      │
                                      ▼
                        ┌────────────────────────────┐
                        │  src/ingest/extractor_combined.py │
                        │   Combined Extractor         │
                        │   ── Gemini Text Extraction  │
                        │      • Handles complex layouts│
                        │      • OCR + image text via AI│
                        │      • Cloud-based (Primary)  │
                        │   ── pdfplumber Parser        │
                        │      • Local deterministic fallback│
                        │      • Clean plain-text output│
                        └───────────┬────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────────┐
                        │   src/chunking/splitter.py │
                        │   Chunking Engine           │
                        │   • 300-token segments      │
                        │   • 30-token overlap       │
                        │   • Sentence-aware splits   │
                        │   • Indexed for retrieval   │
                        └───────────┬────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────────┐
                        │ src/embedding/embedder_gemini.py │
                        │   Gemini Embeddings Engine  │
                        │   • 768-dim vector size     │
                        │   • Batch embedding API     │
                        └───────────┬────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────────┐
                        │ src/store/repository.py    │
                        │  Vector Store (Postgres + pgvector)│
                        │  • Stores embeddings + metadata│
                        │  • Cosine similarity index   │
                        │  • Persistent & queryable    │
                        └───────────┬────────────────┘
                                    │
                           [Accessible via]
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │ CLI Interface (src/cli)      │
                    │  • ingest_one.py  → Ingest PDFs  │
                    │  • query.py   → Query system │
                    │  Both with structured logging│
                    └───────────┬──────────────────┘
                                │
                                ▼
                        ┌────────────────────────────┐
                        │  src/retrieval/retriever.py │
                        │   Query Retrieval Engine    │
                        │   • Embed user question     │
                        │   • Vector similarity search│
                        │   • Returns top-K chunks    │
                        └───────────┬────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────────┐
                        │  src/answer/compose.py     │
                        │   Gemini-Flash Answer Composer │
                        │   • Combines question + chunks │
                        │   • Generates grounded response│
                        │   • Includes [chunk N] citations│
                        │   • Fallback → “I don’t know”   │
                        └───────────┬────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────────┐
                        │  src/serving/api.py (FastAPI) │
                        │   API Gateway Layer          │
                        │   • POST /ingest, POST /query │
                        │   • JSON output + sources     │
                        │   • Health endpoint + logs    │
                        │   • Integrates with CLI & UI  │
                        └───────────┬────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────────┐
                        │ Observability & Logging     │
                        │ src/core/logging.py         │
                        │ • Unified log format        │
                        │ • INFO/WARN/ERROR tracing   │
                        └────────────────────────────┘

---
## ⚙️ Prerequisites

- Python: 3.10+

- Docker Desktop: (for Postgres + pgvector)

- Google Gemini API Key: set in .env

- Code editor--VS Code (recommended)

---
## Installation
```bash
#1 Clone the repository

git clone https://github.com/Nehareddy-T/RAG-System.git
cd RAG-System

#2 Create and activate virtual environment

python3 -m venv venv
source venv/bin/activate  # macOS/Linux
or
venv\Scripts\activate     # Windows

#3 Install dependencies

pip install -r requirements.txt

#4 Copy and configure environment

cp .env.example .env

```

 then update:
**GEMINI_API_KEY=your_api_key_here**

Get Gemini API Key:

- Visit <https://aistudio.google.com/app/apikey>
- Click "Create API Key"
- Copy key to .env file
```bash
#5 Start the pgvector database
docker compose up -d

#Confirm container is running:
docker ps

#6 Initialize the schema
docker exec -it ragdb psql -U raguser -d ragdb -f src/store/schema.sql

```
---
## ⚙️ Scripted Run Commands
The project includes a `Makefile` with automated commands for setup and execution on Mac:
```bash
make install     # install dependencies
make db-up       # start the pgvector database
make run-api     # start the FastAPI server
make ingest      # ingest sample.pdf
make query       # query the RAG pipeline
make run-all     # db-up install run-api
```
*For Windows Users*

If you run into one of the following errors while running make:

bash: .: command not found

command separator '&&' not recognized

It means your shell doesn’t support Linux-style commands.
Run the equivalent steps manually in PowerShell

**Pro tip:** For Windows users, open your terminal as “Git Bash” instead of PowerShell for full Makefile support.

---
## Usage

**1. Ingest Documents (from Terminal):**

```bash
python -m src.cli.ingest_one --doc_id resume --path data/sample.pdf
```

✅ What happens:

- Extracts clean text from PDF

- Splits into chunks

- Embeds each chunk using Gemini embeddings

- Stores vectors in Postgres + pgvector

Expected output:

```lua
I2025-11-09 13:37:00,137 | INFO | CombinedExtractor | Attempting Gemini extraction for data/sample.pdf
2025-11-09 13:37:01,842 | INFO | GeminiExtractor | Uploaded file to Gemini: https://generativelanguage.googleapis.com/v1beta/files/7044ao8twcnb
2025-11-09 13:37:15,464 | INFO | GeminiExtractor | Gemini extracted 11432 characters of text.
2025-11-09 13:37:15,464 | INFO | CombinedExtractor | Gemini extraction successful.
2025-11-09 13:37:15,465 | INFO | splitter | Chunking with size=300, overlap=30
Ingested 53 chunks for resume
```
**Check Data Inserted by Your CLI Ingestion**
```bash
docker exec -it ragdb psql -U postgres -d ragdb
```
```sql
SELECT COUNT(*) FROM chunks;
```
Expected Output:
```markdown
 count
-------
 53
(1 row)
```
**That matches your logger output:**
`Ingested 53 chunks for resume`

When done, just type:
```sql
\q
```
to exit psql.

**2. Query the Knowledge Base (from Terminal):**
```bash
python -m src.cli.query --q "What experience does Neha have?" --k 5
```
Example output:
```vbnet
2025-11-09 13:40:15,156 | INFO | cli_query | Query received: What experience does Neha have? (top_k=5)
2025-11-09 13:40:16,337 | INFO | composer | Generated grounded answer (216 chars)

=== Gemini RAG Answer ===
Question: What experience does Neha have?

Answer: Neha has 5+ years of experience in building and deploying enterprise-grade AI/ML and LLM-powered applications [chunk 0]. She also has experience developing automation scripts for quality assurance testing [chunk 41].

Sources: resume:0, resume:41

2025-11-09 13:40:16,337 | INFO | cli_query | Answered with 2 supporting chunks.
```
**3. Run as a FastAPI Service**

In Terminal:
```bash
uvicorn src.serving.api:app --reload --port 8080
```

Test the Endpoints:
FastAPI Docs UI

FastAPI automatically exposes interactive docs at:
```arduino
http://127.0.0.1:8080/docs
```
- Open that in your browser.

- Find the /ingest endpoint.

- Click “Try it out”, fill in:
```json
{
  "doc_id": "resume",
  "file_path": "data/sample.pdf"
}
```
Click Execute — you’ll see both the request and server response.

Find the /query endpoint.

- Click “Try it out”, fill in:
```json
{
  "question": "Who are Neha parents",
  "top_k": 2
}
```
Click Execute — you’ll see both the request and server response.

Press control+c on keyboard for Application shutdown

---
## 💻 Technologies Used

| Category | Technology | Purpose |
|-----------|-------------|----------|
| **Programming Language** | Python 3.10+ | Core backend logic |
| **Framework** | FastAPI | REST API for ingestion & querying |
| **LLM & Embeddings** | Google Gemini 2.0 Flash / text-embedding-004 | Text extraction, embedding & generation |
| **Local Parser (Fallback)** | pdfplumber | Offline/local text extraction |
| **Database** | PostgreSQL + pgvector | Vector storage and cosine similarity search |
| **Containerization** | Docker Compose | Running Postgres + pgvector locally |
| **Logging** | Python logging (custom module) | Unified INFO/WARN/ERROR logs |
| **CLI Utilities** | Python argparse | Scripted ingestion and query |
| **Environment Management** | python-dotenv | Secure .env configuration |
| **Version Control** | Git + GitHub | Source code management |
---
## 🧾 Logging and Monitoring

All logs are unified under src/core/logging.py with consistent formats:
```
2025-11-09 19:35:28,469 | INFO | CombinedExtractor | Attempting Gemini extraction for data/sample.pdf
2025-11-09 19:35:30,177 | INFO | GeminiExtractor | Uploaded file to Gemini: https://generativelanguage.googleapis.com/v1beta/files/ki042x0r5l4o
2025-11-09 19:35:43,536 | INFO | GeminiExtractor | Gemini extracted 11432 characters of text.
2025-11-09 19:35:43,537 | INFO | CombinedExtractor | Gemini extraction successful.
2025-11-09 19:35:43,537 | INFO | splitter | Chunking with size=300, overlap=30
2025-11-09 19:35:44,317 | ERROR | db | ❌ Database connection failed: Unable to reach Postgres at localhost:5432. Ensure Docker is running and the pgvector container is active.

2025-11-09 20:08:11,825 | INFO | repository | Inserted 53 chunks for document 'resume' into the database

2025-11-09 13:40:15,156 | INFO | cli_query | Query received: What experience does Neha have? (top_k=5)
2025-11-09 13:40:16,337 | INFO | composer | Generated grounded answer (216 chars)
2025-11-09 13:40:16,337 | INFO | cli_query | Answered with 2 supporting chunks.

```
---
## 🔒 Security

- No hardcoded secrets — all keys loaded from .env.

- Safe fallback when Gemini API is unavailable or errors to local parser

- Proper exception handling and sanitized log messages.

---
## 🧪 Testing & Debugging

```
# Health check
curl http://127.0.0.1:8080/healthz

# Verify DB embeddings
SELECT COUNT(*) FROM documents;

# Inspect retrieved chunks
SELECT id, LEFT(chunk_text, 80) FROM documents LIMIT 5;
```

---
## Error Handling

- All endpoints (/ingest, /query) are wrapped in structured try/except blocks.

- A global exception handler catches any unhandled errors and returns safe, JSON-formatted responses instead of raw Python tracebacks.

- Each error is logged internally with full details for debugging, but only concise, user-friendly messages are returned to clients.


### ✅ Exceptions Handled

| Exception Type | Description | API Response |
|----------------|-------------|---------------|
| **FileNotFoundError** | Triggered when the provided file path in `/ingest` does not exist. | `404 File not found` |
| **ValueError** | Raised when the PDF is invalid or no text is extracted (e.g., empty or scanned-only document). | `400 Bad Request` |
| **Database Connection Errors (Postgres / Docker Down)** | Occurs when Postgres + pgvector is not running or unreachable. Logs a clear, actionable message instead of a long traceback. | `500 Internal Server Error` |
| **No Relevant Chunks Found** | When retrieval returns no chunks above the similarity threshold. | Returns `"I don't know"` with empty sources |
| **Unhandled Runtime Errors** | Any other unexpected error is caught by the global FastAPI exception handler. | `500 Internal server error` |

---

### 🗄️ Database Connection Errors (Postgres / Docker Down)

If the Postgres + pgvector database is not running or cannot be reached, the system logs a **clear, actionable message** instead of a raw traceback.

**Example Output**
```bash
2025-11-09 19:35:44,317 | ERROR | db | ❌ Database connection failed: Unable to reach Postgres at localhost:5432. Ensure Docker is running and the pgvector container is active.

[ERROR] Could not connect to the Postgres database.
Reason: connection failed: connection to server at "127.0.0.1", port 5432 failed: could not receive data from server: Connection refused

👉 To fix this, make sure your database container is running:
   docker compose up -d
```

---
## Limitations
- **Single-Document Scope:**
The system currently supports ingestion and retrieval from one document at a time. It does not yet support cross-document or multi-source retrieval.

- **Model & API Dependency:**
The pipeline relies on Google Gemini APIs for text extraction, embedding, and answer generation. This introduces dependency on external APIs, potential latency, and usage costs.

- **No Front-End Interface:**
Currently, the system exposes REST endpoints only; there is no user-facing interface to visualize queries, chunks, or citations.

---
## Future Scope

- **Multi-Document & Multi-Modal RAG:**
Extend the vector store to support retrieval across multiple documents and potentially integrate image or table embeddings for multimodal understanding.

- **Local LLM Integration:**
Introduce optional offline generation using open-source LLMs (e.g., LLaMA 3, Mistral, Phi-3) to remove external API dependencies.

- **User Interface Dashboard:**
Build a Streamlit or Gradio dashboard to allow users to upload PDFs, view retrieved chunks, and inspect source citations interactively.

- **Observability & Logging Improvements:**
Integrate structured logs and metrics collection (Prometheus + Grafana or OpenTelemetry) for system monitoring and performance analysis.

- **Authentication & Access Control:**
Add API key or JWT-based authentication and basic rate-limiting to make the service production-ready.

- **Scalability Enhancements:**
Containerize and orchestrate with Docker + Kubernetes, allowing the RAG components (ingest, retrieval, generation) to scale independently.