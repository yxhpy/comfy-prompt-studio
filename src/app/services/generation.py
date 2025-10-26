"""
Generation service encapsulating stateful image generation workflow.
"""
from __future__ import annotations

import os
import threading
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from src.core.comfyui.client import generate_image_with_comfyui
from src.core.history.manager import history_manager
from src.core.prompt.generator import generate_prompt

from ..extensions import socketio

PROJECT_ROOT = Path(__file__).resolve().parents[3]
GENERATED_DIR = PROJECT_ROOT / "static" / "generated"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}

# Tracking connected websocket clients
_connected_clients: set[str] = set()

# Global generation state (single worker model)
_current_generation: Dict[str, Optional[object]] = {
    "is_running": False,
    "current_prompt": None,
    "prompt_id": None,
    "positive_prompt": None,
    "negative_prompt": None,
    "image_path": None,
    "width": 800,
    "height": 1200,
    "total_count": 10,
    "generated_count": 0,
    "images": [],
    "stop_flag": False,
}

# Synchronise access to mutable state
_state_lock = threading.Lock()


def allowed_file(filename: str) -> bool:
    """Return True if the filename extension is supported."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def add_client(sid: str) -> int:
    """Register a socket client connection."""
    _connected_clients.add(sid)
    return len(_connected_clients)


def remove_client(sid: str) -> int:
    """Remove a socket client connection."""
    _connected_clients.discard(sid)
    return len(_connected_clients)


def save_upload_file(file: FileStorage, upload_folder: str) -> Tuple[str, str]:
    """
    Persist an uploaded reference image.

    Args:
        file: Uploaded file object.
        upload_folder: Target folder path.

    Returns:
        Tuple of (filename, relative_path).

    Raises:
        ValueError: When no filename provided or extension invalid.
    """
    if not file or not file.filename:
        raise ValueError("没有选择文件")

    if not allowed_file(file.filename):
        raise ValueError("不支持的文件类型")

    sanitized = secure_filename(file.filename)
    filename = f"{uuid.uuid4().hex}_{sanitized}"
    target_dir = Path(upload_folder)
    if not target_dir.is_absolute():
        target_dir = PROJECT_ROOT / target_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / filename
    file.save(target_path)

    upload_path = Path(upload_folder)
    if upload_path.is_absolute():
        relative_path = str(upload_path / filename)
    else:
        relative_path = os.path.join(upload_folder, filename)
    return filename, relative_path


def start_generation_request(
    prompt: str,
    count: int,
    width: int,
    height: int,
    image_path: Optional[str],
) -> Dict[str, object]:
    """
    Update generation state and ensure the worker thread is running.

    Returns the updated state snapshot.
    """
    with _state_lock:
        if prompt and prompt != _current_generation["current_prompt"]:
            _reset_generation_state(prompt, width, height, image_path, count)
        else:
            _current_generation["total_count"] += count
            if image_path:
                _current_generation["image_path"] = image_path

        if not _current_generation["is_running"]:
            _current_generation["is_running"] = True
            _current_generation["stop_flag"] = False
            app_obj = current_app._get_current_object()
            thread = threading.Thread(
                target=_worker_thread,
                args=(app_obj,),
                daemon=True,
            )
            thread.start()

    return get_status_snapshot()


def stop_generation_request() -> None:
    """Signal the worker thread to stop gracefully."""
    with _state_lock:
        _current_generation["stop_flag"] = True
        _current_generation["is_running"] = False


def add_more_requests(additional_count: int) -> Dict[str, object]:
    """
    Increase the total number of images to generate and restart worker if needed.
    """
    with _state_lock:
        _current_generation["total_count"] += additional_count
        should_start = (
            not _current_generation["is_running"]
            and bool(_current_generation["current_prompt"])
        )

    if should_start:
        start_generation_request(
            _current_generation["current_prompt"],
            0,
            _current_generation["width"],
            _current_generation["height"],
            _current_generation["image_path"],
        )

    return get_status_snapshot()


def get_status_snapshot() -> Dict[str, object]:
    """Return a copy of the current generation state."""
    with _state_lock:
        return {
            "is_running": _current_generation["is_running"],
            "current_prompt": _current_generation["current_prompt"],
            "width": _current_generation["width"],
            "height": _current_generation["height"],
            "image_path": _current_generation["image_path"],
            "total_count": _current_generation["total_count"],
            "generated_count": _current_generation["generated_count"],
            "images": list(_current_generation["images"]),
        }


def get_preset_prompts() -> List[str]:
    """Read preset prompts from environment variables."""
    prompts: List[str] = []
    idx = 1
    while True:
        value = os.getenv(f"PROMPT_{idx}")
        if not value:
            break
        prompts.append(value)
        idx += 1
    return prompts


def remove_generated_image(filename: str) -> List[str]:
    """
    Delete an image from disk and state/cache.

    Args:
        filename: Prompt-relative path (prompt_id/image.png).

    Returns:
        Updated image list for the current prompt.
    """
    if not filename:
        raise ValueError("缺少文件名参数")

    parts = filename.split("/")
    if len(parts) != 2:
        raise ValueError("文件名格式不正确")

    prompt_id, image_name = parts

    # Delete file from disk
    file_path = GENERATED_DIR / prompt_id / image_name
    if file_path.exists():
        file_path.unlink()

    history_manager.remove_image(prompt_id, image_name)

    with _state_lock:
        if filename in _current_generation["images"]:
            _current_generation["images"].remove(filename)
            _current_generation["generated_count"] = len(
                _current_generation["images"]
            )

        return list(_current_generation["images"])


def handle_history_switch(prompt_id: str) -> Optional[Tuple[Dict, List[str]]]:
    """
    Load a historical prompt and update generation state accordingly.

    Returns:
        Tuple of (record, image_paths) or None when prompt not found.
    """
    record = history_manager.get_record_by_id(prompt_id)
    if not record:
        return None

    image_paths = [f"{prompt_id}/{img}" for img in record.get("images", [])]

    with _state_lock:
        _current_generation["current_prompt"] = record["prompt"]
        _current_generation["prompt_id"] = prompt_id
        _current_generation["positive_prompt"] = record.get("positive_prompt")
        _current_generation["negative_prompt"] = record.get("negative_prompt")
        _current_generation["width"] = record.get("width", 800)
        _current_generation["height"] = record.get("height", 1200)
        _current_generation["images"] = image_paths
        _current_generation["generated_count"] = len(image_paths)
        _current_generation["total_count"] = len(image_paths)
        _current_generation["image_path"] = None
        _current_generation["is_running"] = False
        _current_generation["stop_flag"] = False

    return record, image_paths


def _reset_generation_state(
    prompt: str,
    width: int,
    height: int,
    image_path: Optional[str],
    total_count: int,
) -> None:
    """Reset state for a new prompt."""
    _current_generation.update(
        {
            "current_prompt": prompt,
            "width": width,
            "height": height,
            "image_path": image_path,
            "total_count": total_count,
            "generated_count": 0,
            "images": [],
            "prompt_id": None,
            "positive_prompt": None,
            "negative_prompt": None,
        }
    )


def _worker_thread(app) -> None:
    """Continuously process generation requests while state is active."""
    with app.app_context():
        while _current_generation["is_running"]:
            if _current_generation["stop_flag"]:
                break

            _emit_progress("generating_prompt")

            def log_callback(message: str) -> None:
                socketio.emit("log", {"message": message}, room="generation")

            try:
                positive_prompt, negative_prompt = generate_prompt(
                    _current_generation["current_prompt"],
                    stream=True,
                    log_callback=log_callback,
                )
            except Exception as exc:
                _handle_worker_error(exc)
                break

            _current_generation["positive_prompt"] = positive_prompt
            _current_generation["negative_prompt"] = negative_prompt

            prompt_id = history_manager.add_record(
                _current_generation["current_prompt"],
                positive_prompt,
                negative_prompt,
                _current_generation["width"],
                _current_generation["height"],
            )
            _current_generation["prompt_id"] = prompt_id

            _emit_progress("generating_image")

            try:
                images = generate_image_with_comfyui(
                    positive_prompt,
                    negative_prompt,
                    width=_current_generation["width"],
                    height=_current_generation["height"],
                    image_path=_current_generation["image_path"],
                )
            except Exception as exc:
                _handle_worker_error(exc)
                break

            for image_data in images:
                _persist_image(prompt_id, image_data)

                if _current_generation["stop_flag"]:
                    break

            if _current_generation["generated_count"] >= _current_generation["total_count"]:
                _current_generation["is_running"] = False
                socketio.emit(
                    "generation_complete",
                    {"total": _current_generation["generated_count"]},
                    room="generation",
                )
                break


def _persist_image(prompt_id: str, image_data: bytes) -> None:
    """Save generated image to disk and update state/history."""
    filename = f"{uuid.uuid4().hex}.png"
    prompt_dir = GENERATED_DIR / prompt_id
    prompt_dir.mkdir(parents=True, exist_ok=True)

    filepath = prompt_dir / filename
    with open(filepath, "wb") as fh:
        fh.write(image_data)

    relative_path = f"{prompt_id}/{filename}"
    history_manager.update_images(prompt_id, filename)

    with _state_lock:
        _current_generation["images"].append(relative_path)
        _current_generation["generated_count"] += 1

    socketio.emit(
        "new_image",
        {
            "filename": relative_path,
            "current": _current_generation["generated_count"],
            "total": _current_generation["total_count"],
        },
        room="generation",
    )

    _emit_progress("generating")


def _emit_progress(status: str) -> None:
    """Send progress updates to clients."""
    socketio.emit(
        "progress",
        {
            "current": _current_generation["generated_count"],
            "total": _current_generation["total_count"],
            "status": status,
        },
        room="generation",
    )


def _handle_worker_error(exc: Exception) -> None:
    """Emit error messages and log stack traces."""
    socketio.emit("error", {"message": str(exc)}, room="generation")
    print(f"Error generating image: {exc}", flush=True)
    import traceback

    traceback.print_exc()
    time.sleep(1)
