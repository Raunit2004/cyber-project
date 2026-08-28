import re
import urllib.parse
from urllib.parse import urlparse

class URLFeatureExtractor:
    """Extracts features from URLs for phishing detection."""

    def __init__(self):
        self.suspicious_keywords = [
            'login', 'verify', 'update', 'secure', 'account', 'bank', 
            'paypal', 'apple', 'support', 'service', 'confirm', 'password',
            'auth', 'billing', 'admin'
        ]
        
        self.shortening_services = [
            'bit.ly', 'goo.gl', 't.co', 'tinyurl.com', 'is.gd', 'cli.gs', 
            'yfrog.com', 'migre.me', 'ff.im', 'tiny.cc', 'url4.eu', 'twit.ac', 
            'su.pr', 'twurl.nl', 'snipurl.com', 'short.to', 'BudURL.com', 
            'ping.fm', 'post.ly', 'Just.as', 'bkite.com', 'snipr.com', 
            'fic.kr', 'loopt.us', 'doiop.com', 'short.ie', 'kl.am', 'wp.me', 
            'rubyurl.com', 'om.ly', 'to.ly', 'bit.do', 't.co', 'lnkd.in', 
            'db.tt', 'qr.ae', 'adf.ly', 'bitly.com', 'cur.lv', 'ow.ly', 
            'ity.im', 'q.gs', 'is.gd', 'po.st', 'bc.vc', 'twitthis.com', 
            'u.to', 'j.mp', 'buzurl.com', 'cutt.us', 'u.bb', 'yourls.org', 
            'x.co', 'prettylinkpro.com', 'scrnch.me', 'filoops.info', 
            'vzturl.com', 'qr.net', '1url.com', 'tweez.me', 'v.gd', 'tr.im', 
            'link.zip.net'
        ]

    def extract_features(self, url: str) -> dict:
        """Extracts numerical and boolean features from a single URL."""
        
        # Parse URL
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            path = parsed.path
        except:
            domain = ""
            path = ""

        # Basic length features
        features = {
            'url_length': len(url),
            'domain_length': len(domain),
            'path_length': len(path),
        }

        # Character counts
        features['num_dots'] = url.count('.')
        features['num_hyphens'] = url.count('-')
        features['num_underscores'] = url.count('_')
        features['num_slashes'] = url.count('/')
        features['num_question_marks'] = url.count('?')
        features['num_equal_signs'] = url.count('=')
        features['num_at_symbols'] = url.count('@')
        features['num_ampersands'] = url.count('&')
        features['num_exclamation_marks'] = url.count('!')
        features['num_digits'] = sum(c.isdigit() for c in url)
        
        # Subdomains (rough estimate by counting dots in domain)
        features['num_subdomains'] = domain.count('.') if domain else 0

        # Boolean features (1 or 0)
        features['has_https'] = 1 if url.startswith('https://') else 0
        features['has_ip_address'] = 1 if self._has_ip_address(domain) else 0
        features['is_shortened'] = 1 if self._is_shortened(domain) else 0
        
        # Keyword counting
        features['num_suspicious_keywords'] = sum(
            1 for keyword in self.suspicious_keywords if keyword in url.lower()
        )

        return features

    def _has_ip_address(self, domain: str) -> bool:
        """Checks if the domain is an IP address."""
        ip_pattern = re.compile(
            r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.'
            r'([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5]))'
        )
        return bool(ip_pattern.search(domain))

    def _is_shortened(self, domain: str) -> bool:
        """Checks if the URL uses a known shortening service."""
        return any(short_service in domain for short_service in self.shortening_services)

# For testing independently
if __name__ == "__main__":
    extractor = URLFeatureExtractor()
    test_urls = [
        "https://example.com/login",
        "http://192.168.1.1/admin",
        "https://bit.ly/3xyz"
    ]
    for u in test_urls:
        print(f"URL: {u}")
        print(extractor.extract_features(u))
        print("-" * 40)
