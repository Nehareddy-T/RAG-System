from typing import List, Tuple
from src.store.db import get_conn
from src.core.config import TOP_K
from src.core.logging import get_logger

logger = get_logger("repository")

def upsert_chunks(doc_id: str, rows: List[Tuple[str, int, str]], embeddings: List[List[float]]) -> int:
    assert len(rows) == len(embeddings), "Mismatch between chunk count and embeddings count"

    with get_conn() as conn, conn.cursor() as cur:
        for (doc_id, idx, text), vec in zip(rows, embeddings):
            cur.execute(
                """
                INSERT INTO documents (doc_id, chunk_index, chunk_text, embedding)
                VALUES (%s, %s, %s, %s)
                """,
                (doc_id, idx, text, vec)
            )

    count = len(rows)
    # ✅ Log a concise summary
    logger.info(f"Inserted {count} chunks for document '{doc_id}' into the database.")
    return count


def search_by_embedding(query_emb: List[float], top_k: int = TOP_K, min_score: float = 0.4):
    """
    Searches for top-k most similar chunks to the given query embedding using cosine similarity.
    Filters results above min_score.
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT doc_id, chunk_index, chunk_text,
                   1 - (embedding <=> (%s)::vector) AS cosine_sim
            FROM documents
            WHERE 1 - (embedding <=> (%s)::vector) >= %s
            ORDER BY cosine_sim DESC
            LIMIT %s
            """,
            (query_emb, query_emb, min_score, top_k)
        )
        rows = cur.fetchall()

    if not rows:
        logger.warning(f"No chunks found above similarity threshold ({min_score}). Returning empty results.")
    else:
        top_scores = [round(r[3], 3) for r in rows]
        top_chunks = [r[1] for r in rows]
        logger.info(f"Retrieved {len(rows)} chunks above threshold ({min_score}) for current query.")
        logger.debug(f"Chunk indices retrieved: {top_chunks} | Cosine scores: {top_scores}")

    return rows

