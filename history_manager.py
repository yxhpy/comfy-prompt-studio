import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional

HISTORY_FILE = 'history.json'

def generate_prompt_id(prompt: str) -> str:
    """根据提示词生成唯一ID"""
    return hashlib.md5(prompt.encode('utf-8')).hexdigest()[:12]

class HistoryManager:
    def __init__(self):
        self.history_file = HISTORY_FILE
        self.history = self.load_history()

    def load_history(self) -> List[Dict]:
        """加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载历史记录失败: {e}", flush=True)
                return []
        return []

    def save_history(self):
        """保存历史记录到文件"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}", flush=True)

    def add_record(self, prompt: str, positive_prompt: str, negative_prompt: str,
                   width: int, height: int) -> str:
        """添加新记录"""
        prompt_id = generate_prompt_id(prompt)

        # 检查是否已存在
        existing = self.get_record_by_id(prompt_id)
        if existing:
            # 更新最后使用时间
            existing['last_used'] = datetime.now().isoformat()
            self.save_history()
            return prompt_id

        # 创建新记录
        record = {
            'id': prompt_id,
            'prompt': prompt,
            'positive_prompt': positive_prompt,
            'negative_prompt': negative_prompt,
            'width': width,
            'height': height,
            'created_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'image_count': 0,
            'images': []
        }

        self.history.insert(0, record)  # 插入到开头
        self.save_history()
        return prompt_id

    def get_record_by_id(self, prompt_id: str) -> Optional[Dict]:
        """根据ID获取记录"""
        for record in self.history:
            if record['id'] == prompt_id:
                return record
        return None

    def update_images(self, prompt_id: str, image_filename: str):
        """更新记录的图片列表"""
        record = self.get_record_by_id(prompt_id)
        if record:
            if 'images' not in record:
                record['images'] = []
            record['images'].append(image_filename)
            record['image_count'] = len(record['images'])
            record['last_used'] = datetime.now().isoformat()
            self.save_history()

    def remove_image(self, prompt_id: str, image_filename: str):
        """从记录中移除图片"""
        record = self.get_record_by_id(prompt_id)
        if record and 'images' in record:
            if image_filename in record['images']:
                record['images'].remove(image_filename)
                record['image_count'] = len(record['images'])
                self.save_history()

    def get_all_records(self) -> List[Dict]:
        """获取所有历史记录，按最后使用时间排序"""
        return sorted(self.history, key=lambda x: x.get('last_used', ''), reverse=True)

    def delete_record(self, prompt_id: str):
        """删除记录"""
        self.history = [r for r in self.history if r['id'] != prompt_id]
        self.save_history()

# 全局实例
history_manager = HistoryManager()
