import os
import sys
import joblib
import pandas as pd

# Allow imports from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing.url_features import URLFeatureExtractor


class URLDetector:
    """Wraps the trained Random Forest model to classify URLs as malicious or safe."""

    # Risk thresholds (probability of being phishing)
    THRESHOLD_HIGH   = 0.75
    THRESHOLD_MEDIUM = 0.45

    def __init__(self, model_path: str = None):
        if model_path is None:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base, 'models', 'url_model.pkl')

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"URL model not found at '{model_path}'. "
                "Run training/train_url_model.py first."
            )

        self.model = joblib.load(model_path)
        self.extractor = URLFeatureExtractor()

    def predict(self, url: str) -> dict:
        """
        Classify a single URL.

        Returns a dict with:
            - is_malicious (bool)
            - confidence   (float, 0-1, probability of being malicious)
            - risk_level   ('HIGH' | 'MEDIUM' | 'LOW')
            - features     (dict of extracted features)
            - label        ('Malicious' | 'Safe')
        """
        url = url.strip()
        features = self.extractor.extract_features(url)
        feature_df = pd.DataFrame([features])

        # Probability of class 1 (malicious)
        proba = self.model.predict_proba(feature_df)[0]
        malicious_prob = float(proba[1]) if len(proba) > 1 else float(proba[0])

        is_malicious = malicious_prob >= self.THRESHOLD_MEDIUM

        if malicious_prob >= self.THRESHOLD_HIGH:
            risk_level = 'HIGH'
        elif malicious_prob >= self.THRESHOLD_MEDIUM:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'

        return {
            'url': url,
            'is_malicious': is_malicious,
            'confidence': round(malicious_prob * 100, 2),
            'risk_level': risk_level,
            'label': 'Malicious' if is_malicious else 'Safe',
            'features': features,
        }

    def predict_batch(self, urls: list) -> list:
        """Classify a list of URLs. Returns a list of result dicts."""
        return [self.predict(u) for u in urls]


# Quick standalone test
if __name__ == '__main__':
    detector = URLDetector()
    test_urls = [
        'https://www.google.com',
        'http://secure-login-paypal.com/verify',
        'http://192.168.1.1/admin',
        'https://bit.ly/secure-login',
        'https://github.com/login',
    ]
    for u in test_urls:
        result = detector.predict(u)
        print(f"[{result['risk_level']:6}] {result['label']:10} ({result['confidence']:5.1f}%)  {u}")
