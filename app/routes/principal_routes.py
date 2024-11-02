import json

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
)

from app.controllers.auth_controllers import (
    AVATARS,
    delete_account,
    login_required,
    logout_required,
    update_email,
    update_password,
)
from app.controllers.principal_controllers import (
    build_maze_query,
    serialize_mazes,
)
from app.models import User, MazeBd, db

bp = Blueprint("principal", __name__)


@bp.route("/")
@logout_required
def index():
    return render_template("index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])
    completed_dungeons = len(user.completed_dungeons)
    max_dungeon = None
    if user.completed_dungeons:
        max_dungeon = max(
            user.completed_dungeons, key=lambda dungeon: dungeon.maze_size
        )
        max_size = max_dungeon.maze_size
    else:
        max_size = 0  # Si no ha completado dungeons, el tamaño es 0

    points = user.points
    return render_template(
        "dashboard.html",
        completed_dungeons=completed_dungeons,
        points=points,
        max_size=max_size,
    )


@bp.route("/leaderboard")
@login_required
def leaderboard():

    sort_by = request.args.get(
        "sort_by", "completed_dungeons"
    )  # 'completed_dungeons' como valor predeterminado
    order = request.args.get("order", "desc")  # 'desc' como valor predeterminado

    users = User.query.all()
    users_list = [
        {
            "username": user.username,
            "completed_dungeons": len(user.completed_dungeons),
            "points": user.points,
            "max_size": (
                max(
                    user.completed_dungeons, key=lambda dungeon: dungeon.maze_size
                ).maze_size
                if user.completed_dungeons
                else 0
            ),
        }
        for user in users
    ]

    reverse_order = order == "desc"
    users_sorted = sorted(users_list, key=lambda u: u[sort_by], reverse=reverse_order)
    return render_template("leaderboard.html", users=users_sorted)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.get_or_404(session["user_id"])

    if request.method != "POST":
        return render_template("profile.html", user=user, avatars=AVATARS)

    if selected_avatar := request.form.get("avatar"):
        user.avatar = selected_avatar
        db.session.commit()
        flash("Avatar actualizado con éxito!", "success")
    else:
        flash("Por favor, selecciona un avatar.", "danger")
    return redirect("/profile")


@bp.route("/profile/<int:user_id>")
@login_required
def profileusers(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("profile.html", user=user)


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user = User.query.get(session["user_id"])

    if request.method == "POST":
        # Actualizar contraseña
        if "update_password" in request.form:
            return update_password(user)

        elif "update_email" in request.form:
            return update_email(user)

        elif "delete_account" in request.form:
            return delete_account(user)

    return render_template("settings.html")


@bp.route("/community")
@login_required
def community():
    # Obtener los parámetros de la solicitud, como el filtro y la página
    filter_by = request.args.get("filter", "created_at_desc")
    page = request.args.get("page", 1, type=int)
    per_page = 8

    # Construir la consulta base, uniendo con la tabla User
    query = build_maze_query(filter_by)

    # Paginación de los resultados
    paginated_mazes = query.paginate(page=page, per_page=per_page)

    # Serializar los laberintos
    mazes_serialized = serialize_mazes(paginated_mazes)

    # Manejo de la paginación
    pagination = {
        "page": paginated_mazes.page,
        "total_pages": paginated_mazes.pages,
        "has_next": paginated_mazes.has_next,
        "has_prev": paginated_mazes.has_prev,
        "next_num": paginated_mazes.next_num,
        "prev_num": paginated_mazes.prev_num,
    }

    # Devolver la plantilla con los datos
    return render_template(
        "community.html", mazes=json.dumps(mazes_serialized), pagination=pagination
    )


@bp.route("/dungeons")
@login_required
def my_mazes():
    user_id = session["user_id"]
    user_mazes = MazeBd.query.filter_by(user_id=user_id).all()

    # Convertir los mazes a diccionarios serializables
    user_mazes_serialized = serialize_mazes(user_mazes)

    return render_template("user_mazes.html", mazes=json.dumps(user_mazes_serialized))
