# 贡献指南

感谢你考虑为 ComfyUI Prompt Studio 做出贡献！本文档将指导你如何参与项目开发。

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境搭建](#开发环境搭建)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request 流程](#pull-request-流程)
- [报告问题](#报告问题)

## 🤝 行为准则

参与本项目即表示你同意遵守以下准则：

- 尊重所有贡献者和用户
- 接受建设性的批评
- 关注社区最佳利益
- 对新手友好，耐心解答问题

## 💡 如何贡献

你可以通过以下方式贡献：

### 🐛 报告 Bug
1. 检查 [Issues](https://github.com/yxhpy/comfy-prompt-studio/issues) 确认问题未被报告
2. 创建新 Issue，使用 Bug 报告模板
3. 提供详细的复现步骤和环境信息

### ✨ 功能建议
1. 在 Issues 中描述你的想法
2. 说明功能的使用场景和价值
3. 等待维护者反馈后再开始实现

### 📝 改进文档
- 修复错别字、语法错误
- 补充缺失的文档内容
- 翻译文档（如英文版）
- 添加使用示例和教程

### 💻 提交代码
- 修复 Bug
- 实现新功能
- 性能优化
- 代码重构

## 🛠️ 开发环境搭建

### 1. Fork 并克隆仓库

```bash
# Fork 项目到你的 GitHub 账号
# 然后克隆到本地
git clone https://github.com/YOUR_USERNAME/comfy-prompt-studio.git
cd comfy-prompt-studio

# 添加上游仓库
git remote add upstream https://github.com/yxhpy/comfy-prompt-studio.git
```

### 2. 创建开发分支

```bash
# 从 main 分支创建新分支
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

### 3. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（如有）
# pip install -r requirements-dev.txt
```

### 4. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
```

### 5. 启动服务

```bash
# 确保 ComfyUI 和 Ollama/Gemini 服务已启动

# 验证导入
python -m src.cli.check_import

# 启动应用
python -m src.cli.run
```

## 📏 代码规范

### Python 代码风格

遵循 [PEP 8](https://pep8.org/) 风格指南：

```python
# ✅ 好的示例
def generate_prompt(user_input: str) -> str:
    """
    生成增强的提示词。

    Args:
        user_input: 用户输入的简单描述

    Returns:
        增强后的提示词
    """
    if not user_input:
        raise ValueError("输入不能为空")

    return enhanced_prompt

# ❌ 不好的示例
def generatePrompt(userInput):  # 使用驼峰命名
    if userInput=="":  # 缺少空格
        return None  # 缺少文档字符串
    return result
```

### 关键规范

1. **命名规范**
   - 函数和变量：`snake_case`
   - 类名：`PascalCase`
   - 常量：`UPPER_CASE`

2. **文档字符串**
   - 所有公共函数/类必须有 docstring
   - 使用 Google 风格或 NumPy 风格

3. **导入顺序**
   ```python
   # 标准库
   import os
   import sys

   # 第三方库
   from flask import Flask
   import requests

   # 本地模块
   from src.core.prompt import generator
   ```

4. **类型提示**
   ```python
   from typing import List, Dict, Optional

   def process_images(
       image_list: List[str],
       config: Dict[str, any],
       timeout: Optional[int] = None
   ) -> bool:
       pass
   ```

### 文件编码

- **Windows 系统**：确保使用 UTF-8 编码
  ```python
  import sys
  import io

  if sys.platform == 'win32':
      sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
  ```

## 📝 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型 (type)

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档变更
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具链变更

### 示例

```bash
# 新功能
git commit -m "feat(prompt): 添加 Claude 提示词增强支持"

# Bug 修复
git commit -m "fix(history): 修复删除记录时的并发问题"

# 文档更新
git commit -m "docs(readme): 更新安装步骤说明"

# 重构
git commit -m "refactor(core): 重构 ComfyUI 客户端连接逻辑"
```

## 🔄 Pull Request 流程

### 1. 保持分支最新

```bash
# 拉取上游更新
git fetch upstream
git rebase upstream/main

# 解决冲突（如有）
git add .
git rebase --continue
```

### 2. 提交变更

```bash
# 添加变更
git add .

# 提交（使用规范的提交信息）
git commit -m "feat: your feature description"

# 推送到你的 fork
git push origin feature/your-feature-name
```

### 3. 创建 Pull Request

1. 访问你的 Fork 页面
2. 点击 "New Pull Request"
3. 填写 PR 描述：
   - **标题**：简洁描述变更
   - **描述**：
     - 变更的内容和原因
     - 相关的 Issue 编号
     - 测试方法
     - 截图（如适用）

### PR 模板示例

```markdown
## 变更类型
- [ ] Bug 修复
- [x] 新功能
- [ ] 文档更新
- [ ] 重构

## 变更描述
添加了 Claude AI 作为新的提示词增强提供商。

## 相关 Issue
Closes #123

## 测试方法
1. 配置 CLAUDE_API_KEY
2. 设置 AI_PROVIDER=claude
3. 运行应用，输入提示词
4. 验证生成结果

## 截图
（如适用）

## Checklist
- [x] 代码遵循项目规范
- [x] 添加了必要的测试
- [x] 更新了相关文档
- [x] 提交信息符合规范
```

### 4. 代码审查

- 维护者会审查你的代码
- 可能会要求修改
- 请耐心等待反馈并及时响应

### 5. 合并

- 审查通过后，维护者会合并你的 PR
- 你的名字会出现在贡献者列表中！

## 🐞 报告问题

### Bug 报告清单

在报告 Bug 前，请确保：

- [ ] 已搜索现有 Issues
- [ ] 使用最新版本
- [ ] 问题可重现

### Bug 报告模板

```markdown
**描述**
清晰简洁地描述 Bug。

**复现步骤**
1. 打开应用
2. 点击 '...'
3. 输入 '...'
4. 看到错误

**预期行为**
应该发生什么。

**实际行为**
实际发生了什么。

**环境信息**
- OS: [e.g. Windows 11]
- Python 版本: [e.g. 3.10.5]
- 项目版本: [e.g. 1.0.0]
- ComfyUI 版本: [e.g. latest]

**日志/截图**
如适用，添加日志或截图。

**额外信息**
其他相关信息。
```

## 🎯 开发技巧

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_prompt.py

# 查看覆盖率
pytest --cov=src
```

### 代码检查

```bash
# 格式检查
flake8 src/

# 类型检查
mypy src/

# 自动格式化
black src/
```

### 调试技巧

1. 使用 Python 调试器
   ```python
   import pdb; pdb.set_trace()
   ```

2. 查看日志
   ```bash
   tail -f app.log
   ```

3. 使用 VS Code 调试配置

## ❓ 获得帮助

如有疑问：

- 📖 查看 [CLAUDE.md](CLAUDE.md) 技术文档
- 💬 在 [Discussions](https://github.com/yxhpy/comfy-prompt-studio/discussions) 提问
- 🐛 在 [Issues](https://github.com/yxhpy/comfy-prompt-studio/issues) 报告问题

## 🙏 致谢

感谢所有为本项目做出贡献的开发者！

你的贡献让这个项目变得更好！✨

---

<div align="center">

**Happy Coding! 🚀**

</div>
