from .extractor_base import TextExtractor
from .extractor_gemini import GeminiExtractor
from .extractor_pdfplumber import PdfPlumberExtractor
from src.core.logging import get_logger

logger = get_logger("CombinedExtractor")

class CombinedExtractor(TextExtractor):
    def __init__(self):
        self.gemini = GeminiExtractor()
        self.pdfplumber = PdfPlumberExtractor()

    def extract(self, file_path: str) -> str:
        try:
            logger.info(f"Attempting Gemini extraction for {file_path}")
            text = self.gemini.extract(file_path)
            if text and len(text.strip()) > 100:
                logger.info("Gemini extraction successful.")
                return text
            else:
                raise ValueError("Gemini returned insufficient text; falling back.")
        except Exception as e:
            logger.warning(f"Gemini extraction failed ({e}). Falling back to pdfplumber.")
            text = self.pdfplumber.extract(file_path)
            logger.info(f"PDFPlumber extracted {len(text)} characters of text.")
            return text
