import pdfplumber
from .extractor_base import TextExtractor

class PdfPlumberExtractor(TextExtractor):
    def extract(self, file_path: str) -> str:
        out = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                txt = page.extract_text() or ""
                out.append(txt.strip())
        return "\n\n".join([t for t in out if t])
