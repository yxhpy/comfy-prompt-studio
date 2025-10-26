"""
Socket.IO event handlers for generation workflow.
"""
from __future__ import annotations

from flask import request
from flask_socketio import join_room, leave_room

from ..extensions import socketio
from ..services import add_client, remove_client


@socketio.on("connect")
def handle_connect():
    """Track new socket connection."""
    client_count = add_client(request.sid)
    join_room("generation")
    print(
        f"Client connected: {request.sid}, Total clients: {client_count}",
        flush=True,
    )


@socketio.on("disconnect")
def handle_disconnect():
    """Remove socket connection tracking on disconnect."""
    client_count = remove_client(request.sid)
    leave_room("generation")
    print(
        f"Client disconnected: {request.sid}, Total clients: {client_count}",
        flush=True,
    )
