# -*- coding: utf-8 -*-
from flask import Flask, render_template, Response, request
from Thermal_Camera import Camera
from setting import *
import cv2
import numpy as np
from glob import glob
import os
import time
import numpy as np

app = Flask(__name__)

def convert_raw2rgb(frame):
    def raw_to_8bit(data):
        cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(data, 8, data)
        return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)
    # 画像表示側への処理
    frame = raw_to_8bit(frame)
    frame = cv2.resize(frame,(640, 480))
    frame = cv2.applyColorMap(frame, cv2.COLORMAP_INFERNO)
    return frame

def view_datetimes(img,datetime):
    COLOR = np.array([(0.000, 0.447, 0.741)])
    color = (COLOR * 255).astype(np.uint8).tolist()
    text = f'{datetime[:4]}/{datetime[4:6]}/{datetime[6:8]} {datetime[9:11]}:{datetime[11:13]}:{datetime[13:15]}' 
    txt_color = (0, 0, 0) if np.mean(COLOR) > 0.5 else (255, 255, 255)
    font = cv2.FONT_HERSHEY_SIMPLEX

    txt_size = cv2.getTextSize(text, font, 0.7, 1)[0]

    txt_bk_color = (COLOR * 255 * 0.7).astype(np.uint8).tolist()

    cv2.putText(img, text, (0, 0 + txt_size[1]), font, 0.7, txt_color, thickness=1)
    return img

# previewを見るための機能
NEXT_FRAME_IDX = 0
IMAGES = []
PLAY = 0
SPEED = 1

def generate_images():
    global NEXT_FRAME_IDX, IMAGES, PLAY, SPEED
    # start_timeに基づいて画像ファイルをソートして取得
    # interval = (1.0 / SPEED)  # 再生速度に応じたインターバル（最小0.1秒）
    print('IDX',NEXT_FRAME_IDX, 'SPEED',SPEED,'PLAY', PLAY, 'DATA N',len(IMAGES))
    # 指定されたインデックスから画像を読み込む
    while NEXT_FRAME_IDX < len(IMAGES):
        print('IDX',NEXT_FRAME_IDX, 'SPEED',SPEED,'PLAY', PLAY, 'DATA N',len(IMAGES))
        image_path = IMAGES[NEXT_FRAME_IDX]
        frame = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        frame = convert_raw2rgb(frame)
        frame = cv2.resize(frame,(640, 480))
        frame = view_datetimes(frame,os.path.basename(image_path))
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        # time.sleep(interval)
        if PLAY:
            NEXT_FRAME_IDX += SPEED


#index.htmlを返す
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preview')
def preview():
    return render_template('preview.html')

@app.route('/preview_datetimes ', methods=['POST'])
def preview_datetimes():
    global NEXT_FRAME_IDX, IMAGES, PLAY, SPEED
    if request.method == 'POST':        
        # 日付が入力されていたら初期フレームの設定
        year = request.form.get('year','0')
        month = request.form.get('month','0').zfill(2)    # Ensure month is two digits
        day = request.form.get('day','0').zfill(2)        # Ensure day is two digits
        hour = request.form.get('hour','0').zfill(2)      # Ensure hour is two digits
        minute = request.form.get('minute','0').zfill(2)  # Ensure minute is two digits
        second = request.form.get('second','0').zfill(2)  # Ensure second is two digits
        file_name = f"{year}{month}{day}-{hour}{minute}{second}"
        if year != '0':
            yyyymmdd = year + month + day
            hh = hour + '00'
            print(file_name)
            IMAGES = sorted(glob(os.path.join(FOLODER, yyyymmdd) + '/*/*.png'))
        for idx, file in enumerate(IMAGES):
            if file_name in file:
                NEXT_FRAME_IDX = idx
                break

        print('IDX',NEXT_FRAME_IDX, 'SPEED',SPEED,'PLAY', PLAY, 'DATA N',len(IMAGES))
    return render_template('preview.html')

@app.route('/preview_video_ctrl', methods=['POST'])
def preview_video_ctrl():
    global NEXT_FRAME_IDX, IMAGES, PLAY, SPEED
    if request.method == 'POST':      
        print(request.form)
        # 再生/停止のフラグ
        play = int(request.form.get('play','-1'))
        if play > -1:
            PLAY = play  
        # スキップ調整があればその処理
        skip_seconds = int(request.form.get('skip', '0'))
        if skip_seconds != 0:
            NEXT_FRAME_IDX += int(skip_seconds * FPS)
         
        # 倍速再生があればその処理
        speed = int(request.form.get('speed', '0'))
        if speed != 0:
            SPEED += speed
            NEXT_FRAME_IDX += SPEED
        print('NEXT_FRAME_IDX',NEXT_FRAME_IDX,'SPPED',SPEED, 'PLAY',PLAY,'DATA N', len(IMAGES))
    return render_template('preview.html')

#カメラ映像を配信する
@app.route('/preview_gen')
def preview_gen():
    print('preview_gen')
    return Response(generate_images(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

#カメラ映像を配信する
@app.route('/video')
def video():
    print('video')
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

#カメラオブジェクトから静止画を取得する
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#カメラスレッドを生成してFlaskを起動する
if __name__ == '__main__':
    threaded=True
    video()
    # ip address を入力
    app.run(host="192.168.0.101",port=8888)
