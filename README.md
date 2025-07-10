# 🧠 Multimodal Assistant - CLI 版

> 一个基于语音与摄像头的 AI 多模态私人助理。你可以用语音提问，它将从摄像头抓取图像并结合 GPT-4-Vision 给出回答，然后用语音朗读出来。

## 📌 功能目标

- 🎤 用户使用麦克风语音提问，例如：“这是什么？”
- 📸 系统调用摄像头拍摄当前画面
- 🤖 使用 OpenAI GPT-4 Vision 模型进行图像 + 问题分析
- 🔊 将模型回答朗读出来
- ❌ 不需要 Web 界面，只使用终端命令行交互

## 📦 项目结构

```
multimodal_assistant/
├── main.py
├── utils/
│   ├── audio.py
│   ├── vision.py
│   ├── gpt.py
│   └── tts.py
├── .env
└── requirements.txt
```

## ✅ 依赖需求

### Python 环境：
- Python 3.8+

### 安装依赖：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🔐 API Key 配置

请在项目根目录创建 `.env` 文件，填入你的 OpenAI API Key：

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 🚀 使用方式

```bash
python main.py
```

然后你就可以对麦克风说：“这是什么？”，它会自动截图并提问 GPT-4 Vision，最终用语音回答。

## 🔄 可扩展方向

- Whisper 本地语音识别
- TTS 语音合成替代（piper / edge-tts）
- 树莓派部署适配
- 多轮对话逻辑
