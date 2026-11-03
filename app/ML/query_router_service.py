from functools import lru_cache
from pathlib import Path

import joblib

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "models" / "query_router.joblib"


@lru_cache(maxsize=1)
def load_query_router():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Query Router model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def route_query(query: str) -> dict:
    if not query.strip():
        raise ValueError("Query cannot be empty")

    model = load_query_router()

    probabilities = model.predict_proba([query])[0]
    best_index = probabilities.argmax()

    return {
        "query": query,
        "predicted_route": str(model.classes_[best_index]),
        "confidence": round(float(probabilities[best_index]), 4),
        "model": "tfidf_logistic_regression",
    }