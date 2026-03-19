# myPAW - 自主 AI 助手 (OpenClaw 克隆版)

本项目包含一个 Python 桌面端中控台（PyQt5）和一个 Android 原生移动端应用。

## 核心功能
- **桌面端 (Desktop):** LLM 任务编排、日志可视化、技能系统（Skill System）。
- **移动端 (Android):** 远程指令下达、即时消息同步。
- **技能系统:** 模仿 OpenClaw 插件化设计，支持 Python 编写新技能。

## 快速开始

### 1. 桌面端 (Windows)
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 配置 `.env` 文件，填入您的 LongCat API 密钥：
   ```
   LLM_API_KEY=your_longcat_api_key_here
   LLM_API_BASE=https://api.longcat.chat/openai
   LLM_MODEL=LongCat-Flash-Thinking-2601
   ```
3. 运行主程序：
   ```bash
   # 若要无控制台运行，可将 .py 改为 .pyw 或使用 pythonw
   python main_desktop.py
   ```

### 2. 移动端 (Android)
1. 将 `android/` 目录导入 Android Studio。
2. 在 `MainActivity.kt` 中，将 `baseUrl` 修改为您的桌面端局域网 IP 地址。
3. 确保手机与电脑处于同一局域网，编译并运行。

## 扩展技能
在 `skills/` 目录下创建新的 `.py` 文件，继承 `BaseSkill` 类并实现 `run` 方法。系统将在启动时自动加载。

## 技术栈
- **Desktop:** Python 3.10+, PyQt5, FastAPI, Uvicorn, Requests.
- **Android:** Kotlin, Retrofit2, Gson, RecyclerView (MVVM).
- **LLM API:** LongCat API 开放平台 (兼容 OpenAI API 格式)

## LongCat API 配置

### API 端点
- **OpenAI 格式**: `https://api.longcat.chat/openai`
- **Anthropic 格式**: `https://api.longcat.chat/anthropic`

### 支持的模型
- `LongCat-Flash-Chat`: 高性能通用对话模型
- `LongCat-Flash-Thinking`: 深度思考模型
- `LongCat-Flash-Thinking-2601`: 升级版深度思考模型 ⭐ (推荐)
- `LongCat-Flash-Lite`: 高效轻量化MoE模型

### 环境变量配置
在 `.env` 文件中配置以下参数：
```
LLM_API_KEY=your_longcat_api_key_here
LLM_API_BASE=https://api.longcat.chat/openai
LLM_MODEL=LongCat-Flash-Thinking-2601
```
