import nls
import sounddevice as sd
import numpy as np
import threading
import json

URL = "wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1"
TOKEN = "3fa83c9e482a4bc08c83990a1280fe4e"
APPKEY = "FsUpfzZ1z4S5YPP6"

SAMPLE_RATE = 16000
CHANNELS = 1

class AliyunRealtimeASR:
    def __init__(self):
        self.transcriber = nls.NlsSpeechTranscriber(
            url=URL,
            token=TOKEN,
            appkey=APPKEY,
            on_sentence_begin=None,
            on_sentence_end=self.on_sentence_end,
            on_start=None,
            on_result_changed=None,
            on_completed=None,
            on_error=None,
            on_close=None,
            callback_args=[]
        )
        self.running = True

    def on_sentence_end(self, message, *args):
        result = json.loads(message)
        text = result.get("payload", {}).get("result", "")
        print("用户完整提问：", text)

    def start(self):
        self.transcriber.start(
            aformat="pcm",
            sample_rate=SAMPLE_RATE,
            ch=CHANNELS,
            enable_intermediate_result=True,
            enable_punctuation_prediction=True,
            enable_inverse_text_normalization=True
        )
        print("开始说话，Ctrl+C 退出...")

        def callback(indata, frames, time, status):
            audio_bytes = (indata * 32767).astype(np.int16).tobytes()
            self.transcriber.send_audio(audio_bytes)

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32', blocksize=1600, callback=callback):
            try:
                while self.running:
                    pass
            except KeyboardInterrupt:
                print("手动退出")
            finally:
                self.transcriber.stop()
                self.transcriber.shutdown()

if __name__ == "__main__":
    asr = AliyunRealtimeASR()
    asr.start() 