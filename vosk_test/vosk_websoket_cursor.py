import pyaudio
import websocket
import json
import threading

# Vosk 服务器 websocket 地址
VOSK_SERVER_URL = "ws://172.17.17.130:2700"

# 音频参数
RATE = 16000
CHUNK = 4000
FORMAT = pyaudio.paInt16
CHANNELS = 1


def on_message(ws, message):
    data = json.loads(message)
    if 'text' in data:
        print("识别结果:", data['text'])
    elif 'partial' in data:
        print("临时结果:", data['partial'])

def on_error(ws, error):
    print("WebSocket 错误:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket 连接关闭")

def on_open(ws):
    def run(*args):
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        print("开始说话...")
        try:
            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                ws.send(data, opcode=websocket.ABNF.OPCODE_BINARY)
        except KeyboardInterrupt:
            print("停止录音")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            ws.close()
    threading.Thread(target=run).start()

if __name__ == "__main__":
    ws = websocket.WebSocketApp(VOSK_SERVER_URL,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()
