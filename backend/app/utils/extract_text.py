import tempfile
from pdfminer.high_level import extract_text
import os

def extract_text_from_pdf(file_path):
    # Extract text directly from the given file path
    text = extract_text(file_path)
    return text
