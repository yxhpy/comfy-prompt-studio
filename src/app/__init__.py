"""
Application factory for the ComfyUI web application.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from .config import Config
from .extensions import socketio


def create_app() -> Flask:
    """
    Create and configure the Flask application instance.

    Returns:
        Configured Flask app.
    """
    load_dotenv()

    base_path = Path(__file__).resolve().parents[2]
    template_folder = base_path / "templates"
    static_folder = base_path / "static"

    app = Flask(
        __name__,
        template_folder=str(template_folder),
        static_folder=str(static_folder),
    )
    app.config.from_object(Config)

    _ensure_directories(app)
    _register_blueprints(app)

    # Initialize extensions after app is configured
    socketio.init_app(
        app,
        cors_allowed_origins="*",
        logger=False,
        engineio_logger=False,
    )

    _register_socketio_events()
    return app


def _ensure_directories(app: Flask) -> None:
    """Ensure directories used at runtime exist."""
    project_root = Path(__file__).resolve().parents[2]

    for key in ("UPLOAD_FOLDER",):
        folder = Path(app.config[key])
        if not folder.is_absolute():
            folder = project_root / folder
        folder.mkdir(parents=True, exist_ok=True)

    # Ensure generated asset directories exist
    (project_root / "static" / "generated").mkdir(parents=True, exist_ok=True)
    (project_root / "data" / "generated").mkdir(parents=True, exist_ok=True)
    (project_root / "data" / "upload").mkdir(parents=True, exist_ok=True)


def _register_blueprints(app: Flask) -> None:
    """Register Flask blueprints for routes."""
    from .routes.web import bp as web_bp
    from .routes.api import bp as api_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)


def _register_socketio_events() -> None:
    """
    Import socket event handlers so decorators run.

    Importing inside this function prevents circular imports while ensuring
    handlers register against the shared SocketIO instance.
    """
    from .events import generation  # noqa: F401  (imported for side effects)


__all__ = ["create_app", "socketio"]
