import os
from flask import Flask
from flask_login import LoginManager
from config import config
from database.models import db, User


def create_app(config_name: str = None) -> Flask:
    """Application factory."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # ── Configuration ────────────────────────────────────────────────────────
    app.config.from_object(config.get(config_name, config['default']))

    # ── Extensions ───────────────────────────────────────────────────────────
    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    # ── Blueprints ───────────────────────────────────────────────────────────
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.api  import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # ── Database ─────────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app


# ── Entry point ──────────────────────────────────────────────────────────────
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
