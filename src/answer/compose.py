# src/answer/compose.py
import google.generativeai as genai
from src.core.config import GEMINI_API_KEY
from src.core.logging import get_logger

logger = get_logger("composer")

# Configure Gemini client
genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini 2.0 Flash for fast, grounded reasoning
_model = genai.GenerativeModel("models/gemini-2.0-flash")


def compose_answer(question: str, retrieved_chunks: list[dict]) -> str:
    """
    Compose a concise, grounded answer using only the retrieved context.
    If the answer isn't clearly present in context, return "I don't know."
    """
    if not retrieved_chunks:
        return "I don't know"

    # Build context string
    context = "\n\n".join(
        [f"[chunk {c['chunk_index']}] {c['chunk_text']}" for c in retrieved_chunks]
    )

    # Construct grounded prompt
    prompt = (
        "You are a factual assistant. Using ONLY the provided context below, "
        "answer the user's question truthfully and concisely. "
        "Cite chunk numbers like [chunk N] in your answer. "
        "If the context does not clearly contain the answer, reply only with 'I don't know.'\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\nAnswer:"
    )

    try:
        response = _model.generate_content(prompt)
        answer = response.text.strip()

        # Normalize overly long or non-answers
        if not answer or len(answer) < 3:
            answer = "I don't know"

        logger.info(f"Generated grounded answer ({len(answer)} chars)")
        return answer

    except Exception as e:
        logger.error(f"Gemini generation failed: {e}")
        return "I don't know"
