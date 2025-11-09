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
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

logger = get_logger("api")
app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error during {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error. Please try again later."},
    )

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
    try:
        text = _extractor.extract(req.file_path)
        if not text or len(text.strip()) == 0:
            raise ValueError("No text extracted from file. Possibly an invalid or empty PDF.")
        
        rows = enumerate_chunks(req.doc_id, text)
        vecs = _embedder.embed([r[2] for r in rows])
        count = upsert_chunks(req.doc_id, rows, vecs)
        logger.info(f"Ingested {count} chunks for {req.doc_id}")
        return {"doc_id": req.doc_id, "chunks": count}

    except FileNotFoundError:
        logger.warning(f"File not found: {req.file_path}")
        raise HTTPException(status_code=404, detail=f"File not found: {req.file_path}")

    except ValueError as ve:
        logger.warning(f"Invalid input: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to ingest document.")

@app.post("/query")
def query(req: QueryRequest):
    try:
        top_k = req.top_k or TOP_K
        ctx = retrieve(req.question, top_k)

        if not ctx:
            logger.warning("No relevant chunks found. Returning 'I don't know.'")
            return {"answer": "I don't know", "sources": []}

        # 🧠 Generate grounded answer
        answer = compose_answer(req.question, ctx)
        sources = [f"{c['doc_id']}:{c['chunk_index']}" for c in ctx]
        logger.info(f"Answered query with {len(sources)} sources.")

        return {"answer": answer, "sources": sources}

    except HTTPException:
        # re-raise known HTTP errors
        raise

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail="Error during question answering.")

