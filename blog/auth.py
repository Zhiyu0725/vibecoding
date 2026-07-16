from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        error = None
        if not username or len(username) < 3 or len(username) > 20:
            error = "Username must be 3-20 characters."
        elif not username.isalnum() and not all(c.isalnum() or c == "_" for c in username):
            error = "Username may only contain letters, numbers, and underscores."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm:
            error = "Passwords do not match."

        if error is None:
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password, method="pbkdf2:sha256")),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Username '{username}' is already taken."
            finally:
                db.close()

        if error:
            flash(error, "error")
            return render_template("register.html", username=username)

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        db.close()

        error = None
        if user is None or not check_password_hash(user["password_hash"], password):
            error = "Invalid username or password."

        if error:
            flash(error, "error")
            return render_template("login.html", username=username)

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return redirect(url_for("posts.index"))

    return render_template("login.html")


@auth.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("posts.index"))
