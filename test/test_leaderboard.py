"""
Tests for the leaderboard page functionalities in the web application.
"""


def test_leaderboard_display(login_user):
    """Test that the leaderboard page loads correctly and displays expected content."""
    response = login_user.get('/leaderboard')
    assert response.status_code == 200
    assert b'Leaderboard' in response.data
    assert b'usuarioTest' in response.data
