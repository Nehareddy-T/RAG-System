import re
from typing import List, Tuple
from src.core.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.core.logging import get_logger

logger = get_logger("splitter")
SENTENCE_SPLIT = re.compile(r"(?<=[.?!|])\s+")

def split_with_overlap(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    sentences = SENTENCE_SPLIT.split(text.strip())
    chunks, cur = [], []
    cur_len = 0

    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if cur_len + len(s) + 1 > chunk_size and cur:
            chunks.append(" ".join(cur))
            # start next with overlap from end
            tail = " ".join(cur)[-overlap:]
            cur = [tail, s] if tail else [s]
            cur_len = len(" ".join(cur))
        else:
            cur.append(s)
            cur_len += len(s) + 1
    if cur:
        chunks.append(" ".join(cur))
    return chunks

def enumerate_chunks(doc_id: str, text: str) -> List[Tuple[str, int, str]]:
    logger.info(f"Chunking with size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}")
    out = []
    for idx, ch in enumerate(split_with_overlap(text)):
        out.append((doc_id, idx, ch))
    return out
