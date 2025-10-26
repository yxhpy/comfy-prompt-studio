"""
Legacy import shim for history_manager_sqlite.

External scripts that still import ``history_manager_sqlite`` will receive
the updated implementation from ``src.core.history.manager``.
"""
from src.core.history.manager import (
    HistoryManager,
    generate_prompt_id,
    history_manager,
)

__all__ = ["HistoryManager", "history_manager", "generate_prompt_id"]
