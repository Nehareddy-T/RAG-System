import argparse
from src.serving.api import _extractor, _embedder
from src.chunking.splitter import enumerate_chunks
from src.store.repository import upsert_chunks

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--doc_id", required=True)
    p.add_argument("--path", required=True)
    args = p.parse_args()

    text = _extractor.extract(args.path)
    rows = enumerate_chunks(args.doc_id, text)
    vecs = _embedder.embed([r[2] for r in rows])
    n = upsert_chunks(args.doc_id, rows, vecs)
    print(f"Ingested {n} chunks for {args.doc_id}")
