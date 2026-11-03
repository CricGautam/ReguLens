
from app.services.evidence_service import assess_regulatory_evidence


MAPPING_PATH = "data/synthetic/novacart/control_mapping.csv"


def evidence_agent(state):
    requirements = state["regulatory_requirements"]
    findings = []

    for requirement in requirements:
        legal_reference = requirement["legal_reference"]

        results = assess_regulatory_evidence(
            MAPPING_PATH,
            legal_reference
        )

        findings.extend(results)

    return {"evidence_findings": findings}
