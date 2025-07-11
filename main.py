from utils.vision import capture_frame
from utils.gpt import ask_gpt_vision_stream, ask_gpt_text_stream
from utils.tts import stream_tts_play
from utils.ali_asr import AliyunRealtimeASR
from utils.camera_decision import need_camera_by_llm
import os
from dotenv import load_dotenv

load_dotenv()

# .env
# ALI_TTS_APPKEY=FsUpfzZ1z4S5YPP6
# ALI_TTS_TOKEN=3fa83c9e482a4bc08c83990a1280fe4e

TOKEN = os.getenv("ALI_TTS_TOKEN")
APPKEY = os.getenv("ALI_TTS_APPKEY")

is_processing = False  # 全局状态变量

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

        # 通过大模型 function call 判断是否需要摄像头
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

        stream_tts_play(text_stream, TOKEN, APPKEY)
        print()  # 换行
    finally:
        is_processing = False

def main():
    asr = AliyunRealtimeASR(token=TOKEN, appkey=APPKEY, on_sentence=handle_sentence)
    asr.start()

    # handle_sentence("我今天看起来如何？")

if __name__ == "__main__":
    main()