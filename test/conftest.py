import pytest
import warnings
from app import create_app, db
from config import TestConfig
from app.models import User
import bcrypt

@pytest.fixture(scope='module')
def test_client():
    """Crear un cliente de prueba para las solicitudes HTTP."""
    app = create_app(TestConfig)
    client = app.test_client()

    with app.app_context():
        db.create_all()
        yield client  # Proveer el cliente para las pruebas

    # Después de las pruebas, limpiar la base de datos
    with app.app_context():
        db.drop_all()

@pytest.fixture(autouse=True)
def suppress_warnings():
    """Suprime los warnings de deprecación durante las pruebas."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
        yield

@pytest.fixture
def add_user(test_client):
    existing_user = User.query.filter_by(email='usuario@test.com').first()

    if not existing_user:
        user = User(username='usuario_test', password=bcrypt.hashpw(b'password', bcrypt.gensalt()), email='usuario@test.com', avatar='/static/img/avatars/NikyAvatar.png')
        db.session.add(user)
        db.session.commit()
        
@pytest.fixture
def login_user(test_client):
    response = test_client.post('/login', data={
        'username': 'usuario_test',
        'password': 'password'
    })
    assert response.status_code == 302
    return test_client
