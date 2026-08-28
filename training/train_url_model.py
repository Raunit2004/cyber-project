import sys
import os
import pandas as pd
import numpy as np
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Add parent dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing.url_features import URLFeatureExtractor

def train_url_model():
    print("Loading dataset...")
    try:
        df = pd.read_csv('datasets/urls.csv')
    except FileNotFoundError:
        print("Error: datasets/urls.csv not found.")
        return

    # Drop duplicates & NA
    df = df.drop_duplicates()
    df = df.dropna()

    print(f"Dataset shape after cleaning: {df.shape}")

    extractor = URLFeatureExtractor()
    print("Extracting features...")
    
    # Extract features for all URLs
    features_list = df['url'].apply(extractor.extract_features).tolist()
    X = pd.DataFrame(features_list)
    y = df['label']

    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print("Evaluating model...")
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred).tolist()

    metrics = {
        'url_model': {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'confusion_matrix': cm
        }
    }

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

    # Save model and metrics
    os.makedirs('models', exist_ok=True)
    
    model_path = 'models/url_model.pkl'
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

    # Save metrics (append or create)
    metrics_file = 'models/model_metrics.json'
    existing_metrics = {}
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r') as f:
            existing_metrics = json.load(f)
            
    existing_metrics.update(metrics)
    
    with open(metrics_file, 'w') as f:
        json.dump(existing_metrics, f, indent=4)
    print(f"Metrics saved to {metrics_file}")

if __name__ == "__main__":
    train_url_model()
