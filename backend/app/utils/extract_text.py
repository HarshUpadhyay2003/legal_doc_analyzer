import tempfile
from pdfminer.high_level import extract_text

def extract_text_from_pdf(file_storage):
    # Create a temporary file path (without opening the file)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        temp_path = temp.name

    # Save the uploaded file to the temp path
    file_storage.save(temp_path)

    # Extract text
    text = extract_text(temp_path)

    # Clean up (optional)
    import os
    os.remove(temp_path)

    return text
