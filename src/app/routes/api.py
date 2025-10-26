"""
API endpoints for the ComfyUI web application.
"""
from __future__ import annotations

import random
import shutil
from pathlib import Path
from typing import Any, Dict

from flask import Blueprint, current_app, jsonify, request

from src.core.history.manager import history_manager

from ..extensions import socketio
from ..services import (
    add_more_requests,
    get_preset_prompts,
    get_status_snapshot,
    handle_history_switch,
    remove_generated_image,
    save_upload_file,
    start_generation_request,
    stop_generation_request,
)

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/test_emit", methods=["POST"])
def test_emit():
    """Test emitting a message to Socket.IO clients."""
    socketio.emit("test_message", {"message": "Test from API"}, room="generation")
    return jsonify({"success": True})


@bp.route("/upload", methods=["POST"])
def upload_file():
    """Handle reference image uploads."""
    file = request.files.get("file")
    if not file:
        return jsonify({"success": False, "message": "没有文件被上传"}), 400

    try:
        filename, filepath = save_upload_file(file, current_app.config["UPLOAD_FOLDER"])
        return jsonify(
            {
                "success": True,
                "filename": filename,
                "filepath": filepath,
            }
        )
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception as exc:  # pragma: no cover - defensive
        current_app.logger.exception("上传失败: %s", exc)
        return jsonify({"success": False, "message": "上传失败"}), 500


@bp.route("/start", methods=["POST"])
def start_generation():
    """Start or continue an image generation session."""
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    prompt = data.get("prompt")
    count = int(data.get("count", 10))
    width = int(data.get("width", 800))
    height = int(data.get("height", 1200))
    image_path = data.get("image_path")

    state = start_generation_request(prompt, count, width, height, image_path)

    return jsonify(
        {
            "success": True,
            "current_prompt": state["current_prompt"],
            "total_count": state["total_count"],
        }
    )


@bp.route("/stop", methods=["POST"])
def stop_generation():
    """Stop the current generation worker."""
    stop_generation_request()
    return jsonify({"success": True})


@bp.route("/status", methods=["GET"])
def get_status():
    """Return current generation status snapshot."""
    return jsonify(get_status_snapshot())


@bp.route("/prompts", methods=["GET"])
def get_prompts():
    """Fetch preset prompts."""
    prompts = get_preset_prompts()
    if not prompts:
        return jsonify({"success": False, "message": "没有找到预设提示词"})

    selected = random.choice(prompts)
    return jsonify({"success": True, "prompt": selected, "all_prompts": prompts})


@bp.route("/delete_image", methods=["POST"])
def delete_image():
    """Delete a generated image."""
    data = request.get_json(silent=True) or {}
    filename = data.get("filename")
    if not filename:
        return jsonify({"success": False, "message": "缺少文件名参数"}), 400

    try:
        images = remove_generated_image(filename)
        return jsonify(
            {
                "success": True,
                "remaining_count": len(images),
                "images": images,
            }
        )
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception as exc:  # pragma: no cover - defensive
        current_app.logger.exception("删除图片失败: %s", exc)
        return jsonify({"success": False, "message": str(exc)}), 500


@bp.route("/history", methods=["GET"])
def get_history():
    """Return all history records."""
    records = history_manager.get_all_records()
    return jsonify({"success": True, "records": records})


@bp.route("/history/<prompt_id>", methods=["GET"])
def get_history_by_id(prompt_id: str):
    """Fetch a single history record."""
    record = history_manager.get_record_by_id(prompt_id)
    if record:
        return jsonify({"success": True, "record": record})
    return jsonify({"success": False, "message": "记录不存在"})


@bp.route("/history/<prompt_id>", methods=["DELETE"])
def delete_history(prompt_id: str):
    """Delete a history record and its associated files."""
    try:
        project_root = Path(current_app.root_path).resolve().parent
        prompt_dir = project_root / "static" / "generated" / prompt_id
        if prompt_dir.exists():
            shutil.rmtree(prompt_dir)

        history_manager.delete_record(prompt_id)
        return jsonify({"success": True})
    except Exception as exc:  # pragma: no cover - defensive
        current_app.logger.exception("删除历史记录失败: %s", exc)
        return jsonify({"success": False, "message": str(exc)}), 500


@bp.route("/switch_prompt", methods=["POST"])
def switch_prompt():
    """Switch to a prompt stored in history."""
    data = request.get_json(silent=True) or {}
    prompt_id = data.get("prompt_id")
    if not prompt_id:
        return jsonify({"success": False, "message": "缺少prompt_id参数"}), 400

    result = handle_history_switch(prompt_id)
    if not result:
        return jsonify({"success": False, "message": "历史记录不存在"}), 404

    record, images = result
    return jsonify({"success": True, "record": record, "images": images})


@bp.route("/add_more", methods=["POST"])
def add_more():
    """Increment the number of images to generate."""
    data = request.get_json(silent=True) or {}
    additional = int(data.get("count", 10))
    state = add_more_requests(additional)
    return jsonify({"success": True, "new_total": state["total_count"]})
