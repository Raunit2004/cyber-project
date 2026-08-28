from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from database.models import ScanHistory, db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page with the scan form."""
    return render_template('index.html')


@main_bp.route('/dashboard')
def dashboard():
    """Analytics dashboard – recent scans + model stats."""
    # Last 10 scans for the current user (or guest scans)
    if current_user.is_authenticated:
        recent = (ScanHistory.query
                  .filter_by(user_id=current_user.id)
                  .order_by(ScanHistory.scanned_at.desc())
                  .limit(10).all())
        total  = ScanHistory.query.filter_by(user_id=current_user.id).count()
        flagged = ScanHistory.query.filter_by(user_id=current_user.id)\
                             .filter(ScanHistory.label.in_(['Malicious', 'Phishing'])).count()
    else:
        recent  = []
        total   = 0
        flagged = 0

    return render_template('dashboard.html',
                           recent=recent,
                           total=total,
                           flagged=flagged)


@main_bp.route('/history')
def history():
    """Full paginated scan history for the logged-in user."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    page = 1
    per_page = 20

    from flask import request
    page = request.args.get('page', 1, type=int)

    pagination = (ScanHistory.query
                  .filter_by(user_id=current_user.id)
                  .order_by(ScanHistory.scanned_at.desc())
                  .paginate(page=page, per_page=per_page, error_out=False))

    return render_template('history.html', pagination=pagination)
