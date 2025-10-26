"""
Service layer exports.
"""
from .generation import (
    add_more_requests,
    add_client,
    get_preset_prompts,
    get_status_snapshot,
    handle_history_switch,
    remove_client,
    remove_generated_image,
    save_upload_file,
    start_generation_request,
    stop_generation_request,
)

__all__ = [
    "add_client",
    "remove_client",
    "start_generation_request",
    "stop_generation_request",
    "get_status_snapshot",
    "get_preset_prompts",
    "save_upload_file",
    "remove_generated_image",
    "add_more_requests",
    "handle_history_switch",
]
