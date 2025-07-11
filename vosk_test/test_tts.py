from vosk_websocket_cursor import SpeechRecognizer

def on_sentence_begin(text):
    print(f"[测试] 句子开始: {text}")

def on_sentence_end(text):
    print(f"[测试] 句子结束: {text}")

if __name__ == "__main__":
    recognizer = SpeechRecognizer(on_sentence_begin, on_sentence_end, save_wav_path="test_tts_realtime.wav")
    recognizer.start() 