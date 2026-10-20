from app.document_processor import extract_requirements_with_sources
from app.requirement_schema import RegulatoryRequirement
from app.database import save_regulatory_requirement

PDF_PATH = (
    "data/reference/dpdp/regulations/"
    "Digital Personal Data Protection Rules, 2025.pdf"
)

# 1. Extract requirements from Rule 6
requirements = extract_requirements_with_sources(PDF_PATH, 6)

# 2. Validate the extracted records
validated = [
    RegulatoryRequirement(**req)
    for req in requirements
]

# 3. Save each requirement to SQLite
for req in validated:

    # Preserve the existing requirement code for Rule 6(1)(b)
    if req.legal_reference == "Rule 6(1)(b)":
        requirement_code = "DPDP-R006"
    else:
        clause_letter = req.legal_reference.split("(")[-1].replace(")", "")
        requirement_code = f"DPDP-R6-1-{clause_letter.upper()}"

    result = save_regulatory_requirement(
        requirement_code=requirement_code,
        regulation_name="DPDP Rules, 2025",
        legal_reference=req.legal_reference,
        requirement_text=req.requirement_text,
        applicability=None,
        effective_date="2027-05-14",
        expected_evidence=None,
        source_document=req.source_document,
        source_page=req.source_page
    )

    print(req.legal_reference, "->", result["status"])