import tempfile
from pdfminer.high_level import extract_text
import os
from PyPDF2 import PdfReader

def extract_text_from_pdf(file_or_path):
    """
    Extract text from a PDF file. Accepts either a file path (str) or a file-like object (e.g., BytesIO).
    """
    if isinstance(file_or_path, (str, bytes)):
        # Assume it's a file path
        with open(file_or_path, 'rb') as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
    else:
        # Assume it's a file-like object
        reader = PdfReader(file_or_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
