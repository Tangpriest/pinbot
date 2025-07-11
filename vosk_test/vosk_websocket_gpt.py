import asyncio
import websockets
import sounddevice as sd
import numpy as np
import json
import wave

WS_SERVER_URI = "ws://172.17.17.130:2700"
RATE = 16000
CHANNELS = 1
BLOCKSIZE = 8000

async def send_audio():
    async with websockets.connect(WS_SERVER_URI) as websocket:
        loop = asyncio.get_event_loop()

        # 新增：打开wav文件用于写入
        wf = wave.open("recorded.wav", "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # int16 = 2字节
        wf.setframerate(RATE)

        def callback(indata, frames, time, status):
            if status:
                print(status)
            # 写入wav文件
            wf.writeframes(indata.tobytes())
            # 发送到服务器
            asyncio.run_coroutine_threadsafe(websocket.send(indata.tobytes()), loop)

        with sd.InputStream(samplerate=RATE, channels=CHANNELS,
                            blocksize=BLOCKSIZE, dtype='int16',
                            callback=callback):
            print("开始录音并发送音频流，按 Ctrl+C 停止")
            try:
                while True:
                    result = await websocket.recv()
                    res_json = json.loads(result)
                    if 'text' in res_json:
                        print("识别结果:", res_json['text'])
            except KeyboardInterrupt:
                print("已停止录音")
            finally:
                # 关闭wav文件
                wf.close()

asyncio.run(send_audio())
