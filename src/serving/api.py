from fastapi import FastAPI
from pydantic import BaseModel
from src.core.config import PORT, TOP_K
from src.core.logging import get_logger
from src.ingest.extractor_combined import CombinedExtractor
from src.chunking.splitter import enumerate_chunks
from src.embedding.embedder_gemini import GeminiEmbedder
from src.store.repository import upsert_chunks
from src.retrieval.retriever import retrieve
from src.answer.compose import compose_answer

logger = get_logger("api")
app = FastAPI()
_embedder = GeminiEmbedder()
_extractor = CombinedExtractor()

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

"""@app.post("/query")
def query(req: QueryRequest):
    tk = req.top_k or TOP_K
    ctx = retrieve(req.question, tk)
    if not ctx:
        return {"answer": "I don't know", "sources": [ ]}
    answer_text = " ".join(c["chunk_text"].strip() for c in ctx)
    sources = " ".join([f"{c['doc_id']}:{c['chunk_index']}" for c in ctx])
    return {"answer": answer_text, "sources": sources}"""

@app.post("/query")
def query(req: QueryRequest):
    top_k = req.top_k or TOP_K

    # 🔍 Retrieve top-k most relevant chunks
    ctx = retrieve(req.question, top_k)

    # If no chunks found above similarity threshold
    if not ctx:
        logger.warning("No relevant chunks found. Returning 'I don't know.'")
        return {"answer": "I don't know", "sources": []}

    # 🧠 Generate a grounded answer using Gemini
    answer = compose_answer(req.question, ctx)

    # Collect citation sources for transparency
    sources = [f"{c['doc_id']}:{c['chunk_index']}" for c in ctx]

    logger.info(f"Answered query with {len(sources)} sources.")
    return {"answer": answer, "sources": sources} 
