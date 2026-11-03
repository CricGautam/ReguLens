from pathlib import Path
import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_DIR / "data" / "training" / "document_labels.csv"
MODEL_PATH = BASE_DIR / "models" / "document_classifier.joblib"

# Load training data
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

# Train the classifier
pipeline.fit(df["text"], df["label"])

# Save the trained pipeline
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(pipeline, MODEL_PATH)

print("Document classifier trained successfully!")
print(f"Training examples: {len(df)}")
print(f"Classes: {list(pipeline.classes_)}")
print(f"Model saved to: {MODEL_PATH}")