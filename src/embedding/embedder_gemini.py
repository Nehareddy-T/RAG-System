import google.generativeai as genai
from typing import List
from src.core.config import GEMINI_API_KEY, EMBED_DIM
from src.core.logging import get_logger

logger = get_logger("embedder")

class GeminiEmbedder:
    def __init__(self, model: str = "models/text-embedding-004"):
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not set in environment variables.")
            raise RuntimeError("GEMINI_API_KEY not set")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = model

    def embed(self, texts: List[str]) -> list[list[float]]:
        """
        Generates embeddings for a list of input texts using Gemini's text embedding model.
        """
        if not texts:
            logger.warning("No texts provided for embedding.")
            return []

        try:
            logger.info(f"Requesting embeddings for {len(texts)} text(s) using model '{self.model}'.")
            resp = genai.embed_content(model=self.model, content=texts)

            # Handle possible variations in Gemini's API response format
            vectors = resp.get("embedding") if "embedding" in resp else resp.get("embeddings")
            if isinstance(vectors, dict) and "values" in vectors:
                vectors = [vectors["values"]]
            if isinstance(vectors, list) and isinstance(vectors[0], dict):
                vectors = [v["values"] for v in vectors]

            # Validate embedding dimensions
            if vectors and len(vectors[0]) != EMBED_DIM:
                raise ValueError(f"Embedding dimension mismatch: expected {EMBED_DIM}, got {len(vectors[0])}")

            logger.info(f"Generated {len(vectors)} embeddings with dimension {EMBED_DIM}.")

            return vectors

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise RuntimeError(f"Failed to generate embeddings: {e}")