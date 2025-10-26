# CLAUDE.md
- 本文件为 CLAUDE 记忆文件，只记录最新的项目状态，保持文件内容的准确性，避免历史记录的干扰
- 使用中文
- 项目必须工程化，方便维护，永远保持文件位置正确
- 永远保证 CLAUDE.md 的内容是准确的
- 使用设计模式，保持代码结构清晰，方便维护
- 修复 bug 请先 debug 确认问题所在，再进行修复
- 新增功能先验证功能是否正常，再进行新增
- windows 下必须使用 utf-8 编码，避免中文乱码问题
```python
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```
- 根目录 AGENTS.md CLAUDE.md 禁止删除

AI 图像生成 Web 应用：Ollama 提示词增强 + ComfyUI 工作流 + Flask WebSocket 实时更新

## 架构设计

**数据流：** 用户输入 → Ollama（提示词增强）→ ComfyUI（图像生成）→ WebSocket → 前端展示

**核心模块：**
- `app.py` - Flask 主应用（向后兼容）
- `run.py` - 新的应用启动入口
- `src/services/prompt_service.py` - Ollama/Gemini 提示词服务（单例模式）
- `test.py` - ComfyUI API 集成，自动选择工作流
- `history_manager.py` - SQLite 历史记录管理服务

**工作流系统：**
- `config/workflows/flowv_normal.json` - 普通文生图工作流
- `config/workflows/flow_face.json` - 人脸替换工作流
- 自动选择逻辑：有 `image_path` 参数时使用人脸工作流

## 快速启动

**前置要求：** ComfyUI (127.0.0.1:8188) + Ollama (localhost:11434)

```bash
# 方式1：使用新的启动脚本（推荐）
python run.py

# 方式2：兼容旧方式
python app.py
```

访问: http://localhost:5000

## 目录结构（工程化）

```
comfyui/
├── run.py                      # 新：应用启动入口
├── app.py                      # 旧：Flask 主应用（向后兼容）
├── src/                        # 源代码目录
│   ├── services/              # 业务逻辑层
│   │   └── prompt_service.py # 提示词生成服务（单例）
│   ├── routes/                # 路由模块（待迁移）
│   ├── workers/               # 后台任务（待迁移）
│   ├── models/                # 数据模型（待迁移）
│   └── utils/                 # 工具函数
├── config/                     # 配置文件
│   ├── workflows/             # ComfyUI 工作流
│   │   ├── flowv_normal.json # 普通文生图
│   │   └── flow_face.json    # 人脸替换
│   └── settings.py           # 应用配置类
├── templates/                  # 前端模板
│   └── index.html
├── static/                     # 静态资源（旧）
│   └── generated/             # 向后兼容
├── data/                       # 数据目录（新）
│   ├── generated/             # 生成的图片
│   ├── upload/                # 上传的图片
│   └── history.db             # SQLite 历史记录数据库
├── tests/                      # 测试文件
│   ├── test_api.py
│   ├── test_worker.py
│   └── debug_test.py
├── history_manager.py          # 历史记录管理（旧位置，兼容）
├── test.py                     # ComfyUI 集成（旧位置，兼容）
├── generator_prompt.py         # 提示词生成（旧位置，兼容）
├── requirements.txt
├── .env
└── CLAUDE.md
```

**注意：** 当前处于渐进式重构阶段，部分模块保留在根目录以保持向后兼容。

## API 接口

- `POST /api/start` - 开始生成 (参数: `prompt`, `count`, `width`, `height`, `image_path`)
- `POST /api/stop` - 停止生成
- `GET /api/status` - 当前状态
- `POST /api/add_more` - 添加图片到队列 (参数: `count`)
- `GET /api/history` - 获取所有历史记录
- `POST /api/switch_prompt` - 加载历史记录 (参数: `prompt_id`)
- `DELETE /api/history/<prompt_id>` - 删除历史记录
- `POST /api/upload` - 上传参考图片
- `POST /api/delete_image` - 删除已生成图片 (参数: `filename`)

## WebSocket 事件

**服务端 → 客户端：**
- `new_image` - 新图片生成 (数据: filename, current, total)
- `progress` - 进度更新 (数据: current, total, status)
- `log` - 生成过程实时日志消息
- `generation_complete` - 所有图片完成 (数据: total)
- `error` - 发生错误 (数据: message)

## 关键技术要点

1. **工程化架构**: 采用分层设计，逐步从单文件重构为模块化结构
2. **向后兼容**: 保留旧代码路径，确保现有功能正常运行
3. **设计模式**: PromptService 使用单例模式，避免重复初始化
4. **配置管理**: config/settings.py 统一管理配置，支持开发/生产环境
5. **SocketIO 兼容性**: 不要使用 `broadcast=True` 参数（当前版本不支持）
6. **线程安全**: `current_generation` 字典被路由和工作线程同时访问
7. **图片存储结构**: `static/generated/[prompt_id]/[uuid].png`（旧）或 `data/generated/`（新）
8. **历史记录**: SQLite 数据库 (`data/history.db`)，两张表：`prompts`（提示词记录）和 `images`（图片记录）
9. **工作流节点**: 节点 "45"/"46" 用于正面/负面提示词，节点 "6" 用于图片尺寸
10. **随机种子**: 节点 "5"、"11"（普通工作流）和 "120"（人脸工作流）自动随机化
11. **人脸工作流**: 节点 "96:0" 的 `inputs.image` 字段需要设置为上传图片的绝对路径

## 开发计划

**已完成：**
- ✅ 创建工程化目录结构
- ✅ 配置管理模块 (config/settings.py)
- ✅ 提示词服务重构 (src/services/prompt_service.py)
- ✅ 新的启动脚本 (run.py)

**待完成：**
- ⏳ 路由模块拆分 (src/routes/)
- ⏳ 工作线程模块 (src/workers/)
- ⏳ 历史记录模型 (src/models/)
- ⏳ ComfyUI 服务层 (src/services/comfyui_service.py)
