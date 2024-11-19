"""
Tests for maze map creation and validation functionalities.
"""


def test_create_map(login_user):
    """Test if an authenticated user can access the map creator page."""
    response = login_user.get('/map_creator')
    assert response.status_code == 200


def test_validate_map_invalid_points(login_user):
    """
    Test validation fails when the map lacks valid start or exit points.
    """
    # Map without start or exit points
    response = login_user.post(
        "/validate_map",
        json={"map": [0, 0, 0, 0, 0, 0, 0, 0, 0], "size": 3},
    )
    data = response.get_json()
    assert response.status_code == 400
    assert data["valid"] is False
    assert data["error"] == "Start or exit point not found"


def test_validate_map_valid(login_user):
    """
    Test validation succeeds when the map has valid start and exit points.
    """
    response = login_user.post(
        "/validate_map",
        json={"map": [2, 0, 0, 0, 0, 0, 0, 0, 3], "size": 3},
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data["valid"] is True


def test_validate_map_imposible(login_user):
    """
    Test validation fails when there is no possible path between start and exit.
    """
    response = login_user.post(
        "/validate_map",
        json={"map": [2, 1, 1, 1, 1, 1, 1, 1, 3], "size": 3},
    )
    data = response.get_json()
    assert response.status_code == 400
    assert data["valid"] is False
    assert data["error"] == "No hay camino posible"
