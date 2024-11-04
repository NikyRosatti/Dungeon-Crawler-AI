import bcrypt
from sqlalchemy import or_

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.models import User, db
from app.controllers.auth_controllers import login_required, logout_required, AVATARS

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
@logout_required
def login():
    if request.method != "POST":
        return render_template("login.html")
    username = request.form["username"].strip()
    if username == "TheVoidItself":
        return render_template("login.html")
    password = request.form["password"].strip().encode("utf-8")

    user = User.query.filter(
        or_(User.username == username, User.email == username)
    ).first()

    if not user:
        return render_template("login.html", error="User does not exist."), 400

    if not bcrypt.checkpw(password, user.password.encode("utf-8")):
        return render_template("login.html", error="Incorrect credentials."), 400

    session["user_id"] = user.id
    return redirect(url_for("principal.dashboard"))


@bp.route("/logout")
@login_required
def logout():
    session.pop("user_id", None)
    session.clear()
    session.clear()
    return redirect(url_for("auth.login"))


@bp.route("/register", methods=["GET", "POST"])
@logout_required
def register():
    if request.method != "POST":
        return render_template("register.html", avatars=AVATARS)

    username = request.form["username"]
    password = request.form["password"].encode("utf-8")
    email = request.form["email"]
    avatar = request.form["avatar"]

    if not avatar:
        return render_template(
            "register.html", error="Debes seleccionar un avatar", avatars=AVATARS
        )

    existing_user = User.query.filter(
        or_(User.username == username, User.email == email)
    ).first()

    if existing_user:
        return (
            render_template("register.html", error="Usuario ya registrado"),
            400,
        )  # Error 400, bad request

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
