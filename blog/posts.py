from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from db import get_db

posts = Blueprint("posts", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@posts.route("/")
def index():
    db = get_db()
    rows = db.execute(
        "SELECT p.id, p.title, p.body, p.created_at, u.username "
        "FROM posts p JOIN users u ON p.author_id = u.id "
        "ORDER BY p.created_at DESC"
    ).fetchall()
    db.close()
    return render_template("index.html", posts=rows)


@posts.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "")

        error = None
        if not title or len(title) > 200:
            error = "Title must be 1-200 characters."
        elif not body.strip():
            error = "Post body cannot be empty."

        if error:
            flash(error, "error")
            return render_template("create.html", title=title, body=body)

        db = get_db()
        db.execute(
            "INSERT INTO posts (title, body, author_id) VALUES (?, ?, ?)",
            (title, body, session["user_id"]),
        )
        db.commit()
        db.close()

        flash("Post created successfully.", "success")
        return redirect(url_for("posts.index"))

    return render_template("create.html")


@posts.route("/post/<int:post_id>")
def view(post_id):
    db = get_db()
    row = db.execute(
        "SELECT p.id, p.title, p.body, p.created_at, u.username "
        "FROM posts p JOIN users u ON p.author_id = u.id "
        "WHERE p.id = ?",
        (post_id,),
    ).fetchone()
    db.close()

    if row is None:
        flash("Post not found.", "error")
        return redirect(url_for("posts.index"))

    return render_template("post.html", post=row)
