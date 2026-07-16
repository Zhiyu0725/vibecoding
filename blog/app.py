import os
import secrets
from flask import Flask
from db import init_db
from auth import auth
from posts import posts

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

app.register_blueprint(auth)
app.register_blueprint(posts)

init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
