import json
import os
import re
from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user
from database.models import ScanHistory, db

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ─── Lazy-load detectors so the app starts even if models are missing ──────────

_url_detector   = None
_email_detector = None


def get_url_detector():
    global _url_detector
    if _url_detector is None:
        from detection.url_detector import URLDetector
        _url_detector = URLDetector()
    return _url_detector


def get_email_detector():
    global _email_detector
    if _email_detector is None:
        from detection.email_detector import EmailDetector
        _email_detector = EmailDetector()
    return _email_detector


# ─── Helper ────────────────────────────────────────────────────────────────────

def redact_sensitive_data(text: str) -> str:
    """Redact passwords and API keys from scanned input before saving."""
    if not isinstance(text, str):
        return text
    # Mask URL query parameters (e.g., password=..., api_key=...)
    text = re.sub(r'(?i)(password|pass|pwd|api_?key|key|token|secret)=([^&\s]+)', r'\1=***', text)
    # Mask Bearer tokens
    text = re.sub(r'(?i)(bearer\s+)[A-Za-z0-9\-\._~+]+', r'\1***', text)
    # Mask Google API keys or similar structured keys
    text = re.sub(r'(AIza[0-9A-Za-z\-_]{35})', r'***', text)
    return text


def _save_scan(scan_type: str, input_value: str, label: str,
               risk_level: str, confidence: float):
    """Persist a scan record to the database."""
    user_id = current_user.id if current_user.is_authenticated else None
    
    redacted_input = redact_sensitive_data(input_value)
    
    record = ScanHistory(
        user_id=user_id,
        scan_type=scan_type,
        input_value=redacted_input[:2000],   # cap stored length
        label=label,
        risk_level=risk_level,
        confidence=confidence,
    )
    db.session.add(record)
    db.session.commit()
    return record


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@api_bp.route('/scan/url', methods=['POST'])
def scan_url():
    """
    POST /api/scan/url
    Body: { "url": "https://example.com" }
    """
    data = request.get_json(silent=True) or {}
    url  = (data.get('url') or '').strip()

    if not url:
        return jsonify({'error': 'No URL provided.'}), 400

    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'http://' + url

    try:
        detector = get_url_detector()
        result   = detector.predict(url)
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        current_app.logger.error(f"URL scan error: {e}")
        return jsonify({'error': 'Detection failed. Please try again.'}), 500

    record = _save_scan('url', url, result['label'],
                        result['risk_level'], result['confidence'])

    return jsonify({
        'id':           record.id,
        'url':          url,
        'label':        result['label'],
        'is_malicious': result['is_malicious'],
        'risk_level':   result['risk_level'],
        'confidence':   result['confidence'],
        'features':     result['features'],
        'scanned_at':   record.scanned_at.strftime('%Y-%m-%d %H:%M:%S'),
    })


@api_bp.route('/scan/email', methods=['POST'])
def scan_email():
    """
    POST /api/scan/email
    Body: { "text": "email body here..." }
    """
    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip()

    if not text:
        return jsonify({'error': 'No email text provided.'}), 400

    try:
        detector = get_email_detector()
        result   = detector.predict(text)
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        current_app.logger.error(f"Email scan error: {e}")
        return jsonify({'error': 'Detection failed. Please try again.'}), 500

    record = _save_scan('email', text, result['label'],
                        result['risk_level'], result['confidence'])

    return jsonify({
        'id':           record.id,
        'label':        result['label'],
        'is_phishing':  result['is_phishing'],
        'risk_level':   result['risk_level'],
        'confidence':   result['confidence'],
        'text_preview': result['text_preview'],
        'scanned_at':   record.scanned_at.strftime('%Y-%m-%d %H:%M:%S'),
    })


@api_bp.route('/stats', methods=['GET'])
def stats():
    """Return aggregate scan stats and model metrics."""
    total_scans   = ScanHistory.query.count()
    malicious_cnt = ScanHistory.query.filter(
        ScanHistory.label.in_(['Malicious', 'Phishing'])).count()
    safe_cnt      = total_scans - malicious_cnt

    # Model metrics from file
    metrics = {}
    metrics_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'models', 'model_metrics.json'
    )
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            metrics = json.load(f)

    return jsonify({
        'total_scans':   total_scans,
        'malicious':     malicious_cnt,
        'safe':          safe_cnt,
        'model_metrics': metrics,
    })


@api_bp.route('/history', methods=['GET'])
def history():
    """Return last 50 scans as JSON (for the current user or all guests)."""
    user_id = current_user.id if current_user.is_authenticated else None
    q = ScanHistory.query
    if user_id:
        q = q.filter_by(user_id=user_id)
    records = q.order_by(ScanHistory.scanned_at.desc()).limit(50).all()
    return jsonify([r.to_dict() for r in records])
