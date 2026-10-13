
import re


DOCUMENT_KEYWORDS = {
    "regulation": [
        "act", "regulation", "regulatory", "statute",
        "government notification", "compliance requirements",
    ],
    "internal_policy": [
        "internal policy", "security policy", "standard operating procedure",
        "sop", "company policy", "access control policy",
    ],
    "contract": [
        "agreement", "contract", "vendor agreement",
        "service level agreement", "sla", "terms and conditions",
    ],
    "audit_evidence": [
        "audit report", "access review", "backup log",
        "audit evidence", "control testing", "training records",
    ],
    "risk_record": [
        "risk register", "risk assessment", "incident report",
        "security incident", "risk mitigation",
    ],
}


def classify_document(text: str) -> str:
    """Classify a document using simple keyword matching."""
    normalized_text = re.sub(r"\s+", " ", text.lower())

    scores = {
        category: sum(
            1
            for keyword in keywords
            if keyword in normalized_text
        )
        for category, keywords in DOCUMENT_KEYWORDS.items()
    }

    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]

    if best_score == 0:
        return "unknown"

    # Avoid an arbitrary classification when categories tie.
    highest_categories = [
        category
        for category, score in scores.items()
        if score == best_score
    ]

    if len(highest_categories) > 1:
        return "unknown"

    return best_category
