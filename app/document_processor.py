
import re
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

def extract_pdf_pages(pdf_path):
    pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""

            pages.append({
                "page_number": page_number,
                "text": text
            })

    return pages


def extract_rule_section(pages, rule_number):
    full_text = "\n".join(page["text"] for page in pages)

    pattern = rf"(?m)^{rule_number}\.\s+.+?(?=^\d+\.\s+[A-Z]|\Z)"

    match = re.search(pattern, full_text, flags=re.DOTALL | re.MULTILINE)

    return match.group(0).strip() if match else None

def extract_rule_clauses(rule_text, rule_number):
    pattern = r"(?m)^\(([a-z])\)\s+"

    matches = list(re.finditer(pattern, rule_text))
    clauses = []

    for index, match in enumerate(matches):
        start = match.end()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end_match = re.search(r"(?m)^\(\d+\)\s+", rule_text[start:])
            end = start + end_match.start() if end_match else len(rule_text)

        clauses.append({
            "legal_reference": f"Rule {rule_number}(1)({match.group(1)})",
            "requirement_text": " ".join(rule_text[start:end].split())
        })

    return clauses

def find_rule_start_page(pages, rule_number):
    import re

    pattern = rf"(?m)^{rule_number}\.\s+"

    for page in pages:
        if re.search(pattern, page["text"]):
            return page["page_number"]

    return None


def extract_requirements_with_sources(pdf_path, rule_number):
    pages = extract_pdf_pages(pdf_path)

    rule_text = extract_rule_section(pages, rule_number)

    if not rule_text:
        return []

    clauses = extract_rule_clauses(rule_text, rule_number)
    start_page = find_rule_start_page(pages, rule_number)
    parent_obligation = extract_rule_preamble(rule_text)

    for clause in clauses:
        clause["source_document"] = Path(pdf_path).name
        clause["source_page"] = start_page
        clause['parent_obligation'] = parent_obligation

    return clauses

def extract_rule_preamble(rule_text):
    """
    Extract the introductory obligation before clause (a).
    """
    match = re.search(r"(?m)^\(a\)\s+", rule_text)

    if not match:
        return None

    preamble = rule_text[:match.start()].strip()

    return " ".join(preamble.split())