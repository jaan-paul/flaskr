from typing import *
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
from .db import get_db


blueprint = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view: Callable) -> Callable:
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        else:
            return view(**kwargs)

    return wrapped_view


# QUESTION: We just load stuff to g.user with the only basis is user_id being
# set to a UserId from Users table? Sure the session cookie is tamper proof, but
# what prevents the user from just reusing a previous session cookie, or
# stealing one to login as someone else? Should we protect the user from that?
@blueprint.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().users.select_by_id(user_id)


@blueprint.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username, password = request.form["username"], request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif db.select_by_username(username) is not None:
            error = f"User {username} is already registered."

        if error is None:
            db.insert(username, password)
            return redirect(url_for("auth.login"))
        else:
            flash(error)

    return render_template("auth/register.html")


@blueprint.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username, password = request.form["username"], request.form["password"]
        db = get_db()
        error = None
        user = db.select_by_username(username)

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["PasswordHash"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["Id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@blueprint.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
