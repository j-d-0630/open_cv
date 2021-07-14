"""
顔検出アプリ
"""
import cv2
# VideoCaptureオブジェクト取得
capture = cv2.VideoCapture(0) # 引数は接続されてるカメラの番号