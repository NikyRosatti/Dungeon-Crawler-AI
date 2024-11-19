import os


def test_map_exist(login_user):

    first_response = login_user.post(
        "/validate_map",
        json={"map": [2, 0, 0, 0, 0, 0, 0, 0, 3], "size": 3},
    )

    response = login_user.get('/map?maze_id=1')

    assert response.status_code == 200


def test_map_doesnt_exists(login_user):

    response = login_user.get('/map?maze_id=10')

    assert response.status_code == 404


def test_start_training(login_user):

    response = login_user.get('/map?maze_id=1')
    assert response.status_code == 200

    model_path = os.path.join("app", "saved_models",
                              "trained_models_per_id", "1", "")

    vec_norm_path = model_path + "norm_env.pkl"
    assert os.path.exists(vec_norm_path) == True
    model_ppo_path = model_path + "ppo.zip"
    assert os.path.exists(model_ppo_path) == True
