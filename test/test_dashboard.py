def test_redirect_map_creator(add_user, login_user):
    
    response = login_user.get('/map_creator')
    
    assert response.status_code == 200

def test_redirect_train_ai(login_user):
    
    response = login_user.get('/train-ai')
    
    assert response.status_code == 404