import functools
import logging

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from recipemod.db import get_db
from recipemod.repository import get_user_by_id, get_user_by_name

logger = logging.getLogger(__name__)

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        logger.info("Registering new user with name %s", username)
        db = get_db()
        with db.cursor() as c:
            error = None

            if not username:
                error = {"type": "danger", "text": "Username is required."}
            elif not password:
                error = {"type": "danger", "text": "Password is required"}
            else:
                c.execute("SELECT id FROM users WHERE username = %s;", (username,))
                if c.fetchone():
                    error = {
                        "type": "danger",
                        "text": f"User {username} is already registered.",
                    }

            if not error:
                c.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s);",
                    (username, generate_password_hash(password)),
                )

                return redirect(url_for("auth.login"))
            if error:
                flash(**error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error_message = None
        user = get_user_by_name(username)
        if not user:
            error_message = "Incorrect username"
        elif not check_password_hash(user.password, password):
            error_message = "Incorrect password"

        if not error_message:
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("serve_app"))

        flash(error_message, "danger")

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if not user_id:
        g.user = None
    else:
        user = get_user_by_id(user_id)
        g.user = user


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("serve_app"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.route("/change_password", methods=("GET", "POST"))
def change_password():
    if request.method == "POST":
        error_message = None

        logger.info("Changing password for user %s", g.user.username)
        current_password = request.form["current-password"]
        new_password = request.form["new-password"]

        if not new_password == request.form["confirm-new-password"]:
            error_message = "New passwords don't match"

        if not check_password_hash(g.user.password, current_password):
            error_message = "Incorrect current password"

        if not error_message:
            db = get_db()
            with db.cursor() as c:
                c.execute(
                    "UPDATE users SET password = %(password)s WHERE id = %(id)s;",
                    {
                        "password": generate_password_hash(new_password),
                        "id": g.user.id,
                    },
                )
            db.commit()
            logger.info("Updated password for user %s", g.user.username)

            flash("Password successfully changed", "success")
            return redirect("/")

        flash(error_message, "danger")

    return render_template("auth/change_password.html")
