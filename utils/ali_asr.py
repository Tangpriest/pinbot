import nls
import sounddevice as sd
import numpy as np
import json

class AliyunRealtimeASR:
    def __init__(self, token, appkey, on_sentence, sample_rate=16000, channels=1):
        self.transcriber = nls.NlsSpeechTranscriber(
            url="wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1",
            token=token,
            appkey=appkey,
            on_sentence_end=self.on_sentence_end,
            callback_args=[]
        )
        self.running = True
        self.on_sentence = on_sentence
        self.sample_rate = sample_rate
        self.channels = channels

    def on_sentence_end(self, message, *args):
        result = json.loads(message)
        text = result.get("payload", {}).get("result", "")
        if text and self.on_sentence:
            print(f"🔊 监听结束: {text}")
            self.on_sentence(text)

    def start(self):
        self.transcriber.start(
            aformat="pcm",
            sample_rate=self.sample_rate,
            ch=self.channels,
            enable_intermediate_result=True,
            enable_punctuation_prediction=True,
            enable_inverse_text_normalization=True
        )
        print("开始说话，Ctrl+C 退出...")

        def callback(indata, frames, time, status):
            audio_bytes = (indata * 32767).astype(np.int16).tobytes()
            self.transcriber.send_audio(audio_bytes)

        with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, dtype='float32', blocksize=1600, callback=callback):
            try:
                while self.running:
                    pass
            except KeyboardInterrupt:
                print("手动退出")
            finally:
                self.transcriber.stop()
                self.transcriber.shutdown() 