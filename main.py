from utils.vision import capture_frame
from utils.gpt import ask_gpt_vision_stream
from utils.tts import stream_tts_play
from utils.ali_asr import AliyunRealtimeASR


TOKEN = "3fa83c9e482a4bc08c83990a1280fe4e"
APPKEY = "FsUpfzZ1z4S5YPP6"

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
        image_path = capture_frame()
        print("📤 正在请求 通义千问")
        print("🤖 GPT 回答:", end="", flush=True)
        text_stream = ask_gpt_vision_stream(question, image_path)
        stream_tts_play(text_stream, TOKEN, APPKEY)
        print()  # 换行
    finally:
        is_processing = False

def main():
    asr = AliyunRealtimeASR(token=TOKEN, appkey=APPKEY, on_sentence=handle_sentence)
    asr.start()

if __name__ == "__main__":
    main()