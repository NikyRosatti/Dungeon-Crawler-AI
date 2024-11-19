"""
This module contains controllers for handling authentication-related tasks, such as
user login, logout, updating password and email, and deleting user accounts.
It also includes decorators for protecting routes that require login.
"""

from functools import wraps
import bcrypt
from flask import redirect, render_template, request, session, url_for
from flask_babel import gettext as _

from app.models import User, db

# List of avatar images available for users
AVATARS = [
    "/static/img/avatars/ValenAvatar.png",
    "/static/img/avatars/NikyAvatar.png",
    "/static/img/avatars/EstebanAvatar.png",
    "/static/img/avatars/GonzaAvatar.png",
    "/static/img/avatars/FlorAvatar.png",
    "/static/img/avatars/JoaquinTAvatar.png",
    "/static/img/avatars/JoaquinBAvatar.png",
    "/static/img/avatars/BrusattiAvatar.png",
    "/static/img/avatars/SimonAvatar.png",
    "/static/img/avatars/AgusAvatar.png",
]


# Decorator to require login for accessing a route
def login_required(f):
    """
    Decorator to ensure that the user is logged in before accessing the route.
    If the user is not logged in, they are redirected to the index page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("principal.index"))
        return f(*args, **kwargs)

    return decorated_function


# Decorator to require logout for accessing a route
def logout_required(f):
    """
    Decorator to ensure that the user is logged out before accessing the route.
    If the user is logged in, they are redirected to their dashboard.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" in session:
            return redirect(url_for("principal.dashboard"))
        return f(*args, **kwargs)

    return decorated_function


def update_password(user):
    """
    Update the password for the given user. It checks if the current password is correct
    and if the new password matches the confirmation password.
    After successful validation, the new password is hashed and saved.
    """
    current_password = request.form["current_password"].encode("utf-8")
    new_password = request.form["new_password"].encode("utf-8")
    confirm_password = request.form["confirm_password"].encode("utf-8")

    if not bcrypt.checkpw(current_password, user.password.encode("utf-8")):
        return render_template("settings.html", error=_("Incorrect current password."))

    if new_password != confirm_password:
        return render_template("settings.html", error=_("New passwords do not match."))

    hashed_new_password = bcrypt.hashpw(
        new_password, bcrypt.gensalt()).decode("utf-8")

    user.password = hashed_new_password
    db.session.commit()

    return render_template("settings.html", success=_("Password updated successfully."))


def update_email(user):
    """
    Update the email for the given user. It checks if the new email matches the confirmation
    email and if the email is already in use by another user.
    """
    new_email = request.form["new_email"]
    confirm_email = request.form["confirm_email"]

    if new_email != confirm_email:
        return render_template("settings.html", error=_("Emails do not match."))

    if User.query.filter_by(email=new_email).first():
        return render_template("settings.html", error=_("Email is already in use."))

    user.email = new_email
    db.session.commit()

    return render_template("settings.html", success=_("Email updated successfully."))


def delete_account(user):
    """
    Delete the account of the given user. All mazes associated with the user are reassigned
    to a special user, and the user account is deleted. The user is logged out after deletion.
    """
    special_user = User.query.filter_by(username="TheVoidItself").first()

    for maze in user.mazes:
        maze.user_id = special_user.id

    db.session.commit()

    db.session.delete(user)
    db.session.commit()

    session.clear()
    return redirect(url_for("auth.register"))
