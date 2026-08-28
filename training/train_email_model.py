import sys
import os
import pandas as pd
import numpy as np
import joblib
import json
import re
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix


# ─── Feature helpers ─────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Basic text cleaning for email content."""
    text = str(text).lower()
    text = re.sub(r'http\S+', ' urltoken ', text)   # replace URLs with token
    text = re.sub(r'[^a-z\s]', ' ', text)           # keep only letters
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ─── Training ─────────────────────────────────────────────────────────────────

def train_email_model():
    print("Loading email dataset...")
    try:
        df = pd.read_csv('datasets/emails.csv')
    except FileNotFoundError:
        print("Error: datasets/emails.csv not found. Run datasets/generate_mock_data.py first.")
        return

    df = df.drop_duplicates()
    df = df.dropna()
    print(f"Dataset shape after cleaning: {df.shape}")

    # Clean text
    df['cleaned'] = df['text'].apply(clean_text)

    X = df['cleaned']
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Training TF-IDF + Random Forest pipeline...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000, sublinear_tf=True)),
        ('clf',   RandomForestClassifier(n_estimators=200, random_state=42)),
    ])
    pipeline.fit(X_train, y_train)

    print("Evaluating model...")
    y_pred = pipeline.predict(X_test)

    accuracy  = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall    = recall_score(y_test, y_pred)
    f1        = f1_score(y_test, y_pred)
    cm        = confusion_matrix(y_test, y_pred).tolist()

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    metrics_entry = {
        'email_model': {
            'accuracy':          float(accuracy),
            'precision':         float(precision),
            'recall':            float(recall),
            'f1_score':          float(f1),
            'confusion_matrix':  cm,
        }
    }

    os.makedirs('models', exist_ok=True)

    model_path = 'models/email_model.pkl'
    joblib.dump(pipeline, model_path)
    print(f"Model saved to {model_path}")

    metrics_file = 'models/model_metrics.json'
    existing = {}
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r') as f:
            existing = json.load(f)

    existing.update(metrics_entry)
    with open(metrics_file, 'w') as f:
        json.dump(existing, f, indent=4)
    print(f"Metrics saved to {metrics_file}")


if __name__ == '__main__':
    train_email_model()
