from app.document_processor import extract_requirements_with_sources
from app.requirement_schema import RegulatoryRequirement
from app.database import update_requirement_parent_obligation


def process_regulatory_context(pdf_path, rule_number, regulation_name):
    # Step 1: Extract requirements with legal context
    extracted = extract_requirements_with_sources(
        pdf_path, rule_number
    )

    # Step 2: Validate requirements
    validated = [
        RegulatoryRequirement(**requirement)
        for requirement in extracted
    ]

    # Step 3: Update existing database records
    results = []

    for requirement in validated:
        updated_count = update_requirement_parent_obligation(
            regulation_name=regulation_name,
            legal_reference=requirement.legal_reference,
            parent_obligation=requirement.parent_obligation
        )

        results.append({
            "legal_reference": requirement.legal_reference,
            "updated": updated_count == 1
        })

    return results