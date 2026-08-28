import sys
import os
import pytest

# Add parent dir to path to import preprocessing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing.url_features import URLFeatureExtractor

def test_url_length():
    extractor = URLFeatureExtractor()
    url = "https://example.com"
    features = extractor.extract_features(url)
    assert features['url_length'] == len(url)
    assert features['domain_length'] == len("example.com")

def test_has_ip_address():
    extractor = URLFeatureExtractor()
    features = extractor.extract_features("http://192.168.1.1/admin")
    assert features['has_ip_address'] == 1
    
    features2 = extractor.extract_features("https://example.com")
    assert features2['has_ip_address'] == 0

def test_suspicious_keywords():
    extractor = URLFeatureExtractor()
    features = extractor.extract_features("http://secure-login.paypal.com")
    assert features['num_suspicious_keywords'] >= 2  # 'secure', 'login', 'paypal'

def test_shortened_url():
    extractor = URLFeatureExtractor()
    features = extractor.extract_features("https://bit.ly/12345")
    assert features['is_shortened'] == 1

    features2 = extractor.extract_features("https://google.com")
    assert features2['is_shortened'] == 0
