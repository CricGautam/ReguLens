
from pathlib import Path

from app.database import get_document_by_id
from app.document_processor import extract_requirements_with_sources
from app.requirement_schema import RegulatoryRequirement


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = (PROJECT_ROOT / "data" / "raw").resolve()


def regulatory_agent(state):
    document_id = state["document_id"]
    rule_number = state["rule_number"]

    # Retrieve the uploaded document from SQLite
    document = get_document_by_id(document_id)

    if document is None:
        raise ValueError(f"Document {document_id} not found")

    if document["processing_status"] != "processed":
        raise ValueError("Document is not ready for assessment")

    if document["document_type"] != "regulation":
        raise ValueError("Selected document is not a regulation")

    # Resolve and validate the registered PDF path
    pdf_path = (PROJECT_ROOT / document["file_path"]).resolve()

    if (
        not pdf_path.is_relative_to(RAW_DATA_DIR)
        or pdf_path.suffix.lower() != ".pdf"
        or not pdf_path.is_file()
    ):
        raise ValueError("Registered regulation PDF is invalid or unavailable")

    # Existing requirement extraction logic
    requirements = extract_requirements_with_sources(
        str(pdf_path), rule_number
    )

    validated_requirements = [
        RegulatoryRequirement(**requirement).model_dump()
        for requirement in requirements
    ]

    return {"regulatory_requirements": validated_requirements}
