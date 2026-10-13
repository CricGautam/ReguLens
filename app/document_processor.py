
from pathlib import Path

import pdfplumber


def extract_pdf_text(pdf_path: str | Path) -> str:
    """Extract text from all pages of a PDF."""
    extracted_pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            extracted_pages.append(page_text)

    return "\n\n".join(extracted_pages)
