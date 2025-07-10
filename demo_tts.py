import nls
import time
import pyaudio

# 初始化 pyaudio
player = pyaudio.PyAudio()
stream = player.open(
    format=pyaudio.paInt16,  # 16位音频
    channels=1,              # 单声道
    rate=24000,              # 采样率要和 TTS 设置一致
    output=True
)

# 配置回调
def on_data(data, *args):
    print(f"收到音频数据，长度: {len(data)} 字节")
    stream.write(data)  # 实时播放

def on_error(message, *args):
    print(f"发生错误: {message}")

def on_close(*args):
    print("连接关闭")
    stream.stop_stream()
    stream.close()
    player.terminate()

# 创建 TTS 实例
# TOKEN = "3fa83c9e482a4bc08c83990a1280fe4e"
# APPKEY = "FsUpfzZ1z4S5YPP6"
sdk = nls.NlsStreamInputTtsSynthesizer(
    url="wss://nls-gateway-cn-beijing.aliyuncs.com/ws/v1",
    token="3fa83c9e482a4bc08c83990a1280fe4e",      # 替换为你的token
    appkey="FsUpfzZ1z4S5YPP6",    # 替换为你的appkey
    on_data=on_data,
    on_error=on_error,
    on_close=on_close,
    callback_args=[],
)

# 启动流式TTS
sdk.startStreamInputTts(
    voice="xiaoyun",     # 可选音色
    aformat="wav",       # 输出格式
    sample_rate=24000,   # 采样率
    volume=50,
    speech_rate=0,
    pitch_rate=0,
)

# 发送文本
sdk.sendStreamInputTts("你好，这是一段流式语音合成的测试。")
time.sleep(0.1)
sdk.sendStreamInputTts("你可以把多句话分多次发送。")
time.sleep(0.1)

# 停止并收尾
sdk.stopStreamInputTts()