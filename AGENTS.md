# AGENTS.md - AI 代理配置文档

本文档说明项目中使用的 AI 代理配置和提示词生成服务。

## AI 提供商

项目支持两种 AI 提供商，通过环境变量 `AI_PROVIDER` 配置：

### 1. Ollama (默认)

**配置参数:**
```env
AI_PROVIDER=ollama
OLLAMA_MODEL=huihui_ai/qwen3-abliterated:30b
OLLAMA_URL=http://localhost:11434
```

**特点:**
- 本地部署，数据隐私性强
- 需要本地运行 Ollama 服务
- 支持多种开源模型
- 默认端口：11434

**使用场景:**
- 对数据隐私有要求的场景
- 需要离线工作的环境
- 自定义模型训练

### 2. Gemini

**配置参数:**
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_BASE_URL=https://api.laozhang.ai/v1/
```

**特点:**
- 云端 API 服务
- 响应速度快
- 需要 API 密钥
- 支持流式响应

**使用场景:**
- 需要快速响应的场景
- 不便部署本地模型的环境
- 对最新模型能力有要求

## 提示词生成服务

### 核心模块

**位置:** `src/core/prompt/generator.py`

**主要功能:**
- 增强用户输入的简单提示词
- 生成详细的 Stable Diffusion 风格提示词
- 支持中英文输入
- 自动添加画质关键词

### 提示词生成流程

```
用户输入 → AI 代理 → 提示词增强 → 返回优化后的提示词
```

### 提示词模板

系统使用固定的提示词模板来指导 AI 生成高质量的图像描述：

```python
PROMPT_TEMPLATE = """
你是一个专业的 Stable Diffusion 提示词专家。
用户会给你一个简单的描述，请帮助扩展成详细的 Stable Diffusion 提示词。

要求：
1. 保持用户原意，不要改变主题
2. 添加详细的画面细节、氛围、光影描述
3. 添加适当的画质关键词（如 masterpiece, best quality, ultra detailed 等）
4. 使用英文逗号分隔的关键词格式
5. 直接输出提示词，不要有其他说明文字

用户输入：{user_prompt}
"""
```

### 使用示例

**输入:**
```
一个女孩在花园里
```

**输出:**
```
masterpiece, best quality, ultra detailed, 8k wallpaper,
a beautiful girl standing in a lush garden,
surrounded by colorful flowers, soft sunlight filtering through trees,
peaceful atmosphere, detailed facial features, elegant pose,
vibrant colors, professional photography, shallow depth of field
```

## 单例模式实现

提示词服务使用单例模式，确保在应用生命周期内只初始化一次：

**位置:** `src/services/prompt_service.py`

**优势:**
- 避免重复初始化 AI 客户端
- 减少资源消耗
- 全局共享配置

**使用方法:**
```python
from src.services.prompt_service import PromptService

service = PromptService.get_instance()
enhanced_prompt = service.generate_prompt("用户输入")
```

## 服务健康检查

在应用启动时，系统会自动检查 AI 服务的可用性：

**Ollama 检查:**
```python
response = requests.get(f"{OLLAMA_URL}/api/tags")
if response.status_code == 200:
    print("✅ Ollama 服务正常")
```

**Gemini 检查:**
```python
client = OpenAI(api_key=GEMINI_API_KEY, base_url=GEMINI_BASE_URL)
# 测试连接
```

## 错误处理

### 常见错误

1. **连接失败**
   - 检查服务是否启动（Ollama）
   - 检查 API 密钥是否正确（Gemini）
   - 检查网络连接

2. **模型未找到**
   - 确认模型名称拼写正确
   - Ollama：使用 `ollama list` 查看可用模型
   - Gemini：查看 API 文档确认模型名称

3. **超时错误**
   - 增加超时时间配置
   - 检查网络延迟
   - 考虑切换到本地部署

## 配置最佳实践

1. **开发环境**: 使用 Ollama 本地部署
2. **生产环境**: 根据负载选择 Ollama 或 Gemini
3. **API 密钥管理**:
   - 使用 `.env` 文件存储密钥
   - 不要将密钥提交到版本控制
   - 定期轮换 API 密钥
4. **性能优化**:
   - 使用单例模式避免重复初始化
   - 考虑添加提示词缓存机制
   - 监控 API 调用频率和成本

## 扩展性

项目设计支持扩展更多 AI 提供商：

1. 在 `src/core/prompt/generator.py` 添加新的生成函数
2. 在 `config/settings.py` 添加新的配置参数
3. 在 `src/services/prompt_service.py` 添加初始化逻辑
4. 更新本文档说明新提供商的使用方法

## 参考资料

- [Ollama 官方文档](https://ollama.ai/)
- [Gemini API 文档](https://ai.google.dev/)
- [Stable Diffusion 提示词指南](https://stable-diffusion-art.com/prompt-guide/)
