import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", "8080"))
ENV = os.getenv("ENV", "dev")

PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = int(os.getenv("PGPORT", "5432"))
PGDATABASE = os.getenv("PGDATABASE", "ragdb")
PGUSER = os.getenv("PGUSER", "raguser")
PGPASSWORD = os.getenv("PGPASSWORD", "ragpass")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

EMBED_DIM = int(os.getenv("EMBED_DIM", "768"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
TOP_K = int(os.getenv("TOP_K", "5"))
