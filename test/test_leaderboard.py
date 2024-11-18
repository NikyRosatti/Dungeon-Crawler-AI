from app.models import User

def test_leaderboard_display(login_user, add_user):
    response = login_user.get('/leaderboard')
    
    assert response.status_code == 200
    
    assert b'Leaderboard' in response.data
    
    assert b'usuario_test' in response.data
