import functools

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

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
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
        db = get_db()
        with db.cursor() as c:
            error = None
            c.execute("SELECT * FROM users WHERE username = %s;", (username,))
            user = c.fetchone()
            if not user:
                error = {"type": "danger", "text": "Incorrect username"}
            elif not check_password_hash(user["password"], password):
                error = {"type": "danger", "text": "Incorrect password"}
            if not error:
                session.clear()
                session["user_id"] = user["id"]
                return redirect(url_for("serve_app"))

            flash(error)

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if not user_id:
        g.user = None
    else:
        db = get_db()
        with db.cursor() as c:
            c.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
            user = c.fetchone()
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
        message = None
        user = g.user
        print(request.form)
        current_password = request.form["current-password"]
        new_password = request.form["new-password"]
        if not new_password == request.form["confirm-new-password"]:
            message = {"type": "danger", "text": "New passwords don't match"}
        if not check_password_hash(user["password"], current_password):
            message = {"type": "danger", "text": "Incorrect current password"}

        if not message:
            db = get_db()
            with db.cursor() as c:
                c.execute(
                    "UPDATE users SET password = %(password)s " "WHERE id = %(id)s;",
                    {"password": generate_password_hash(password), "id": user["id"]},
                )
            db.commit()
            message = {"type": "success", "text": "Password successfully changed"}
        flash(message)
    return render_template("auth/change_password.html")
