"""
历史记录数据迁移脚本
将 JSON 格式的历史记录迁移到 SQLite 数据库
"""
import json
import shutil
from pathlib import Path

from src.core.history.manager import HistoryManager

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LEGACY_DIR = PROJECT_ROOT / "data" / "legacy"


def migrate_json_to_sqlite():
    """迁移 JSON 数据到 SQLite"""
    json_file = LEGACY_DIR / "history.json"
    backup_file = LEGACY_DIR / "history.json.backup"

    if not json_file.exists():
        print(f"⚠️ 未找到 {json_file}，跳过迁移")
        return

    print("=" * 60)
    print("开始迁移历史记录数据：JSON → SQLite")
    print("=" * 60)

    LEGACY_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(json_file, backup_file)
    print(f"✅ 已备份原始文件到: {backup_file}\n")

    try:
        with open(json_file, "r", encoding="utf-8") as f:
            records = json.load(f)
        print(f"📖 读取到 {len(records)} 条历史记录\n")
    except Exception as e:
        print(f"❌ 读取 JSON 文件失败: {e}")
        return

    manager = HistoryManager()
    success_count = 0
    error_count = 0

    for idx, record in enumerate(records, 1):
        try:
            prompt_id = record.get("id")
            prompt = record.get("prompt", "")
            positive_prompt = record.get("positive_prompt", "")
            negative_prompt = record.get("negative_prompt", "")
            width = record.get("width", 800)
            height = record.get("height", 1200)

            print(f"[{idx}/{len(records)}] 迁移记录: {prompt_id}")
            print(f"  提示词: {prompt[:50]}...")

            manager.add_record(
                prompt=prompt,
                positive_prompt=positive_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
            )

            images = record.get("images", [])
            for img in images:
                manager.update_images(prompt_id, img)

            print(f"  ✅ 成功迁移 {len(images)} 张图片\n")
            success_count += 1
        except Exception as e:
            print(f"  ❌ 迁移失败: {e}\n")
            error_count += 1

    print("=" * 60)
    print("迁移完成统计")
    print("=" * 60)
    print(f"✅ 成功: {success_count} 条")
    print(f"❌ 失败: {error_count} 条")

    stats = manager.get_statistics()
    print(f"\nSQLite 数据库统计:")
    print(f"  提示词记录: {stats['total_prompts']} 条")
    print(f"  图片记录: {stats['total_images']} 张")

    print("\n" + "=" * 60)
    print(f"⚠️ 原始 JSON 文件已备份到: {backup_file}")
    print(f"如果迁移成功，可以手动删除 {json_file}")
    print("=" * 60)


if __name__ == "__main__":
    migrate_json_to_sqlite()
