import os
import sys
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database.models import db, User

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's cli commands."""
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    """Create a sample user in the database."""
    with app.app_context():
        user = User()
        user.username = "testuser"
        user.email = "test@example.com"
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        yield db
