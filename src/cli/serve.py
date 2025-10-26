"""
WSGI entry point and CLI launcher for the ComfyUI web application.
"""
from __future__ import annotations

import os

from src.app import create_app, socketio

app = create_app()


def main() -> None:
    """Launch the Socket.IO server using environment configuration."""
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
    )


if __name__ == "__main__":
    main()
