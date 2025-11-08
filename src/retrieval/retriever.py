from typing import Dict, Any
from src.embedding.embedder_gemini import GeminiEmbedder
from src.store.repository import search_by_embedding

_embedder = GeminiEmbedder()

def retrieve(question: str, top_k: int) -> list[dict[str, Any]]:
    qvec = _embedder.embed([question])[0]
    rows = search_by_embedding(qvec, top_k=top_k)
    # rows: (doc_id, chunk_index, chunk_text, cosine_sim)
    if not rows:
        return []
    return [
        {"doc_id": r[0], "chunk_index": r[1], "chunk_text": r[2], "score": float(r[3])}
        for r in rows
    ]
