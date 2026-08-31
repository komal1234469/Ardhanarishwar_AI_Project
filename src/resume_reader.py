from pypdf import PdfReader


def extract_pdf_text(uploaded_file):
    """Extracts plain text from an uploaded PDF (Streamlit UploadedFile).
    Returns an empty string if extraction fails or the PDF is
    image-only/scanned (no selectable text)."""
    try:
        reader = PdfReader(uploaded_file)
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages_text).strip()
    except Exception:
        return ""
