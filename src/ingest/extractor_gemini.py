# src/ingest/extractor_gemini.py
import google.generativeai as genai
from .extractor_base import TextExtractor
from src.core.logging import get_logger
from src.core.config import GEMINI_API_KEY

logger = get_logger("GeminiExtractor")

class GeminiExtractor(TextExtractor):
    def __init__(self):
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            # ✅ Full model path required for 0.8.3+
            self.model = genai.GenerativeModel("models/gemini-2.0-flash")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.model = None

    def extract(self, file_path: str) -> str:
        if not self.model:
            raise RuntimeError("Gemini model not initialized")

        try:
            uploaded_file = genai.upload_file(path=file_path)
            logger.info(f"Uploaded file to Gemini: {uploaded_file.uri}")

            response = self.model.generate_content(
                [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "file_data": {
                                    "mime_type": "application/pdf",
                                    "file_uri": uploaded_file.uri,
                                }
                            },
                            {"text": "Extract and return the full, clean text content of this document."},
                        ],
                    }
                ]
            )

            text = response.text.strip()
            logger.info(f"Gemini extracted {len(text)} characters of text.")
            return text

        except Exception as e:
            logger.error(f"Gemini extraction failed: {e}")
            raise
