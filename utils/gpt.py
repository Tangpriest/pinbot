import os
from openai import OpenAI
import base64
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def ask_gpt_vision(question, image_path):
    with open(image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")
    image_url = f"data:image/jpeg;base64,{b64_image}"

    completion = client.chat.completions.create(
        model="qwen-vl-max-latest",  # 可按需更换模型
        messages=[
            {
                "role": "system",
                "content": [{"type": "text", "text": "你是一个简洁的中文助手。请直接用简明中文回答用户问题，不要任何 Markdown 或格式化符号。每次输出尽量控制在20个汉字左右，适合语音和控制台直接播报。"}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": question},
                ],
            },
        ],
        max_tokens=500,
    )
    return completion.choices[0].message.content

def ask_gpt_vision_stream(question, image_path):
    with open(image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")
    image_url = f"data:image/jpeg;base64,{b64_image}"

    stream = client.chat.completions.create(
        model="qwen-vl-max-latest",  # 可按需更换模型
        messages=[
            {
                "role": "system",
                "content": [{"type": "text", "text": "你是一个简洁的中文助手。请直接用简明中文回答用户问题，不要任何 Markdown 或格式化符号。每次输出尽量控制在20个汉字左右，适合语音和控制台直接播报。"}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": question},
                ],
            },
        ],
        max_tokens=500,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if hasattr(delta, "content") and delta.content:
            yield delta.content

def ask_gpt_text_stream(question):
    stream = client.chat.completions.create(
        model="qwen-plus",  # 纯文本模型
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": "你是一个简洁的中文助手。请直接用简明中文回答用户问题，不要任何 Markdown 或格式化符号。每次输出尽量控制在20个汉字左右，适合语音和控制台直接播报。"}
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question}
                ],
            },
        ],
        max_tokens=500,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if hasattr(delta, "content") and delta.content:
            yield delta.content

def handle_sentence(question):
    global is_processing
    if is_processing:
        print("AI 正在回答，忽略本次输入。")
        return
    is_processing = True
    print(f"🧠 is_processing: {is_processing}")
    try:
        if not question:
            is_processing = False
            return
        if "退出" in question:
            print("检测到退出指令，程序结束。")
            exit(0)
        print(f"🧠 你问的是: {question}")

        image_path = None
        if need_camera_by_llm(question):
            image_path = capture_frame()
            print("📤 正在请求 通义千问（带图片）")
        else:
            print("📤 正在请求 通义千问（纯文本）")

        if image_path:
            text_stream = ask_gpt_vision_stream(question, image_path)
        else:
            text_stream = ask_gpt_text_stream(question)

        # 只打印内容，不调用TTS
        for part in text_stream:
            print("text_stream内容:", repr(part), type(part))
        print()  # 换行
    finally:
        is_processing = False