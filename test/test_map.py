"""
This module contains tests for map validation, retrieval, and training processes.

Tests included:
- Validation of existing maps.
- Retrieval of non-existent maps.
- Existence of training-related files.
"""
import os


def test_map_exist(login_user):
    """
    Test if an existing map can be validated and retrieved.
    """
    login_user.post(
        "/validate_map",
        json={"map": [2, 0, 0, 0, 0, 0, 0, 0, 3], "size": 3},
    )

    response = login_user.get('/map?maze_id=1')

    assert response.status_code == 200


def test_map_doesnt_exists(login_user):
    """
    Test if requesting a non-existent map returns 404.
    """
    response = login_user.get('/map?maze_id=10')

    assert response.status_code == 404


def test_map_trained(login_user):
    """
    Test if training-related files exist for a given map.
    """
    response = login_user.get('/map?maze_id=1')

    if response.status_code == 404:
        assert response.status_code == 404
    else:
        assert response.status_code == 200

        model_path = os.path.join("app", "saved_models",
                                  "trained_models_per_id", "1", "")

        vec_norm_path = f"{model_path}norm_env.pkl"
        model_ppo_path = f"{model_path}ppo.zip"

        if os.path.exists(vec_norm_path):
            assert os.path.exists(vec_norm_path)
        if os.path.exists(model_ppo_path):
            assert os.path.exists(model_ppo_path)