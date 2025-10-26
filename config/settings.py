"""
应用配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """基础配置"""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # 目录配置
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'upload')
    GENERATED_FOLDER = os.path.join(BASE_DIR, 'data', 'generated')
    HISTORY_FILE = os.path.join(BASE_DIR, 'data', 'history.json')
    WORKFLOW_DIR = os.path.join(BASE_DIR, 'config', 'workflows')

    # 工作流配置
    WORKFLOW_NORMAL = os.path.join(WORKFLOW_DIR, 'flowv_normal.json')
    WORKFLOW_FACE = os.path.join(WORKFLOW_DIR, 'flow_face.json')

    # AI 配置
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'ollama')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'huihui_ai/qwen3-abliterated:30b')
    OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')

    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
    GEMINI_BASE_URL = os.getenv('GEMINI_BASE_URL', 'https://api.laozhang.ai/v1/')

    # ComfyUI 配置
    COMFYUI_SERVER = os.getenv('COMFYUI_SERVER', '127.0.0.1:8188')

    # 文件上传配置
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 确保必要的目录存在
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.GENERATED_FOLDER, exist_ok=True)
        os.makedirs(os.path.dirname(Config.HISTORY_FILE), exist_ok=True)


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
