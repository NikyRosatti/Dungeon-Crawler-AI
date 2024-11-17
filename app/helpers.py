from flask import session

def get_user_language():
    from app.models import User
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        if user and user.language:
            return user.language
    return None
