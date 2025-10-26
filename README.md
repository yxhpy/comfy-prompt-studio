# ComfyUI Web Application

AI 图像生成 Web 应用 - Ollama 提示词增强 + ComfyUI 工作流 + Flask WebSocket 实时更新

## 快速启动

### 前置要求
- ComfyUI 服务器运行在 `127.0.0.1:8188`
- Ollama 服务器运行在 `localhost:11434`
- Python 3.8+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
# 注意：.env 包含敏感信息（API密钥），不会被提交到 git
```

`.env` 文件示例（参考 `.env.example`）：

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=your-model-name
GEMINI_BASE_URL=https://your-api-endpoint.com/v1/
```

### 验证安装

```bash
python check_import.py
```

预期输出：
```
[OK] Python 路径配置成功
[OK] 成功导入 app 和 socketio
[OK] 成功导入 ComfyUI 集成模块
[OK] 成功导入提示词生成模块
[OK] 成功导入历史记录管理器
[SUCCESS] 所有核心模块导入成功！
```

### 启动应用

```bash
# 推荐：使用新的启动脚本
python run.py

# 或者使用传统方式（向后兼容）
python app.py
```

访问: http://localhost:5000

## 项目特性

- ✅ AI 智能提示词增强（支持 Ollama/Gemini）
- ✅ ComfyUI 工作流自动切换（普通/人脸替换）
- ✅ WebSocket 实时进度推送
- ✅ 历史记录管理与切换
- ✅ 工程化目录结构
- ✅ 单例模式服务层
- ✅ 配置分离管理

## 技术栈

- **后端**: Flask + Flask-SocketIO
- **AI 服务**: Ollama / Gemini
- **图像生成**: ComfyUI API
- **前端**: HTML + JavaScript（原生）

## 工程化结构

```
comfyui/
├── run.py                    # 应用启动入口（推荐）
├── src/                      # 源代码（模块化）
│   ├── services/            # 业务逻辑层
│   ├── routes/              # 路由模块
│   ├── workers/             # 后台任务
│   ├── models/              # 数据模型
│   └── utils/               # 工具函数
├── config/                   # 配置管理
│   ├── workflows/           # ComfyUI 工作流
│   └── settings.py          # 配置类
├── data/                     # 数据存储
│   ├── generated/           # 生成的图片（不提交）
│   ├── upload/              # 上传的图片（不提交）
│   └── history.db           # SQLite 历史记录（不提交）
├── tests/                    # 测试文件
├── .env                      # 环境变量（不提交，包含敏感信息）
└── .env.example             # 环境变量模板（可提交）
```

**注意**: 带有"（不提交）"标记的文件/目录已在 `.gitignore` 中忽略

## 开发状态

**已完成：**
- ✅ 工程化目录结构
- ✅ 配置管理模块
- ✅ 提示词服务重构（单例模式）
- ✅ 新的启动脚本

**进行中：**
- ⏳ 路由模块拆分
- ⏳ 工作线程模块
- ⏳ 历史记录模型重构
- ⏳ ComfyUI 服务层封装

## 许可证

MIT

## 更多信息

详细文档请查看 [CLAUDE.md](./CLAUDE.md)
