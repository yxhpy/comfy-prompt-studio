"""
Quick smoke-test to ensure core modules import correctly.
"""
import io
import os
import sys
from pathlib import Path

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print("[OK] Python 路径配置成功")

try:
    from src.cli.serve import app, socketio  # noqa: F401
    print("[OK] 成功导入 app 和 socketio")
except Exception as e:
    print(f"[FAIL] 导入失败: {e}")
    sys.exit(1)

try:
    from src.core.comfyui.client import generate_image_with_comfyui  # noqa: F401
    print("[OK] 成功导入 ComfyUI 集成模块")
except Exception as e:
    print(f"[FAIL] 导入失败: {e}")
    sys.exit(1)

try:
    from src.core.prompt.generator import generate_prompt  # noqa: F401
    print("[OK] 成功导入提示词生成模块")
except Exception as e:
    print(f"[FAIL] 导入失败: {e}")
    sys.exit(1)

try:
    from src.core.history.manager import history_manager  # noqa: F401
    print("[OK] 成功导入历史记录管理器")
except Exception as e:
    print(f"[FAIL] 导入失败: {e}")
    sys.exit(1)

workflows = [
    PROJECT_ROOT / "config" / "workflows" / "flowv_normal.json",
    PROJECT_ROOT / "config" / "workflows" / "flow_face.json",
]

print("\n检查工作流文件:")
for wf in workflows:
    if wf.exists():
        size = wf.stat().st_size / 1024
        print(f"  [OK] {wf} ({size:.1f} KB)")
    else:
        print(f"  [FAIL] {wf} (不存在)")

print("\n检查必要的目录:")
dirs = [
    PROJECT_ROOT / "static" / "generated",
    PROJECT_ROOT / "upload",
    PROJECT_ROOT / "data" / "generated",
    PROJECT_ROOT / "data" / "upload",
    PROJECT_ROOT / "templates",
]
for d in dirs:
    if d.exists():
        print(f"  [OK] {d}/")
    else:
        print(f"  [WARN] {d}/ (不存在，将自动创建)")

print("\n" + "=" * 60)
print("[SUCCESS] 所有核心模块导入成功！")
print("=" * 60)
print("\n现在可以运行以下命令启动服务:")
print("  python -m src.cli.run")
print("  或")
print("  python -m src.cli.serve")
