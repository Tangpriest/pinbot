from utils.vision import capture_frame
from utils.gpt import ask_gpt_vision_stream, ask_gpt_text_stream
from utils.tts import stream_tts_play
from utils.ali_asr import AliyunRealtimeASR
from utils.camera_decision import need_camera_by_llm
import os
from dotenv import load_dotenv
# 新增导入
from vosk_test.vosk_websocket_cursor import SpeechRecognizer
from playsound import playsound
import time
import threading

# 指定 .env 文件的绝对路径
ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=ENV_PATH)

# 打印 .env 文件内容，便于调试
try:
    with open(ENV_PATH, 'r') as f:
        print("当前.env内容：")
        print(f.read())
except Exception as e:
    print("读取.env文件失败：", e)

TOKEN = os.getenv("ALI_TTS_TOKEN")
APPKEY = os.getenv("ALI_TTS_APPKEY")

print(TOKEN, APPKEY)

is_processing = False  # 全局状态变量
is_awake = False       # 唤醒状态
WAKEUP_WORD = "小爱同学"
WAKEUP_WAV = "wakeup.mp3"  # 请确保该文件存在

def check_wake_word(text, wake_word="小周同学"):
    # 处理text里面的空字符串
    text = text.replace(" ", "")
    # 遍历唤醒词中的所有连续两个字的组合
    for i in range(len(wake_word) - 1):
        pair = wake_word[i:i+2]
        if pair in text:
            return True
    return False

def check_quit_word(text, wake_word="退下"):
    # 遍历唤醒词中的所有连续两个字的组合
    text = text.replace(" ", "")
    for i in range(len(wake_word) - 1):
        pair = wake_word[i:i+2]
        if pair in text:
            return True
    return False

# 统一大模型请求和TTS逻辑

def handle_sentence(question):
    global is_processing, is_awake
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

        # 打字机+TTS同步
        def filtered_stream():
            for part in text_stream:
                if hasattr(part, 'content'):
                    content = part.content
                else:
                    content = part
                # 过滤 ChoiceDelta 字符串
                if isinstance(content, str) and content.startswith("ChoiceDelta("):
                    continue
                print(content, end='', flush=True)
                yield content
            print()  # 最后补一个换行

        stream_tts_play(filtered_stream(), TOKEN, APPKEY)
        # 播报结束后自动退出对话
        # is_awake = False
        print("播报结束，已退出对话状态")
        is_processing = False

    finally:
        is_processing = False


def handle_sentence_end(text):
    global is_awake, is_processing
    # 只要正在处理，直接丢弃本次输入
    if is_processing:
        print("AI 正在回答，忽略本次输入。")
        return
    print(f"[识别到完整句] {text}")
    if not is_awake:
        if check_wake_word(text, WAKEUP_WORD):
            print("检测到唤醒词，播放唤醒音...")
            # playsound(WAKEUP_WAV)
            is_awake = True
            print("已进入对话状态")
        else:
            print("未检测到唤醒词，继续监听...")
    else:
        if check_quit_word(text, "退下"):
            print("检测到退出词，退出程序...")
            is_awake = False
            print("已退出对话状态")
        else:
            handle_sentence(text)


def handle_sentence_begin(text):
    # 这里可以做句子开始的处理，目前不需要
    pass

def main():
    # 用 vosk 语音识别替换阿里云 asr
    recognizer = SpeechRecognizer(handle_sentence_begin, handle_sentence_end)
    recognizer.start()

# 1s后调用   handle_sentence_end  输入 "小周同学"
def test():
    handle_sentence_end("小周同学")
    time.sleep(0.5)
    handle_sentence_end("评价一下特朗普")
    handle_sentence_end("这一段应该被忽略")


def TestSpeechRecognizer():
    print("=== TestSpeechRecognizer 并发测试开始 ===")
    handle_sentence_end("小周同学")
    threads = []
    def ask1():
        time.sleep(0.1)
        print("ask1")
        handle_sentence_end("客观评价特朗普")
    def ask2():
        time.sleep(0.2)
        print("ask2")
        handle_sentence_end("客观评价一下詹姆斯")
    t1 = threading.Thread(target=ask1)
    t2 = threading.Thread(target=ask2)
    t1.start()
    t2.start()
    threads.append(t1)
    threads.append(t2)
    for t in threads:
        t.join()
    print("=== TestSpeechRecognizer 并发测试结束 ===")

if __name__ == "__main__":
    TestSpeechRecognizer()