"""
顔検出アプリ
"""
import os
import cv2
import sys

os.system("cd")
print(sys.base_prefix)
print(cv2)

# path = "C:\\Users\\junichi doi\\AppData\\Local\\Programs\\Python\\Python37\\Lib\\site-packages\\cv2\\data\\" #自宅用
path = "C:\\Users\\e12503\\AppData\\Local\\Programs\\Python\\Python37\\Lib\\site-packages\\cv2\\data\\" # 会社用
face_cascade_path = path + "haarcascade_frontalface_default.xml"
eye_cascade_path = path + "haarcascade_eye.xml"
mouth_cascade_path = path + "haarcascade_mcs_mouth.xml"
face_cascade = cv2.CascadeClassifier(face_cascade_path)
eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
mouth_cascade = cv2.CascadeClassifier(mouth_cascade_path)

# VideoCaptureオブジェクト取得
capture = cv2.VideoCapture(0) # 引数は接続されてるカメラの番号

# lena = cv2.imread("lena.png")
while 1:
    ret, frame = capture.read()
    # frame = lena
    frame_g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(frame_g)
    cv2.putText(frame, 'look at a camera!', (10,30), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0,0,255), thickness=2)

    # 【AI】顔の中に目（と口）がある場合に人と認識するに改良する
    for x, y, w, h in faces:
        # cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        face = frame[y: y + h, x: x + w]
        face1 = frame[y: y + h//2 - 0, x: x + w] # 目を探す範囲を顔の上半分に限定
        face2 = frame[y + h//2 + 35: y + h, x: x + w] # 口を探す範囲を顔の下半分に限定
        face_gray1 = frame_g[y: y + h//2 - 0, x: x + w]
        face_gray2 = frame_g[y + h//2 + 35: y + h, x: x + w]
        eyes = eye_cascade.detectMultiScale(face_gray1)
        # print("顔ある")
        for (ex, ey, ew, eh) in eyes:
            # print("目もある")
            mouths = mouth_cascade.detectMultiScale(face_gray2)
            for (mx, my, mw, mh) in mouths:
                cv2.putText(face2, 'Not masked!!', (mx, my), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0,0,255), thickness=2)
                # print("口もある")
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.rectangle(face1, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                cv2.rectangle(face2, (mx, my), (mx + mw, my + mh), (255, 255, 255), 2)


    cv2.imshow("image", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"): #waitkeyの引数はキーボードからの入力待ち時間。この時間で再度read()されるまでの時間を調整できる
        break

capture.release()
cv2.destroyAllWindows()
