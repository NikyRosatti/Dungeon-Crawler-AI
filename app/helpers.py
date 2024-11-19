"""
Helper module to handle functions related to user session and language retrieval.
"""

from flask import session
from app.models import User  # Import at the top level for better clarity and consistency

def get_user_language():
    """
    Retrieves the language preference of the current user stored in the session.

    Returns the language set by the user if available, or None if there is no
    user or the language is not set.
    """
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        if user and user.language:
            return user.language
    return None
