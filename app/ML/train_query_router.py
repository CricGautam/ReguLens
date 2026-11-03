from pathlib import Path

import joblib
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = BASE_DIR / "data" / "training" / "query_router_labels.csv"
MODEL_PATH = BASE_DIR / "models" / "query_router.joblib"

# Load training dataset
df = pd.read_csv(DATASET_PATH)

# Create ML pipeline
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        max_features=5000
    )),
    ("classifier", LogisticRegression(
        max_iter=1000,
        random_state=42
    ))
])

# Train ML Query Router
pipeline.fit(df["query"], df["label"])

# Save trained model
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(pipeline, MODEL_PATH)

print("ML Query Router trained successfully!")
print("Training samples:", len(df))
print("Classes:", list(pipeline.classes_))
print("Model saved to:", MODEL_PATH)