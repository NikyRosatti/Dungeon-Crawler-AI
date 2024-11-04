import bcrypt
from functools import wraps

from flask import redirect, render_template, request, session, url_for

from app.models import User, db

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


# Decorador de login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("principal.index"))
        return f(*args, **kwargs)

    return decorated_function


def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" in session:
            return redirect(url_for("principal.dashboard"))
        return f(*args, **kwargs)

    return decorated_function


def update_password(user):
    current_password = request.form["current_password"].encode("utf-8")
    new_password = request.form["new_password"].encode("utf-8")
    confirm_password = request.form["confirm_password"].encode("utf-8")

    if not bcrypt.checkpw(current_password, user.password.encode("utf-8")):
        return render_template("settings.html", error="Incorrect current password.")

    if new_password != confirm_password:
        return render_template("settings.html", error="New passwords do not match.")

    hashed_new_password = bcrypt.hashpw(new_password, bcrypt.gensalt()).decode("utf-8")

    user.password = hashed_new_password
    db.session.commit()

    return render_template("settings.html", success="Password updated successfully.")


def update_email(user):
    new_email = request.form["new_email"]
    confirm_email = request.form["confirm_email"]

    if new_email != confirm_email:
        return render_template("settings.html", error="Emails do not match.")

    if User.query.filter_by(email=new_email).first():
        return render_template("settings.html", error="Email is already in use.")

    user.email = new_email
    db.session.commit()

    return render_template("settings.html", success="Email updated successfully.")


def delete_account(user):
    special_user = User.query.filter_by(username="TheVoidItself").first()

    for maze in user.mazes:
        maze.user_id = special_user.id

    db.session.commit()

    db.session.delete(user)
    db.session.commit()

    session.clear()
    return redirect(url_for("auth.register"))
