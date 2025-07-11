from gtts import gTTS

def generate_voice(text, filename):
    """
    将输入文本合成为语音并保存为指定文件名（如mp3）。
    :param text: 要合成的文本内容
    :param filename: 保存的音频文件名（如 'tongxue.mp3'）
    """
    tts = gTTS(text=text, lang='zh')
    tts.save(filename)

# 示例用法：
generate_voice("嘿哟，我是你的小周同学", "wakup.mp3")
