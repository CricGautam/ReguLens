
import csv
from pathlib import Path


def assess_access_review_evidence(evidence_path, control_id):
    """Assess documented access-review evidence for a control."""

    evidence_path = Path(evidence_path)

    with evidence_path.open("r", encoding="utf-8-sig", newline="") as file:
        records = list(csv.DictReader(file))

    relevant_records = [
        record for record in records
        if record["control_id"] == control_id
    ]

    if not relevant_records:
        return {
            "control_id": control_id,
            "status": "NO_EVIDENCE",
            "finding": "No access-review records found."
        }

    missing_reviews = [
        record["review_period"]
        for record in relevant_records
        if record["status"].strip().lower() == "missing"
        or not record["evidence_reference"].strip()
    ]

    return {
        "control_id": control_id,
        "status": (
            "POTENTIAL_EVIDENCE_GAP"
            if missing_reviews else "NO_GAP_IDENTIFIED"
        ),
        "total_records": len(relevant_records),
        "missing_periods": missing_reviews,
        "finding": (
            f"Missing supporting evidence for: {', '.join(missing_reviews)}"
            if missing_reviews
            else "No missing evidence identified in supplied records."
        )
    }


def assess_regulatory_evidence(mapping_path, legal_reference):
    """Assess evidence using the regulatory-to-control mapping."""

    mapping_path = Path(mapping_path)

    with mapping_path.open("r", encoding="utf-8-sig", newline="") as file:
        mappings = list(csv.DictReader(file))

    relevant_mappings = [
        mapping for mapping in mappings
        if mapping["legal_reference"] == legal_reference
    ]

    results = []

    for mapping in relevant_mappings:
        evidence_path = (
            mapping_path.parent
            / "evidence"
            / mapping["evidence_document"]
        )

        assessment = assess_access_review_evidence(
            evidence_path,
            mapping["control_id"]
        )

        results.append({
            "legal_reference": legal_reference,
            "control_id": mapping["control_id"],
            "control_name": mapping["control_name"],
            "policy_document": mapping["policy_document"],
            "evidence_assessment": assessment
        })

    return results
