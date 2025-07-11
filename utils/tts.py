from gtts import gTTS
import playsound
import os
import nls
import time
import pyaudio


def stream_tts_play(text_stream, token, appkey, voice="xiaoyun", sample_rate=24000):
    """
    将大模型流式输出（text_stream）实时送入TTS并播放。
    text_stream: 可迭代的文本流（如 ask_gpt_vision_stream 的返回值）
    token, appkey: 阿里云TTS鉴权参数
    voice, sample_rate: TTS参数
    """
    player = pyaudio.PyAudio()
    stream = player.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        output=True
    )

    def on_data(data, *args):
        stream.write(data)

    def on_error(message, *args):
        print(f"TTS发生错误: {message}")

    def on_close(*args):
        stream.stop_stream()
        stream.close()
        player.terminate()
        print("TTS连接关闭")

    tts = nls.NlsStreamInputTtsSynthesizer(
        url="wss://nls-gateway-cn-beijing.aliyuncs.com/ws/v1",
        token=token,
        appkey=appkey,
        on_data=on_data,
        on_error=on_error,
        on_close=on_close,
        callback_args=[],
    )

    tts.startStreamInputTts(
        voice=voice,
        aformat="wav",
        sample_rate=sample_rate,
        volume=100,
        speech_rate=10,
        pitch_rate=0,
    )

    for part in text_stream:
        if part.strip():
            tts.sendStreamInputTts(part)
            time.sleep(0.05)  # 防止文本堆积，可根据体验调整
    tts.stopStreamInputTts()