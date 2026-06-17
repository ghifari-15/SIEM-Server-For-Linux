from flask import Flask

from .database import init_db
from .routes import main_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_bp)
    return app


__all__ = ["create_app", "init_db"]
