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
            connection = get_db().connection
            connection.execute(
                "INSERT INTO Posts (Title, Body, AuthorId)"
                "   VALUES(?, ?, ?)",
                (title, body, g.user["Id"]),
            )
            connection.commit()

            return redirect(url_for("blog.index"))

    return render_template("blog/create.jinja")


@blueprint.route("/<int:post_id>/update", methods=("GET", "POST"))
@login_required
def update(post_id: int):
    post = _get_post(post_id)

    if request.method == "POST":
        title, body = request.form["title"], request.form["body"]
        error = "Title is required." if not title else None

        if error is not None:
            flash(error)
        else:
            connection = get_db().connection
            connection.execute(
                "UPDATE Posts SET Title = ?, Body = ? WHERE Id = ?",
                (title, body, post_id),
            )
            connection.commit()

            return redirect(url_for("blog.index"))

    return render_template("blog/update.jinja", post=post)


@blueprint.route("/<int:post_id>/delete", methods=("POST",))
@login_required
def delete(post_id: int):
    _get_post(post_id)

    connection = get_db().connection
    connection.execute("DELETE FROM Posts WHERE Id = ?", (post_id,))
    connection.commit()

    return redirect(url_for("blog.index"))


# Get post from the database with post_id. Uses abort(404) to signal
# non-existent post or in the case of check_author being True, abort(403).
#
# abort throws an exception with the given HTTP status code.
def _get_post(post_id: int, check_author: bool = True):
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
        # 404: Not Found.
        abort(404, f"Post Id {post_id} does not exist.")

    if check_author and post["AuthorId"] != g.user["Id"]:
        # 403: Forbidden.
        abort(403)

    return post

