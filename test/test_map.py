

def test_map_exist(login_user):

    first_response = login_user.post(
        "/validate_map",
        json={"map": [2, 0, 0, 0, 0, 0, 0, 0, 3], "size": 3},
    )

    response = login_user.get('/map?maze_id=1')
    
    assert response.status_code == 200
    
    
def text_map_doesnt_map(login_user):
    
    response = login_user.get('/map?maze_id=1')
    
    assert response.status_code == 500
