# Module docstring
"""
This module contains all the routes of the main page
"""

import json

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
)
from flask_babel import gettext as _

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
    update_language,
)
from app.models import User, MazeBd, db

bp = Blueprint("principal", __name__)

# Module docstring
"""
This module contains routes related to the user's principal actions,
including accessing the dashboard, profile settings, leaderboard,
community, and managing user mazes.
"""


@bp.route("/")
@logout_required
def index():
    """
    Renders the index page. Redirects logged-in users to the dashboard.
    """
    return render_template("index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    """
    Renders the dashboard page showing user-specific statistics such as 
    completed dungeons and points.
    """
    user = User.query.get(session["user_id"])
    completed_dungeons = len(user.completed_dungeons)
    max_dungeon = None
    if user.completed_dungeons:
        max_dungeon = max(
            user.completed_dungeons, key=lambda dungeon: dungeon.maze_size
        )
        max_size = max_dungeon.maze_size
    else:
        max_size = 0  # If no dungeons are completed, size is 0

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
    """
    Displays the leaderboard, sorted by a specified criterion ('completed_dungeons' or 'points'),
    in ascending or descending order.
    """
    sort_by = request.args.get(
        "sort_by", "completed_dungeons"
    )  # Default sort by 'completed_dungeons'
    order = request.args.get("order", "desc")

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
    users_sorted = sorted(
        users_list, key=lambda u: u[sort_by], reverse=reverse_order)
    return render_template("leaderboard.html", users=users_sorted)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """
    Displays and updates the user's profile, including avatar selection.
    """
    user = User.query.get_or_404(session["user_id"])

    if request.method != "POST":
        return render_template("profile.html", user=user, avatars=AVATARS)

    if selected_avatar := request.form.get("avatar"):
        user.avatar = selected_avatar
        db.session.commit()
        flash(_("Avatar updated successfully!"), "success")
    else:
        flash(_("Please, select an avatar."), "danger")
    return redirect("/profile")


@bp.route("/profile/<int:user_id>")
@login_required
def profileusers(user_id):
    """
    Displays the profile of a user specified by user_id.
    """
    user = User.query.get_or_404(user_id)
    return render_template("profile.html", user=user)


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """
    Allows the user to update their account settings such as password, email, and language.
    """
    user = User.query.get(session["user_id"])

    if request.method == "POST":
        if "update_password" in request.form:
            return update_password(user)

        if "update_email" in request.form:
            return update_email(user)

        if "delete_account" in request.form:
            return delete_account(user)

        if "update_language" in request.form:
            return update_language(user)

    return render_template("settings.html")


@bp.route("/community")
@login_required
def community():
    """
    Displays a list of public mazes in the community, with pagination.
    """
    filter_by = request.args.get("filter", "created_at_desc")
    page = request.args.get("page", 1, type=int)
    per_page = 8

    query = build_maze_query(filter_by)

    paginated_mazes = query.paginate(page=page, per_page=per_page)

    mazes_serialized = serialize_mazes(paginated_mazes)

    pagination = {
        "page": paginated_mazes.page,
        "total_pages": paginated_mazes.pages,
        "has_next": paginated_mazes.has_next,
        "has_prev": paginated_mazes.has_prev,
        "next_num": paginated_mazes.next_num,
        "prev_num": paginated_mazes.prev_num,
    }

    return render_template(
        "community.html", mazes=json.dumps(mazes_serialized), pagination=pagination
    )


@bp.route("/dungeons")
@login_required
def my_mazes():
    """
    Displays a list of mazes that the logged-in user has created.
    """
    user_id = session["user_id"]
    user_mazes = MazeBd.query.filter_by(user_id=user_id).all()

    user_mazes_serialized = serialize_mazes(user_mazes)

    return render_template("user_mazes.html", mazes=json.dumps(user_mazes_serialized))
