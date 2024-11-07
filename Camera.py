import cv2          #Opencv
import pyrealsense2 as rs
import numpy as np
import sys          #変数&関数
import datetime     #時刻
import os           #FILE&directory
from loguru import logger
import time
from base_camera import * 
from PIL import Image
###################################################
## 定数定義
###################################################
#動画の格納パス
#ファイル名を時刻にするため時刻取得
from setting import *
os.makedirs(LOGDIR, exist_ok=True)
size = (160, 120)
from copy import deepcopy
#保存形式指定
size = (160, 120) #画像サイズ
logger.add(os.path.join(LOGDIR,"logtest.log"), rotation="1h")


class Camera(BaseCamera):
    ###################################################
    ## カメラ処理のメインメソッド
    ###################################################
    @staticmethod
    def frames():
        print("camera_id", 0)
        cap = cv2.VideoCapture(0) #wseb camera
        FRAME_ID = 0
        if not cap.isOpened():
            logger.error("Webカメラが開けませんでした。")
            cap.release()
            return False
        
        while True: #カメラから画像を取得してファイルに書き込むことを繰り返す
            # カメラから映像を取得
            ret, frame = cap.read() #画像の取得が成功したかどうかの結果取得(True成功/Fales失敗)
            dt_now = datetime.datetime.now()
            yyyymmdd = dt_now.strftime('%Y%m%d')
            hh = dt_now.strftime('%H00')
            file_name = dt_now.strftime('%Y%m%d-%H%M%S_%f')
            output_path = os.path.join(FOLDER, "camera0", file_name + '-thermo.png')
            os.makedirs(os.path.join(FOLDER, "camera0"), exist_ok=True)
            if ret:
                cv2.imwrite(output_path, frame)
                frame = cv2.resize(frame, (size))     #保存形式指定のフレーム
                cv2.imwrite(output_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                frame = cv2.resize(frame,(640,480))
                #ライブ配信用に画像を返す
                yield frame

            else:
                logger.error(f"Fail {output_path}")

class DepthCameraRGB(BaseCamera):
    ###################################################
    ## カメラ処理のメインメソッド
    ###################################################
    @staticmethod
    def frames():
        pipe = rs.pipeline()
        cfg  = rs.config()

        cfg.enable_stream(rs.stream.color, 640,480, rs.format.bgr8, 30)
        pipe.start(cfg)
        while True: #カメラから画像を取得してファイルに書き込むことを繰り返す
            # カメラから映像を取得
            frame = pipe.wait_for_frames()
            color_frame = frame.get_color_frame()
            color_image = np.asanyarray(color_frame.get_data())
            yield color_image


class DepthCamera(BaseCamera):
    ###################################################
    ## カメラ処理のメインメソッド
    ###################################################
    @staticmethod
    def frames():
        pipe = rs.pipeline()
        cfg  = rs.config()
        cfg.enable_stream(rs.stream.depth, 640,480, rs.format.z16, 30)
        pipe.start(cfg)
        while True: #カメラから画像を取得してファイルに書き込むことを繰り返す
            # カメラから映像を取得
            frame = pipe.wait_for_frames()
            depth_frame = frame.get_depth_frame()
            depth_image = np.asanyarray(depth_frame.get_data())
            # 深度画像を0〜255にスケーリング
            depth_image_normalized = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)
            depth_image = cv2.cvtColor(depth_image_normalized,cv2.COLOR_GRAY2RGB)
            yield depth_image