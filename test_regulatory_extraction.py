from app.document_processor import extract_requirements_with_sources
from app.requirement_schema import RegulatoryRequirement

PDF_PATH = (
    "data/reference/dpdp/regulations/"
    "Digital Personal Data Protection Rules, 2025.pdf"
)

requirements = extract_requirements_with_sources(PDF_PATH, 6)

validated = [
    RegulatoryRequirement(**requirement)
    for requirement in requirements
]

print("\n========== CONTEXT VALIDATION ==========\n")

for requirement in validated:
    print(
        requirement.legal_reference,
        "-> Parent obligation:",
        bool(requirement.parent_obligation)
    )

print(f"Successfully validated {len(validated)} requirements")

for requirement in validated:
    print(
        requirement.legal_reference,
        "-> PDF page",
        requirement.source_page
    )

from app.document_processor import (
    extract_pdf_pages,
    extract_rule_section
)

pages = extract_pdf_pages(PDF_PATH)

rule_text = extract_rule_section(pages, 6)

print("\n========== FULL RULE 6 ==========\n")
print(rule_text)

from app.document_processor import extract_rule_preamble

preamble = extract_rule_preamble(rule_text)

print("\n========== RULE PREAMBLE ==========\n")
print(preamble)