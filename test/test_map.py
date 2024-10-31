

import os
import shutil
from app.routes import train


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
    
    train(1, "./app/test_saved_models")
    vec_norm_path = "./app/test_saved_models/vec_normalize.pkl"
    assert os.path.exists(vec_norm_path) == True
    model_ppo_path = "./app/test_saved_models/ppo_dungeons.zip"
    assert os.path.exists(model_ppo_path) == True
    
    shutil.rmtree("test_saved_models")


