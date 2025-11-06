import google.generativeai as genai
from typing import List
from src.core.config import GEMINI_API_KEY, EMBED_DIM

class GeminiEmbedder:
    def __init__(self, model: str = "models/text-embedding-004"):
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY not set")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = model

    def embed(self, texts: List[str]) -> list[list[float]]:
        # batching is supported; keep it simple
        resp = genai.embed_content(model=self.model, content=texts)
        vectors = resp["embedding"] if "embedding" in resp else resp["embeddings"]
        # Ensure vectors is a list of vectors
        if isinstance(vectors, dict) and "values" in vectors:
            vectors = [vectors["values"]]
        if isinstance(vectors, list) and isinstance(vectors[0], dict):
            vectors = [v["values"] for v in vectors]
        # dim check
        if vectors and len(vectors[0]) != EMBED_DIM:
            raise RuntimeError(f"Embedding dim mismatch: expected {EMBED_DIM}, got {len(vectors[0])}")
        return vectors
