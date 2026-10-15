from email.mime import text
import re
import spacy

nlp = spacy.load("en_core_web_sm")


def detect_pii(text: str):
    detected_entities = []

    # Detect names using spaCy NLP
    doc = nlp(text)

    for entity in doc.ents:
        if entity.label_ == "PERSON":
            detected_entities.append({
                "type": "PERSON",
                "value": entity.text,
                "start": entity.start_char,
                "end": entity.end_char,
            })

    # Detect email addresses using regex
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    for match in re.finditer(email_pattern, text):
        detected_entities.append({
            "type": "EMAIL",
            "value": match.group(),
            "start": match.start(),
            "end": match.end(),
        })

    # Detect Indian mobile numbers
    phone_pattern = r"(?<!\d)(?:\+91[\s-]?|0)?[6-9]\d{9}(?!\d)"

    for match in re.finditer(phone_pattern, text):
        detected_entities.append({
            "type": "PHONE",
            "value": match.group(),
            "start": match.start(),
            "end": match.end(),
        })

    return detected_entities

def mask_pii(text: str) -> str:
    detected_entities = detect_pii(text)

    # Sort entities by their position in the original text
    detected_entities.sort(key=lambda entity: entity["start"])

    masked_parts = []
    last_position = 0

    for entity in detected_entities:
        start = entity["start"]
        end = entity["end"]

        # Skip overlapping entities
        if start < last_position:
            continue

        # Preserve text before the detected entity
        masked_parts.append(text[last_position:start])

        # Replace sensitive information with its category
        masked_parts.append(f"[{entity['type']}]")

        last_position = end

    # Preserve remaining text
    masked_parts.append(text[last_position:])

    return "".join(masked_parts)     