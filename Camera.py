import cv2          #Opencv
import sys          #変数&関数
import datetime     #時刻
import os           #FILE&directory
from loguru import logger
import time
from base_camera import BaseCamera
from PIL import Image
###################################################
## 定数定義
###################################################
#動画の格納パス
#ファイル名を時刻にするため時刻取得
FOLODER = '/home/shisei/thermal/ssd/test3/'  #保存フォルダ指定
RESULT_FILE = '/home/shisei/thermal/ssd/test3/result.png'
LOGDIR = '/home/shisei/thermal/ssd/test3/logs/'
RESIZE_RETIO = 0.4
os.makedirs(LOGDIR, exist_ok=True)
size = (160, 120)

#保存形式指定
size = (160, 120) #画像サイズ
logger.add("/home/shisei/thermal/ssd/test3/logs/logtest.log", rotation="1h")


class Camera(BaseCamera):           #<--２箇所目
    ###################################################
    ## カメラ処理のメインメソッド
    ###################################################
    @staticmethod
    def frames():
        cap = cv2.VideoCapture(0) #wseb camera
        FRAME_ID = 0

        if not cap.isOpened():
            logger.error("Webカメラが開けませんでした。")
            cap.release()
            return False
        
        dt_now = datetime.datetime.now()
        yyyymmdd = dt_now.strftime('%Y%m%d')
        hh = dt_now.strftime('%H00')
        file_name = dt_now.strftime('%Y%m%d-%H%M%S_%f')
        save_dir = os.path.join(FOLODER, yyyymmdd, hh)
        os.makedirs(save_dir, exist_ok=True)
        output_path = os.path.join(save_dir, file_name + '.png')

        while True: #カメラから画像を取得してファイルに書き込むことを繰り返す
            # カメラから映像を取得
            ret, frame = cap.read() #画像の取得が成功したかどうかの結果取得(True成功/Fales失敗)
            if ret:
                # フレームの取得に成功したらPNG形式で保存
                #画面サイズを指定&window表示
                frame = cv2.resize(frame, (size))     #保存形式指定のフレーム
                cv2.imwrite(output_path, frame)
                logger.info(f"SAVE {output_path}")
                if FRAME_ID % 5 == 0:
                    FRAME_ID = 1
                    frame = cv2.resize(frame,(int(160 / RESIZE_RETIO),int(120 / RESIZE_RETIO)))

                    #ライブ配信用に画像を返す
                    yield cv2.imencode('.jpg', frame)[1].tobytes()

                else:
                    FRAME_ID += 1
            else:
                logger.error(f"Fail {output_path}")