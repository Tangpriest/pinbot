import pyaudio
import websocket
import json
import threading
import wave

# Vosk 服务器 websocket 地址
VOSK_SERVER_URL = "ws://172.17.17.130:2700"
# 音频参数
RATE = 16000
CHUNK = 4000
FORMAT = pyaudio.paInt16
CHANNELS = 1

class SpeechRecognizer:
    def __init__(self, on_sentence_begin, on_sentence_end, save_wav_path=None):
        self.on_sentence_begin = on_sentence_begin
        self.on_sentence_end = on_sentence_end
        self.save_wav_path = save_wav_path
        self._last_partial = ""
        self._frames = []
        self._running = False

    def _on_message(self, ws, message):
        data = json.loads(message)
        # 句子开始判定
        if 'partial' in data:
            current_text = data['partial']
            if current_text and not self._last_partial:
                if self.on_sentence_begin:
                    self.on_sentence_begin(current_text)
            self._last_partial = current_text
        # 句子结束判定
        if 'text' in data:
            if self.on_sentence_end:
                self.on_sentence_end(data['text'])
            self._last_partial = ""

    def _on_error(self, ws, error):
        print("WebSocket 错误:", error)

    def _on_close(self, ws, close_status_code, close_msg):
        print("WebSocket 连接关闭")
        self._running = False

    def _on_open(self, ws):
        def run(*args):
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
            print("开始说话...")
            ws.send(json.dumps({"config": {"sample_rate": RATE}}))
            self._frames = []
            self._running = True
            try:
                while self._running:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    ws.send(data, opcode=websocket.ABNF.OPCODE_BINARY)
                    if self.save_wav_path:
                        self._frames.append(data)
            except KeyboardInterrupt:
                print("停止录音")
            finally:
                stream.stop_stream()
                stream.close()
                p.terminate()
                if self.save_wav_path and self._frames:
                    wf = wave.open(self.save_wav_path, "wb")
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(self._frames))
                    wf.close()
                ws.close()
        threading.Thread(target=run).start()

    def start(self):
        ws = websocket.WebSocketApp(VOSK_SERVER_URL,
                                    on_open=self._on_open,
                                    on_message=self._on_message,
                                    on_error=self._on_error,
                                    on_close=self._on_close)
        ws.run_forever()

    def stop(self):
        self._running = False

# 示例用法
if __name__ == "__main__":
    def on_begin(text):
        print(f"事件 句子开始: {text}")
    def on_end(text):
        print(f"事件 句子结束: {text}")
    recognizer = SpeechRecognizer(on_begin, on_end, save_wav_path="test_realtime.wav")
    recognizer.start()
