"""
Application configuration.
"""
from __future__ import annotations

import os


class Config:
    """Default runtime configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "upload")
