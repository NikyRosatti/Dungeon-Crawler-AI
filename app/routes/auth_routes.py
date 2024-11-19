"""
Authentication routes for handling user login, logout, and registration.
"""

import re
import bcrypt
from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_babel import gettext as _
from app.models import User, db
from app.controllers.auth_controllers import login_required, logout_required, AVATARS

bp = Blueprint("auth", __name__)

# Email regex pattern for validation
EMAIL_REGEX_PATTERN = r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$"


@bp.route("/login", methods=["GET", "POST"])
@logout_required
def login():
    """Handles user login"""
    if request.method != "POST":
        return render_template("login.html")

    username = request.form["username"].strip()
    if username == "TheVoidItself":
        return render_template("login.html")

    password = request.form["password"].strip().encode("utf-8")
    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()

    if not user:
        return render_template("login.html", error=_("User does not exist.")), 400

    if not bcrypt.checkpw(password, user.password.encode("utf-8")):
        return render_template("login.html", error=_("Incorrect credentials.")), 400

    session["user_id"] = user.id
    return redirect(url_for("principal.dashboard"))


@bp.route("/logout")
@login_required
def logout():
    """Handles user logout"""
    session.pop("user_id", None)
    session.clear()
    return redirect(url_for("auth.login"))


@bp.route("/register", methods=["GET", "POST"])
@logout_required
def register():
    """Handles user registration"""
    if request.method != "POST":
        return render_template("register.html", avatars=AVATARS)

    username = request.form["username"]
    password = request.form["password"].encode("utf-8")
    email = request.form["email"]
    avatar = request.form.get("avatar")

    error = validate_registration_input(username, password, email, avatar)
    if error:
        return render_template("register.html", error=error, avatars=AVATARS), 400

    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    new_user = User(
        username=username,
        password=hashed_password.decode("utf-8"),
        email=email,
        avatar=avatar,
    )
    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id
    return redirect(url_for("principal.dashboard"))


def validate_registration_input(username, password, email, avatar):
    """
    Validates the registration input fields.

    Args:
        username (str): The username input.
        password (bytes): The password input (encoded).
        email (str): The email input.
        avatar (str | None): The selected avatar.

    Returns:
        str | None: Error message if validation fails, otherwise None.
    """
    if not avatar:
        return _("You must select an avatar")
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return _("Username already exists")
    if len(username) < 3:
        return _("Username must have at least 3 characters")
    if not username.isalnum():
        return _("Username can only contain letters and numbers")
    if not re.match(EMAIL_REGEX_PATTERN, email):
        return _("Please enter a valid email address")
    if len(password) < 8:
        return _("Password must have at least 8 characters")
    return None
