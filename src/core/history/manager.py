"""
SQLite 版本的历史记录管理器
使用 SQLite 数据库替代 JSON 文件存储
"""
import sqlite3
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DB_FILE = os.path.join(PROJECT_ROOT, 'data/history.db')

def generate_prompt_id(prompt: str) -> str:
    """根据提示词生成唯一ID"""
    return hashlib.md5(prompt.encode('utf-8')).hexdigest()[:12]


class HistoryManager:
    """历史记录管理器 - SQLite 版本"""

    def __init__(self, db_path: str = DB_FILE):
        if not os.path.isabs(db_path):
            db_path = os.path.join(PROJECT_ROOT, db_path)
        self.db_path = db_path

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # 初始化数据库
        self._init_database()

    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 允许通过列名访问
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 创建提示词记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prompts (
                    id TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    positive_prompt TEXT,
                    negative_prompt TEXT,
                    width INTEGER DEFAULT 800,
                    height INTEGER DEFAULT 1200,
                    created_at TEXT NOT NULL,
                    last_used TEXT NOT NULL,
                    image_count INTEGER DEFAULT 0
                )
            ''')

            # 创建图片表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE
                )
            ''')

            # 创建索引以提高查询性能
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_prompts_last_used
                ON prompts(last_used DESC)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_images_prompt_id
                ON images(prompt_id)
            ''')

    def add_record(self, prompt: str, positive_prompt: str, negative_prompt: str,
                   width: int, height: int) -> str:
        """添加新记录或更新已存在的记录"""
        prompt_id = generate_prompt_id(prompt)
        now = datetime.now().isoformat()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 检查是否已存在
            cursor.execute('SELECT id FROM prompts WHERE id = ?', (prompt_id,))
            existing = cursor.fetchone()

            if existing:
                # 更新最后使用时间
                cursor.execute('''
                    UPDATE prompts
                    SET last_used = ?
                    WHERE id = ?
                ''', (now, prompt_id))
            else:
                # 创建新记录
                cursor.execute('''
                    INSERT INTO prompts
                    (id, prompt, positive_prompt, negative_prompt, width, height, created_at, last_used, image_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                ''', (prompt_id, prompt, positive_prompt, negative_prompt, width, height, now, now))

        return prompt_id

    def get_record_by_id(self, prompt_id: str) -> Optional[Dict]:
        """根据ID获取记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM prompts WHERE id = ?', (prompt_id,))
            row = cursor.fetchone()

            if row:
                record = dict(row)
                record['images'] = self.get_images_by_prompt_id(prompt_id)
                return record
            return None

    def update_images(self, prompt_id: str, image_filename: str):
        """添加图片到记录"""
        now = datetime.now().isoformat()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 添加图片记录
            cursor.execute('''
                INSERT INTO images (prompt_id, filename, created_at)
                VALUES (?, ?, ?)
            ''', (prompt_id, image_filename, now))

            # 更新图片计数和最后使用时间
            cursor.execute('''
                UPDATE prompts
                SET image_count = (
                    SELECT COUNT(*) FROM images WHERE prompt_id = ?
                ),
                last_used = ?
                WHERE id = ?
            ''', (prompt_id, now, prompt_id))

    def remove_image(self, prompt_id: str, image_filename: str):
        """从记录中移除图片"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 删除图片记录
            cursor.execute('''
                DELETE FROM images
                WHERE prompt_id = ? AND filename = ?
            ''', (prompt_id, image_filename))

            # 更新图片计数
            cursor.execute('''
                UPDATE prompts
                SET image_count = (
                    SELECT COUNT(*) FROM images WHERE prompt_id = ?
                )
                WHERE id = ?
            ''', (prompt_id, prompt_id))

    def get_images_by_prompt_id(self, prompt_id: str) -> List[str]:
        """获取指定提示词的所有图片"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT filename FROM images
                WHERE prompt_id = ?
                ORDER BY created_at ASC
            ''', (prompt_id,))

            return [row['filename'] for row in cursor.fetchall()]

    def get_all_records(self) -> List[Dict]:
        """获取所有历史记录，按最后使用时间排序"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM prompts
                ORDER BY last_used DESC
            ''')

            records = []
            for row in cursor.fetchall():
                record = dict(row)
                # 获取图片列表
                record['images'] = self.get_images_by_prompt_id(record['id'])
                records.append(record)

            return records

    def delete_record(self, prompt_id: str):
        """删除记录（级联删除关联的图片记录）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 先删除图片记录（虽然有外键级联，但显式删除更清晰）
            cursor.execute('DELETE FROM images WHERE prompt_id = ?', (prompt_id,))

            # 删除提示词记录
            cursor.execute('DELETE FROM prompts WHERE id = ?', (prompt_id,))

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) as total_prompts FROM prompts')
            total_prompts = cursor.fetchone()['total_prompts']

            cursor.execute('SELECT COUNT(*) as total_images FROM images')
            total_images = cursor.fetchone()['total_images']

            cursor.execute('SELECT SUM(image_count) as sum_images FROM prompts')
            sum_images = cursor.fetchone()['sum_images'] or 0

            return {
                'total_prompts': total_prompts,
                'total_images': total_images,
                'sum_images': sum_images
            }


# 全局实例
history_manager = HistoryManager()
