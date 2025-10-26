"""
Shared application extensions.
"""
from flask_socketio import SocketIO

# Single SocketIO instance used across the app
socketio = SocketIO()

__all__ = ["socketio"]
