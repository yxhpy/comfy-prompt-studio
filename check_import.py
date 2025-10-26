"""
快速测试启动脚本
"""
import sys
import os
import io

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("[OK] Python 路径配置成功")

try:
    from app import app, socketio
    print("[OK] 成功导入 app 和 socketio")
except Exception as e:
    print(f"[FAIL] 导入失败: {e}")
    sys.exit(1)

try:
    from test import generate_image_with_comfyui
    print("[OK] 成功导入 ComfyUI 集成模块")
except Exception as e:
    print(f"[FAIL] 导入失败: {e}")
    sys.exit(1)

try:
    from generator_prompt import generate_prompt
    print("[OK] 成功导入提示词生成模块")
except Exception as e:
    print(f"[FAIL] 导入失败: {e}")
    sys.exit(1)

try:
    from history_manager import history_manager
    print("[OK] 成功导入历史记录管理器")
except Exception as e:
    print(f"[FAIL] 导入失败: {e}")
    sys.exit(1)

# 检查工作流文件
import os
workflows = [
    "config/workflows/flowv_normal.json",
    "config/workflows/flow_face.json",
]

print("\n检查工作流文件:")
for wf in workflows:
    if os.path.exists(wf):
        size = os.path.getsize(wf) / 1024
        print(f"  [OK] {wf} ({size:.1f} KB)")
    else:
        print(f"  [FAIL] {wf} (不存在)")

# 检查目录
print("\n检查必要的目录:")
dirs = ["static/generated", "upload", "data/generated", "data/upload", "templates"]
for d in dirs:
    if os.path.exists(d):
        print(f"  [OK] {d}/")
    else:
        print(f"  [WARN] {d}/ (不存在，将自动创建)")

print("\n" + "="*60)
print("[SUCCESS] 所有核心模块导入成功！")
print("="*60)
print("\n现在可以运行以下命令启动服务:")
print("  python run.py")
print("  或")
print("  python app.py")
