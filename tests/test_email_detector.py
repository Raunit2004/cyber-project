import pytest
from detection.email_detector import EmailDetector, _clean_text

def test_clean_text():
    assert _clean_text("Hello World!") == "hello world"
    assert _clean_text("Visit http://example.com now") == "visit urltoken now"
    assert _clean_text("SOME CAPS AND numbers 123") == "some caps and numbers"

def test_email_detector_legitimate():
    detector = EmailDetector()
    result = detector.predict("Hi team, please find the attached quarterly report. Let me know if you need any clarification.")
    assert result['is_phishing'] is False
    assert result['label'] == 'Legitimate'
    assert result['risk_level'] == 'LOW'

def test_email_detector_phishing():
    detector = EmailDetector()
    result = detector.predict("URGENT: Your account has been compromised. Please update your details immediately at http://secure-login-paypal.com/verify to prevent account suspension.")
    assert result['is_phishing'] is True
    assert result['label'] == 'Phishing'
    assert result['risk_level'] in ['HIGH', 'MEDIUM']
