from flask import Flask

from .database import init_db
from .routes import app_bp


def create_app():
    init_db()
    app = Flask(__name__)
    app.register_blueprint(app_bp)
    return app


__all__ = ["create_app", "init_db"]
