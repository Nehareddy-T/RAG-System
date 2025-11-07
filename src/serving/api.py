from fastapi import FastAPI
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader
from src.core.config import PORT, TOP_K
from src.core.logging import get_logger
from src.ingest.extractor_pdfplumber import PdfPlumberExtractor
from src.chunking.splitter import enumerate_chunks
from src.embedding.embedder_gemini import GeminiEmbedder
from src.store.repository import upsert_chunks
from src.retrieval.retriever import retrieve

logger = get_logger("api")
app = FastAPI()
env = Environment(loader=FileSystemLoader("src/prompts"))
_template = env.get_template("answer.jinja")
_embedder = GeminiEmbedder()
_extractor = PdfPlumberExtractor()

class IngestRequest(BaseModel):
    doc_id: str
    file_path: str

class QueryRequest(BaseModel):
    question: str
    top_k: int | None = None

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.post("/ingest")
def ingest(req: IngestRequest):
    text = _extractor.extract(req.file_path)
    rows = enumerate_chunks(req.doc_id, text)
    vecs = _embedder.embed([r[2] for r in rows])
    count = upsert_chunks(req.doc_id, rows, vecs)
    logger.info(f"Ingested {count} chunks for {req.doc_id}")
    return {"doc_id": req.doc_id, "chunks": count}

@app.post("/query")
def query(req: QueryRequest):
    tk = req.top_k or TOP_K
    ctx = retrieve(req.question, tk)
    rendered = _template.render(question=req.question, chunks=ctx)
    return {"answer": rendered.strip(), "sources": ctx}
