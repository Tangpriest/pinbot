from utils.camera_decision import need_camera_by_llm

if __name__ == "__main__":
    while True:
        question = input("请输入一句话（回车结束，Ctrl+C 退出）：")
        result = need_camera_by_llm(question)
        print(f"是否需要调用摄像头？{result}")