"""
ComfyUI Web Application
AI 图像生成 Web 应用
"""

from importlib import import_module
import sys

__version__ = '1.0.0'

_COMPAT_MODULES = {
    "history_manager_sqlite": "src.legacy.history_manager_sqlite",
    "app": "src.cli.serve",
    "run": "src.cli.run",
    "check_import": "src.cli.check_import",
    "migrate_to_sqlite": "src.cli.migrate_to_sqlite",
}

for alias, target in _COMPAT_MODULES.items():
    try:
        module = import_module(target)
        sys.modules.setdefault(alias, module)
    except Exception:  # pragma: no cover - best effort compatibility
        pass

__all__ = ["__version__"]
