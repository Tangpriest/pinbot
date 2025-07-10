import sounddevice as sd
import numpy as np

def callback(indata, frames, time, status):
    print("采集到音频数据:", indata.shape)

with sd.InputStream(samplerate=16000, channels=1, dtype='float32', callback=callback):
    input("说话试试，按回车退出\n")