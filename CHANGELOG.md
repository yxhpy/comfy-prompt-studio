# Changelog

本文档记录项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增
- 完善项目文档体系
- 添加 MIT 许可证
- 增强 README 文档
- 添加项目徽章和常见问题

### 改进
- 优化 GitHub 仓库元数据
- 完善 AGENTS.md AI 代理配置文档

## [1.0.0] - 2025-10-27

### 新增
- 🎉 项目首次发布
- ✨ AI 智能提示词增强（支持 Ollama/Gemini）
- ✨ ComfyUI 工作流自动切换（普通/人脸替换）
- ✨ WebSocket 实时进度推送
- ✨ SQLite 历史记录管理系统
- ✨ 工程化目录结构
- ✨ 单例模式服务层
- ✨ 配置分离管理（.env）

### 文档
- 📝 添加 CLAUDE.md 技术文档
- 📝 添加 AGENTS.md 代理配置文档
- 📝 添加 README.md 快速开始指南
- 📝 API 接口文档
- 📝 WebSocket 事件文档

### 重构
- ♻️ 工程化重构和安全配置优化
- ♻️ 从 JSON 迁移到 SQLite 数据库
- ♻️ 模块化路由和服务层
- ♻️ Flask 应用工厂模式

### 修复
- 🐛 修复文档不一致问题
- 🐛 清理冗余文件
- 🐛 优化 .gitignore 配置

## [0.1.0] - 2025-10-XX (早期开发版本)

### 新增
- 首页历史记录按钮
- 图片尺寸配置
- 实时日志功能
- 历史记录管理功能

### 改进
- 顶部栏和图片容器样式优化
- UI 布局和间距调整

---

## 版本说明

### 主版本号 (Major)
当做了不兼容的 API 修改时递增

### 次版本号 (Minor)
当做了向下兼容的功能性新增时递增

### 修订号 (Patch)
当做了向下兼容的问题修正时递增

## 未来计划

### v1.1.0 (计划中)
- [ ] 添加用户认证系统
- [ ] 支持批量生成
- [ ] 添加更多 AI 提供商
- [ ] 性能优化和缓存机制
- [ ] 国际化支持

### v1.2.0 (规划中)
- [ ] 图片编辑功能
- [ ] 提示词模板库
- [ ] 社区分享功能
- [ ] Docker 容器化部署
- [ ] API 限流和配额管理

### v2.0.0 (远期目标)
- [ ] 微服务架构重构
- [ ] 分布式任务队列
- [ ] 云端部署方案
- [ ] 商业版功能

---

**链接:**
- [Unreleased]: https://github.com/yxhpy/comfy-prompt-studio/compare/v1.0.0...HEAD
- [1.0.0]: https://github.com/yxhpy/comfy-prompt-studio/releases/tag/v1.0.0
