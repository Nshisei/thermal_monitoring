import cv2          #Opencv
import pyrealsense2 as rs
import numpy as np
import sys          #変数&関数
import datetime     #時刻
import os           #FILE&directory
import time
from base_camera import * 
###################################################
## 定数定義
###################################################
#動画の格納パス
#ファイル名を時刻にするため時刻取得
from setting import *



class Camera(BaseCamera):
    ###################################################
    ## カメラ処理のメインメソッド
    ###################################################
    @staticmethod
    def frames():
        print("camera_id", THREMAL_CAMERA_WIDE_ID)
        cap = cv2.VideoCapture(THREMAL_CAMERA_WIDE_ID) #wseb camera
        FRAME_ID = 0
        if not cap.isOpened():
            print("Webカメラが開けませんでした。")
            cap.release()
            return False
        
        while True: #カメラから画像を取得してファイルに書き込むことを繰り返す
            # カメラから映像を取得
            ret, frame = cap.read() #画像の取得が成功したかどうかの結果取得(True成功/Fales失敗)
            if ret:
                frame = cv2.resize(frame,(640,480))
                #ライブ配信用に画像を返す
                yield frame

class Camera2(BaseCamera):
    ###################################################
    ## カメラ処理のメインメソッド
    ###################################################
    @staticmethod
    def frames():
        print("camera_id", THREMAL_CAMERA_ID)
        cap = cv2.VideoCapture(THREMAL_CAMERA_ID) #wseb camera
        FRAME_ID = 0
        if not cap.isOpened():
            print("Webカメラが開けませんでした。")
            cap.release()
            return False
        
        while True: #カメラから画像を取得してファイルに書き込むことを繰り返す
            # カメラから映像を取得
            ret, frame = cap.read() #画像の取得が成功したかどうかの結果取得(True成功/Fales失敗)
            if ret:
                frame = cv2.resize(frame,(640,480))
                #ライブ配信用に画像を返す
                yield frame


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
        def save_depth_raw(depth_image):
            dt_now = datetime.datetime.now()
            yyyymmdd = dt_now.strftime('%Y%m%d')
            hh = dt_now.strftime('%H00')
            filename_base = dt_now.strftime('%Y%m%d-%H%M%S_%f')
            depthraw_path = os.path.join(SAVE_DATA_STEM, "realsense_depth", yyyymmdd, hh, filename_base + f"-realsense_depth.npy")
            os.makedirs(os.path.dirname(depthraw_path), exist_ok=True)
            np.save(depthraw_path, depth_image)
        while True: #カメラから画像を取得してファイルに書き込むことを繰り返す
            # カメラから映像を取得
            frame = pipe.wait_for_frames()
            depth_frame = frame.get_depth_frame()
            depth_image = np.asanyarray(depth_frame.get_data())
            # 深度画像を0〜255にスケーリング
            save_depth_raw(depth_image)
            depth_image_normalized = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)
            depth_image = cv2.cvtColor(depth_image_normalized,cv2.COLOR_GRAY2RGB)
            yield depth_image

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
class PNGHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__() 
        self.latest_image = None
        self.frame_available = False

    def on_created(self, event):
        # 新しく作成されたファイルがPNGかどうかを確認
        print(event.src_path)
        if event.src_path.endswith(".png"):
            print(f"New PNG detected: {event.src_path}")
            frame = cv2.imread(event.src_path)
            if frame is not None:
                self.latest_image = frame
                self.frame_available = True


class OAKDPRO(BaseCamera):
    @staticmethod
    def frames():
        # 保存ディレクトリの存在確認
        OAK_SAVE_DIR = os.path.join(SAVE_DATA_STEM, "OAK-D", "depth")  # 保存ディレクトリを指定
        os.makedirs(OAK_SAVE_DIR, exist_ok=True)
        handler = PNGHandler()
        observer = Observer()
        observer.schedule(handler, OAK_SAVE_DIR, recursive=True)
        observer.start()
        print("OAK-D PRO observe")
        try:
            while True:
                if handler.frame_available:
                    yield handler.latest_image
                    handler.frame_available = False
        except KeyboardInterrupt:
            print("Stopped OAK-D PRO monitoring.")
        finally:
            observer.stop()
            observer.join()

class Lidarmid70(BaseCamera):
    @staticmethod
    def frames():
        # 保存ディレクトリの存在確認
        LIDAR_SAVE_DIR = os.path.join(SAVE_DATA_STEM, "Lidar", "png")  # 保存ディレクトリを指定
        os.makedirs(LIDAR_SAVE_DIR, exist_ok=True)
        handler = PNGHandler()
        observer = Observer()
        observer.schedule(handler, LIDAR_SAVE_DIR, recursive=True)
        observer.start()
        print("Lidar observe")
        try:
            while True:
                if handler.frame_available:
                    yield handler.latest_image
                    handler.frame_available = False
        except KeyboardInterrupt:
            print("Stopped Lidar monitoring.")
        finally:
            observer.stop()
            observer.join()

