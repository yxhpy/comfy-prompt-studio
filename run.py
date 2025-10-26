#!/usr/bin/env python
"""
ComfyUI Web Application 启动入口
"""
import os
import sys

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 使用现有的 app.py（向后兼容）
from app import app, socketio

if __name__ == '__main__':
    # 从环境变量获取配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║   ComfyUI Web Application                                 ║
    ║   AI 图像生成服务已启动                                    ║
    ╠═══════════════════════════════════════════════════════════╣
    ║   访问地址: http://{host}:{port:<40} ║
    ║   调试模式: {'开启' if debug else '关闭':<45} ║
    ║   工作流目录: config/workflows/                           ║
    ║   数据目录: data/ (新) / static/generated/ (旧)          ║
    ╚═══════════════════════════════════════════════════════════╝
    """, flush=True)

    # 确保必要的目录存在
    os.makedirs('static/generated', exist_ok=True)
    os.makedirs('data/generated', exist_ok=True)
    os.makedirs('data/upload', exist_ok=True)
    os.makedirs('upload', exist_ok=True)

    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        allow_unsafe_werkzeug=True
    )
