# CLAUDE.md
- 本文件为 CLAUDE 记忆文件，只记录最新的项目状态，保持文件内容的准确性，避免历史记录的干扰
- 使用中文
- 项目必须工程化，方便维护，永远保持文件位置正确
- 永远保证 CLAUDE.md, README.md, AGENTS.md 的内容是准确的,文档和代码一致
- 使用设计模式，保持代码结构清晰，方便维护
- 修复 bug 请先 debug 确认问题所在，再进行修复
- 新增功能先验证功能是否正常，再进行新增
- windows 下必须使用 utf-8 编码，避免中文乱码问题
```python
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```
- 根目录 CLAUDE.md, README.md, AGENTS.md 禁止删除


AI 图像生成 Web 应用：Ollama 提示词增强 + ComfyUI 工作流 + Flask WebSocket 实时更新

## 架构设计

**数据流：** 用户输入 → Ollama（提示词增强）→ ComfyUI（图像生成）→ WebSocket → 前端展示

**核心模块：**
- `src/cli/run.py` - 应用启动入口
- `src/cli/serve.py` - Flask 服务器
- `src/app/__init__.py` - Flask 应用工厂
- `src/core/prompt/` - 提示词生成服务（Ollama/Gemini）
- `src/core/comfyui/` - ComfyUI API 集成，自动选择工作流
- `src/core/history/` - SQLite 历史记录管理服务

**工作流系统：**
- `config/workflows/flowv_normal.json` - 普通文生图工作流
- `config/workflows/flow_face.json` - 人脸替换工作流
- 自动选择逻辑：有 `image_path` 参数时使用人脸工作流

## 快速启动

**前置要求：** ComfyUI (127.0.0.1:8188) + Ollama (localhost:11434)

**环境配置：**

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑 .env 文件，填入你的 API 密钥等敏感信息
# 注意：.env 文件包含敏感信息，已在 .gitignore 中忽略

# 3. 安装依赖
pip install -r requirements.txt
```

**启动应用：**

```bash
python -m src.cli.run
```

访问: http://localhost:5000

## 目录结构（工程化）

```
comfyui/
├── src/                        # 源代码目录
│   ├── app/                    # Flask 应用模块
│   │   ├── __init__.py        # 应用工厂
│   │   ├── config.py          # 应用配置
│   │   ├── extensions.py      # Flask 扩展
│   │   ├── routes/            # 路由蓝图
│   │   ├── services/          # 业务服务
│   │   └── events/            # WebSocket 事件
│   ├── cli/                    # 命令行工具
│   │   ├── run.py             # 应用启动入口
│   │   ├── serve.py           # Flask 服务器
│   │   ├── check_import.py    # 导入验证工具
│   │   └── migrate_to_sqlite.py  # 数据迁移工具
│   ├── core/                   # 核心业务逻辑
│   │   ├── comfyui/           # ComfyUI 集成
│   │   ├── history/           # 历史记录管理
│   │   └── prompt/            # 提示词生成
│   ├── legacy/                 # 向后兼容代码
│   ├── models/                 # 数据模型
│   ├── routes/                 # 路由模块（待迁移）
│   ├── services/               # 业务服务（待迁移）
│   ├── utils/                  # 工具函数
│   └── workers/                # 后台任务
├── config/                     # 配置文件
│   ├── workflows/             # ComfyUI 工作流
│   │   ├── flowv_normal.json # 普通文生图
│   │   └── flow_face.json    # 人脸替换
│   └── settings.py           # 全局配置类
├── templates/                  # Jinja2 模板
│   ├── layouts/               # 布局模板
│   └── partials/              # 组件模板
├── static/                     # 静态资源
│   ├── css/                   # 样式文件
│   ├── js/                    # JavaScript 文件
│   └── generated/             # 生成图片（旧，向后兼容）
├── data/                       # 数据目录
│   ├── generated/             # 生成的图片（不提交）
│   ├── upload/                # 上传的图片（不提交）
│   └── history.db             # SQLite 历史记录（不提交）
├── tests/                      # 测试文件
├── .env                        # 环境变量（不提交）
├── .env.example               # 环境变量模板
├── requirements.txt
├── CLAUDE.md                   # 项目技术文档
├── README.md                   # 快速开始指南
└── AGENTS.md                   # AI 代理配置
```

**注意：**
- 当前处于渐进式重构阶段，部分模块保留以保持向后兼容
- 带有"（不提交）"标记的文件已在 `.gitignore` 中忽略

## API 接口

**图像生成:**
- `POST /api/start` - 开始生成 (参数: `prompt`, `count`, `width`, `height`, `image_path`)
- `POST /api/stop` - 停止生成
- `GET /api/status` - 当前状态
- `POST /api/add_more` - 添加图片到队列 (参数: `count`)
- `POST /api/delete_image` - 删除已生成图片 (参数: `filename`)

**文件上传:**
- `POST /api/upload` - 上传参考图片

**历史记录:**
- `GET /api/history` - 获取所有历史记录
- `GET /api/history/<prompt_id>` - 获取单个历史记录
- `POST /api/switch_prompt` - 加载历史记录 (参数: `prompt_id`)
- `DELETE /api/history/<prompt_id>` - 删除历史记录

**提示词:**
- `GET /api/prompts` - 获取预设提示词（随机返回一个）

**开发调试:**
- `POST /api/test_emit` - 测试 WebSocket 消息发送

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

## 安全配置

**敏感信息保护：**

1. **环境变量**: 使用 `.env` 文件存储 API 密钥等敏感信息
   - `.env` 已在 `.gitignore` 中忽略，不会提交到版本控制
   - 使用 `.env.example` 作为模板，不包含真实密钥
   - 首次部署时复制 `.env.example` 为 `.env` 并填入真实配置

2. **数据库文件**: `data/history.db` 已被 `.gitignore` 忽略
   - 包含用户生成的历史记录，属于个人数据
   - 不应提交到公共仓库

3. **生成文件**: `data/generated/` 和 `data/upload/` 目录被忽略
   - 包含用户生成和上传的图片
   - 避免仓库体积过大

4. **最佳实践**:
   - 定期检查 `.gitignore` 确保敏感文件未被追踪
   - 使用 `git status` 查看暂存区，避免误提交敏感信息
   - API 密钥应有访问限制和定期轮换机制

## 开发计划

**已完成：**
- ✅ 创建工程化目录结构
- ✅ 配置管理模块 (config/settings.py)
- ✅ 提示词服务重构 (src/services/prompt_service.py)
- ✅ 应用启动脚本 (src/cli/run.py)

**待完成：**
- ⏳ 路由模块拆分 (src/routes/)
- ⏳ 工作线程模块 (src/workers/)
- ⏳ 历史记录模型 (src/models/)
- ⏳ ComfyUI 服务层 (src/services/comfyui_service.py)
