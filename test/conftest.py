# tests/conftest.py
import pytest
import warnings
from app import create_app, db
from config import TestConfig

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