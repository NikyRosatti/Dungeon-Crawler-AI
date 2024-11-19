from app.models import MazeBd, User


def test_create_map(login_user):
    response = login_user.get('/map_creator')
    assert response.status_code == 200


def test_validate_map_invalid_points(login_user):
    """
    Prueba cuando los puntos de inicio y salida no son válidos.
    """
    # Mapa sin puntos de inicio o salida
    response = login_user.post(
        "/validate_map",
        json={"map": [0, 0, 0, 0, 0, 0, 0, 0, 0], "size": 3},
    )
    data = response.get_json()
    assert response.status_code == 400
    assert data["valid"] is False
    assert data["error"] == "No se encontró el punto de inicio o salida"


def test_validate_map_valid(login_user):
    """
    Prueba cuando los puntos de inicio y salida no son válidos.
    """
    # Mapa sin puntos de inicio o salida
    response = login_user.post(
        "/validate_map",
        json={"map": [2, 0, 0, 0, 0, 0, 0, 0, 3], "size": 3},
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data["valid"] is True


def test_validate_map_imposible(login_user):
    """
    Prueba cuando los puntos de inicio y salida no son válidos.
    """
    # Mapa sin puntos de inicio o salida
    response = login_user.post(
        "/validate_map",
        json={"map": [2, 1, 1, 1, 1, 1, 1, 1, 3], "size": 3},
    )
    data = response.get_json()
    assert response.status_code == 400
    assert data["valid"] is False
    assert data["error"] == "No hay camino posible"
