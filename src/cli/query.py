import argparse
from src.retrieval.retriever import retrieve
from src.answer.compose import compose_answer
from src.core.logging import get_logger

logger = get_logger("cli_query")

if __name__ == "__main__":
    # Parse command-line arguments
    p = argparse.ArgumentParser(description="Query your ingested documents using Gemini RAG")
    p.add_argument("--q", required=True, help="Question to ask")
    p.add_argument("--k", type=int, default=5, help="Top K chunks to retrieve")
    args = p.parse_args()

    logger.info(f"Query received: {args.q} (top_k={args.k})")

    # Retrieve relevant chunks
    ctx = retrieve(args.q, args.k)

    if not ctx:
        logger.warning("No relevant chunks found. Returning fallback answer.")
        print("\nAnswer: I don't know\nSources: []")
    else:
        # Generate answer using Gemini
        answer = compose_answer(args.q, ctx)
        sources = [f"{c['doc_id']}:{c['chunk_index']}" for c in ctx]

        print("\n=== Gemini RAG Answer ===")
        print(f"Question: {args.q}\n")
        print(f"Answer: {answer}\n")
        print(f"Sources: {', '.join(sources)}\n")

        logger.info(f"Answered with {len(sources)} supporting chunks.")
