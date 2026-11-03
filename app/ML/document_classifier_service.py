from functools import lru_cache
from pathlib import Path

import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "document_classifier.joblib"


@lru_cache(maxsize=1)
def load_classifier():
    if not MODEL_PATH.exists():
        return None

    return joblib.load(MODEL_PATH)


def predict_document_type(text: str):
    model = load_classifier()

    if model is None or not text.strip():
        return None

    probabilities = model.predict_proba([text])[0]
    best_index = probabilities.argmax()

    return {
        "predicted_type": model.classes_[best_index],
        "confidence": round(float(probabilities[best_index]), 4),
        "model": "tfidf_logistic_regression",
    }