from typing import Any, TypedDict


class ComplianceState(TypedDict, total=False):
    assessment_id: str
    query: str
    document_id: int  # NEW: SQLite document reference
    regulation_path: str
    rule_number: int

    regulatory_requirements: list[dict[str, Any]]
    policy_matches: list[dict[str, Any]]
    evidence_findings: list[dict[str, Any]]

    draft_report: dict[str, Any]
    errors: list[str]