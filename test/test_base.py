from app.models import User


def test_redirect_dashboard(test_client, add_user):
    response = test_client.post('/login', data={
        'username': 'usuario_test',
        'password': 'password'
    })
    
    assert 'Location' in response.headers
    assert response.headers['Location'] == '/dashboard'
    
    response = test_client.get('/dashboard')
    assert response.status_code == 200

def test_redirect_dungeons(test_client):
    response = test_client.post('/login', data={
        'username': 'usuario_test',
        'password': 'password'
    })
    
    assert 'Location' in response.headers
    assert response.headers['Location'] == '/dashboard'
    
    response = test_client.get('/dungeons')
    assert response.status_code == 200

def test_redirect_profile(test_client):
    test_client.post('/login', data={
        'username': 'usuario_test',
        'password': 'password'
    })
    
    assert 'Location' in response.headers
    assert response.headers['Location'] == '/dashboard'
    
    user = User.query.filter_by(username = 'usuario_test').first()
    
    response = test_client.get('/profile', data={
        'user_id': user.id
    })
    
    assert response.status_code == 200
    assert 'Location' in response.headers
    assert response.headers['Location'] == '/profile'