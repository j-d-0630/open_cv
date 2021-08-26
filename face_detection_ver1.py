"""
顔検出アプリ

<変更点>
・顔検出時は未検出であることをAWSIOTへ送る処理を追加
・顔検出の周期を3秒に変更
・AWSIOTへの通知内容を現在時刻と検知結果(0：未検知 , 1：検知)に変更
"""
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import datetime
import json

import os
import cv2
import sys

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT, MESSAGE, TOPIC, and RANGE
ENDPOINT = ".amazonaws.com"
CLIENT_ID = "testDevice"
PATH_TO_CERT = "./cert/-certificate.pem.crt"
PATH_TO_KEY = "./cert/-private.pem.key"
PATH_TO_ROOT = "./cert/AmazonRootCA1.pem"
MESSAGE = "Hello World"
TOPIC = "face_detection/testing"

# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=PATH_TO_CERT,
            pri_key_filepath=PATH_TO_KEY,
            client_bootstrap=client_bootstrap,
            ca_filepath=PATH_TO_ROOT,
            client_id=CLIENT_ID,
            clean_session=False,
            keep_alive_secs=6
            )
print("Connecting to {} with client ID '{}'...".format(
        ENDPOINT, CLIENT_ID))
# Make the connect() call
connect_future = mqtt_connection.connect()
# Future.result() waits until a result is available
connect_future.result()
print("Connected!")
# Publish message to server desired number of times.
print('Begin Publish')

#face detect
path = "/home/pi/.local/lib/python3.7/site-packages/cv2/data/"
face_cascade_path = path + "haarcascade_frontalface_default.xml"
eye_cascade_path = path + "haarcascade_eye.xml"
mouth_cascade_path = path + "haarcascade_mcs_mouth.xml"
face_cascade = cv2.CascadeClassifier(face_cascade_path)
eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
mouth_cascade = cv2.CascadeClassifier(mouth_cascade_path)

# VideoCaptureオブジェクト取得
capture = cv2.VideoCapture(0) # 引数は接続されてるカメラの番号

while 1:
  detect_flg = 0 # 検出の有無 (未検出なら0,検出したら1)
  ret, frame = capture.read()

  frame_g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  faces = face_cascade.detectMultiScale(frame_g)
  cv2.putText(frame, 'look at a camera!', (10,30), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0,0,255), thickness=2)

  for x, y, w, h in faces:
    face = frame[y: y + h, x: x + w]
    face1 = frame[y: y + h//2 - 0, x: x + w] # 目を探す範囲を顔の上半分に限定
    face2 = frame[y + h//2 + 35: y + h, x: x + w] # 口を探す範囲を顔の下半分に限定
    face_gray1 = frame_g[y: y + h//2 - 0, x: x + w]
    face_gray2 = frame_g[y + h//2 + 35: y + h, x: x + w]
    eyes = eye_cascade.detectMultiScale(face_gray1)

    for (ex, ey, ew, eh) in eyes:
      mouths = mouth_cascade.detectMultiScale(face_gray2)
      for (mx, my, mw, mh) in mouths:
        detect_flg = 1 # 顔検出したのでフラグを1に設定
        cv2.putText(face2, 'Not masked!!', (mx, my), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0,0,255), thickness=2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.rectangle(face1, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
        cv2.rectangle(face2, (mx, my), (mx + mw, my + mh), (255, 255, 255), 2)

        #Send to AWS IOR CORE
        date = str(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))))
        result = detect_flg
        message = {"detection_result" : [date,result]} # {日本時刻,顔検出結果}を格納
        mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
        print("Published: '" + json.dumps(message) + "' to the topic: " + "'face_detection/testing'")
        t.sleep(0.1)
  
  #顔検出しなかった場合の処理
  if detect_flg == 0:
    #Send to AWS IOR CORE
    date = str(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))))
    result = detect_flg
    message = {"detection_result" : [date,result]} # {日本時刻,顔検出結果}を格納
    mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
    print("Published: '" + json.dumps(message) + "' to the topic: " + "'face_detection/testing'")
    t.sleep(0.1)

  # 描画
  cv2.imshow("image", frame)
  if cv2.waitKey(1) & 0xFF == ord("q"): #waitkeyの引数はキーボードからの入力待ち時間。この時間で再度read()されるまでの時間を調整できる
      print('Publish End')
      disconnect_future = mqtt_connection.disconnect()
      disconnect_future.result()
      break
  
  # 3秒ごとに顔検出実施
  t.sleep(2.9)

capture.release()
cv2.destroyAllWindows()
