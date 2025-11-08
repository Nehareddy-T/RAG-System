from typing import List, Tuple
from src.store.db import get_conn
from src.core.config import TOP_K

def upsert_chunks(doc_id: str, rows: List[Tuple[str, int, str]], embeddings: List[List[float]]) -> int:
    assert len(rows) == len(embeddings)
    with get_conn() as conn, conn.cursor() as cur:
        for (doc_id, idx, text), vec in zip(rows, embeddings):
            cur.execute(
                """
                INSERT INTO documents (doc_id, chunk_index, chunk_text, embedding)
                VALUES (%s, %s, %s, %s)
                """,
                (doc_id, idx, text, vec)
            )
    return len(rows)

def search_by_embedding(query_emb: List[float], top_k: int = TOP_K, min_score: float=0.4):
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
        return cur.fetchall()
