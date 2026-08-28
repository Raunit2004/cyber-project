import os
import sys
import re
import joblib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def _clean_text(text: str) -> str:
    """Mirror of the cleaning used during training."""
    text = str(text).lower()
    text = re.sub(r'http\S+', ' urltoken ', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


class EmailDetector:
    """Wraps the trained TF-IDF + RF pipeline to classify email text."""

    THRESHOLD_HIGH   = 0.75
    THRESHOLD_MEDIUM = 0.45

    def __init__(self, model_path: str = None):
        if model_path is None:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base, 'models', 'email_model.pkl')

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Email model not found at '{model_path}'. "
                "Run training/train_email_model.py first."
            )

        self.pipeline = joblib.load(model_path)

    def predict(self, text: str) -> dict:
        """
        Classify a single email body.

        Returns a dict with:
            - is_phishing  (bool)
            - confidence   (float %, probability of being phishing)
            - risk_level   ('HIGH' | 'MEDIUM' | 'LOW')
            - label        ('Phishing' | 'Legitimate')
            - preview      (first 120 chars of input)
        """
        cleaned = _clean_text(text)
        proba = self.pipeline.predict_proba([cleaned])[0]
        phishing_prob = float(proba[1]) if len(proba) > 1 else float(proba[0])

        is_phishing = phishing_prob >= self.THRESHOLD_MEDIUM

        if phishing_prob >= self.THRESHOLD_HIGH:
            risk_level = 'HIGH'
        elif phishing_prob >= self.THRESHOLD_MEDIUM:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'

        return {
            'text_preview': text[:120] + ('...' if len(text) > 120 else ''),
            'is_phishing':  is_phishing,
            'confidence':   round(phishing_prob * 100, 2),
            'risk_level':   risk_level,
            'label':        'Phishing' if is_phishing else 'Legitimate',
        }


# Quick standalone test
if __name__ == '__main__':
    detector = EmailDetector()
    samples = [
        "Hi team, please find the meeting notes attached.",
        "URGENT: Your account will be suspended! Verify at http://secure-login-paypal.com",
        "Thank you for your Amazon order! Your package will arrive by Tuesday.",
        "Your password expires in 24 hours. Reset: http://bit.ly/secure-login",
    ]
    for s in samples:
        r = detector.predict(s)
        print(f"[{r['risk_level']:6}] {r['label']:12} ({r['confidence']:5.1f}%)  {s[:60]}")
