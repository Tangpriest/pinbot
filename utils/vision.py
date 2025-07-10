import cv2

def capture_frame(filename="frame.jpg"):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if ret:
        cv2.imwrite(filename, frame)
        return filename
    else:
        raise Exception("摄像头获取失败")