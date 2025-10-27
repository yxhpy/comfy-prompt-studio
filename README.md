<div align="center">

# ComfyUI Prompt Studio

**AI图像生成Web应用 - Ollama/Gemini提示词增强 + ComfyUI工作流 + Flask WebSocket实时推送**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![GitHub issues](https://img.shields.io/github/issues/yxhpy/comfy-prompt-studio)](https://github.com/yxhpy/comfy-prompt-studio/issues)
[![GitHub stars](https://img.shields.io/github/stars/yxhpy/comfy-prompt-studio)](https://github.com/yxhpy/comfy-prompt-studio/stargazers)

[English](README_EN.md) | 简体中文

</div>

---

## 📖 项目简介

**ComfyUI Prompt Studio** 是一个功能强大的 AI 图像生成 Web 应用，通过整合多种先进技术，为用户提供流畅的图像创作体验。

### 🎯 为什么选择这个项目？

- **智能提示词增强**：将简单的描述转换为专业的 Stable Diffusion 提示词
- **双AI引擎支持**：灵活切换 Ollama（本地）和 Gemini（云端）
- **自动工作流切换**：根据需求自动选择普通生图或人脸替换工作流
- **实时进度追踪**：WebSocket 实时推送生成进度和日志
- **历史记录管理**：SQLite 数据库存储，支持快速切换和管理
- **工程化架构**：模块化设计，易于维护和扩展

### 🎬 演示

> 📸 **截图正在准备中...**
> 你可以先克隆项目本地运行体验完整功能！

<!-- 未来可添加截图
![主界面](docs/images/main-ui.png)
![生成过程](docs/images/generation.gif)
-->

### 🆚 与其他方案对比

| 特性 | ComfyUI原生 | 本项目 | WebUI |
|-----|------------|--------|-------|
| 提示词增强 | ❌ | ✅ AI自动增强 | ⚠️ 基础增强 |
| 实时日志 | ❌ | ✅ WebSocket推送 | ⚠️ 页面刷新 |
| 历史记录 | ❌ | ✅ SQLite管理 | ✅ |
| 工作流切换 | 手动 | ✅ 自动识别 | 手动 |
| 易用性 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

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
python -m src.cli.check_import
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
python -m src.cli.run
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
├── src/                      # 源代码（模块化）
│   ├── app/                  # Flask 应用模块
│   │   ├── __init__.py      # 应用工厂
│   │   ├── config.py        # 应用配置
│   │   ├── extensions.py    # Flask 扩展
│   │   ├── routes/          # 路由蓝图
│   │   ├── services/        # 业务服务
│   │   └── events/          # WebSocket 事件
│   ├── cli/                  # 命令行工具
│   │   ├── run.py           # 应用启动入口
│   │   ├── serve.py         # Flask 服务器
│   │   ├── check_import.py  # 导入验证工具
│   │   └── migrate_to_sqlite.py  # 数据迁移工具
│   ├── core/                 # 核心业务逻辑
│   │   ├── comfyui/         # ComfyUI 集成
│   │   ├── history/         # 历史记录管理
│   │   └── prompt/          # 提示词生成
│   ├── legacy/               # 向后兼容代码
│   ├── models/               # 数据模型
│   ├── routes/               # 路由模块（待迁移）
│   ├── services/             # 业务服务（待迁移）
│   ├── utils/                # 工具函数
│   └── workers/              # 后台任务
├── config/                   # 配置管理
│   ├── workflows/           # ComfyUI 工作流
│   │   ├── flowv_normal.json  # 普通文生图
│   │   └── flow_face.json     # 人脸替换
│   └── settings.py          # 全局配置类
├── templates/                # Jinja2 模板
│   ├── layouts/             # 布局模板
│   └── partials/            # 组件模板
├── static/                   # 静态资源
│   ├── css/                 # 样式文件
│   ├── js/                  # JavaScript 文件
│   └── generated/           # 生成图片（旧，向后兼容）
├── data/                     # 数据存储
│   ├── generated/           # 生成的图片（不提交）
│   ├── upload/              # 上传的图片（不提交）
│   └── history.db           # SQLite 历史记录（不提交）
├── tests/                    # 测试文件
├── .env                      # 环境变量（不提交，包含敏感信息）
├── .env.example             # 环境变量模板（可提交）
└── requirements.txt         # Python 依赖
```

**注意**:
- 带有"（不提交）"标记的文件/目录已在 `.gitignore` 中忽略
- 当前处于渐进式重构阶段，部分模块保留以保持向后兼容

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

本项目采用 [MIT 许可证](LICENSE)。

## 🤝 贡献

欢迎贡献代码、报告问题或提出功能建议！

详情请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## ❓ 常见问题

<details>
<summary><b>Q: 为什么生成图片失败？</b></summary>

检查以下几点：
1. ComfyUI 服务是否正常运行在 `127.0.0.1:8188`
2. Ollama/Gemini 服务是否可访问
3. 查看控制台日志获取详细错误信息
4. 检查 `.env` 配置是否正确
</details>

<details>
<summary><b>Q: 如何切换 Ollama 和 Gemini？</b></summary>

编辑 `.env` 文件，修改 `AI_PROVIDER` 参数：
```env
# 使用 Ollama（本地）
AI_PROVIDER=ollama

# 使用 Gemini（云端）
AI_PROVIDER=gemini
```
</details>

<details>
<summary><b>Q: 人脸替换功能如何使用？</b></summary>

1. 在界面上传参考图片（包含人脸）
2. 输入提示词
3. 系统会自动切换到人脸替换工作流
4. 生成的图片会替换为参考图片中的人脸
</details>

<details>
<summary><b>Q: 历史记录保存在哪里？</b></summary>

历史记录保存在 `data/history.db` SQLite 数据库中，包含提示词和生成的图片路径。
</details>

<details>
<summary><b>Q: 可以自定义 ComfyUI 工作流吗？</b></summary>

可以！修改 `config/workflows/` 目录下的 JSON 文件：
- `flowv_normal.json` - 普通文生图工作流
- `flow_face.json` - 人脸替换工作流
</details>

## 📚 更多信息

- [CLAUDE.md](CLAUDE.md) - 完整技术文档
- [AGENTS.md](AGENTS.md) - AI 代理配置说明
- [CHANGELOG.md](CHANGELOG.md) - 版本更新历史

## 🙏 致谢

感谢以下开源项目：
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - 强大的 Stable Diffusion GUI
- [Flask](https://flask.palletsprojects.com/) - Python Web 框架
- [Ollama](https://ollama.ai/) - 本地 LLM 运行环境
- [Gemini](https://ai.google.dev/) - Google AI 服务

## 📬 联系方式

- 提交 Issue：[GitHub Issues](https://github.com/yxhpy/comfy-prompt-studio/issues)
- 项目讨论：[GitHub Discussions](https://github.com/yxhpy/comfy-prompt-studio/discussions)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！ ⭐**

Made with ❤️ by [yxhpy](https://github.com/yxhpy)

</div>
