from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.exceptions import abort
from http import HTTPStatus
from .auth import login_required
from .db import get_db


blueprint = Blueprint("blog", __name__)


@blueprint.route("/")
def index():
    db = get_db()
    # Get all posts and sort by most recent.
    posts = db.connection.execute(
        "SELECT P.Id, Title, Body, CreationTime, AuthorId, Username"
        "   FROM Posts P JOIN Users U ON P.AuthorId = U.Id"
        "   ORDER BY CreationTime DESC"
    ).fetchall()

    return render_template("blog/index.jinja", posts=posts)


@blueprint.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title, body = request.form["title"], request.form["body"]
        error = "Title is required." if not title else None

        if error is not None:
            flash(error)
        else:
            get_db().posts.insert(title, body, g.user["Id"])

            return redirect(url_for("blog.index"))

    return render_template("blog/create.jinja")


@blueprint.route("/<int:post_id>/update", methods=("GET", "POST"))
@login_required
def update(post_id: int):
    post = _get_post_with_author_username(post_id)

    if request.method == "POST":
        title, body = request.form["title"], request.form["body"]
        error = "Title is required." if not title else None

        if error is not None:
            flash(error)
        else:
            get_db().posts.update_content(post_id, title, body)

            return redirect(url_for("blog.index"))

    return render_template("blog/update.jinja", post=post)


@blueprint.route("/<int:post_id>/delete", methods=("POST",))
@login_required
def delete(post_id: int):
    _get_post_with_author_username(post_id)
    get_db().posts.delete(post_id)

    return redirect(url_for("blog.index"))


def _get_post_with_author_username(post_id: int, check_author: bool = True):
    post = (
        get_db()
        .connection.execute(
            "SELECT P.Id, Title, Body, CreationTime, AuthorId, Username"
            "   FROM Posts P JOIN Users U ON P.AuthorId = U.Id"
            "   WHERE P.Id = ?",
            (post_id,),
        )
        .fetchone()
    )

    if post is None:
        abort(HTTPStatus.NOT_FOUND, f"Post Id {post_id} does not exist.")

    if check_author and post["AuthorId"] != g.user["Id"]:
        abort(HTTPStatus.FORBIDDEN)

    return post

