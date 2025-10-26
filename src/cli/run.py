#!/usr/bin/env python
"""
Console entry that mimics the original run.py helper.
"""
import os
import sys
from pathlib import Path

# Ensure project root on path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .serve import main as run_server  # noqa: E402


def banner() -> str:
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    return f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║   ComfyUI Web Application                                 ║
    ║   AI 图像生成服务已启动                                    ║
    ╠═══════════════════════════════════════════════════════════╣
    ║   访问地址: http://{host}:{port:<40} ║
    ║   调试模式: {'开启' if debug else '关闭':<45} ║
    ║   工作流目录: config/workflows/                           ║
    ║   数据目录: data/ (新) / static/generated/ (旧)          ║
    ╚═══════════════════════════════════════════════════════════╝
    """


def main() -> None:
    print(banner(), flush=True)
    run_server()


if __name__ == "__main__":
    main()
