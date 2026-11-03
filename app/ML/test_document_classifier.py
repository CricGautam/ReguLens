from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "models" / "document_classifier.joblib"

model = joblib.load(MODEL_PATH)

test_documents = [
    "The organization must comply with data protection regulations.",
    "Employees must follow the company's password management policy.",
    "The auditor identified missing approval records during the assessment.",
    "The quarterly access review was completed and approved by the manager."
]

for text in test_documents:
    prediction = model.predict([text])[0]
    probabilities = model.predict_proba([text])[0]
    confidence = max(probabilities)

    print(f"\nDocument: {text}")
    print(f"Predicted Type: {prediction}")
    print(f"Model Confidence: {confidence:.2%}")