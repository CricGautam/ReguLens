
def reporting_agent(state):
    requirements = state.get("regulatory_requirements", [])
    policies = state.get("policy_matches", [])
    findings = state.get("evidence_findings", [])

    assessed_references = {
        finding["legal_reference"] for finding in findings
    }

    unassessed_references = [
        requirement["legal_reference"]
        for requirement in requirements
        if requirement["legal_reference"] not in assessed_references
    ]

    report = {
        "assessment_query": state["query"],
        "report_status": "DRAFT_REQUIRES_REVIEW",
        "total_requirements": len(requirements),
        "retrieved_policy_sections": len(policies),
        "evidence_assessments": len(findings),
        "unassessed_requirements": unassessed_references,
        "findings": findings,
        "conclusion": (
            "This is a preliminary evidence assessment. "
            "Missing evidence does not establish noncompliance. "
            "Unassessed requirements require further investigation."
        )
    }

    return {"draft_report": report}
