"""
Configuration file for pytest fixtures used in testing the application.
"""
import pytest
import warnings
import bcrypt

from app import create_app, db
from config import TestConfig
from app.models import User


@pytest.fixture(scope='module')
def test_client():
    """Create a test client for HTTP requests."""
    app = create_app(TestConfig)
    client = app.test_client()

    with app.app_context():
        db.create_all()
        yield client  # Provide the client for the tests

    # After the tests, clean the database
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def suppress_warnings():
    """Suppress deprecation warnings during the tests."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
        yield


@pytest.fixture
def add_user():
    """Adds a test user to the database."""
    existing_user = User.query.filter_by(email='usuario@test.com').first()

    if not existing_user:
        user = User(
            username='usuarioTest',
            password=bcrypt.hashpw(
                b'password', bcrypt.gensalt()
            ).decode('utf-8'),
            email='usuario@test.com',
            avatar='/static/img/avatars/NikyAvatar.png'
        )
        db.session.add(user)
        db.session.commit()


@pytest.fixture
def login_user(test_client, add_user):
    """Simulates logging in to set up future tests."""
    response = test_client.post(
        '/login',
        data={
            'username': 'usuarioTest',
            'password': 'password'
        }
    )
    assert response.status_code == 302
    return test_client
