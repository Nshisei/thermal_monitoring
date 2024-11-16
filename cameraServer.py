# -*- coding: utf-8 -*-
from flask import Flask, render_template, Response, request, jsonify
from Camera import *
from setting import *
import cv2
import numpy as np
from glob import glob
import os
import time
import numpy as np
import subprocess
import os

app = Flask(__name__)

# previewを見るための機能
SPEED = 1
IS_RECORDING = False


# Lidar
SCRIPT_PATH = "./run_lidar.sh"
def start_lidar(camera_path, save_dir, max_points, screenshot_interval):
    """LiDAR プログラムを非同期で起動する"""
    if not os.path.isfile(camera_path):
        print(f"Error: Camera position file not found at {camera_path}")
        return
    
    def run():
        try:
            # 実行結果を無視してバックグラウンドで処理
            subprocess.run(
                [SCRIPT_PATH, "start", camera_path, save_dir, str(max_points), str(screenshot_interval)],
                )
        except subprocess.CalledProcessError:
            pass  # 必要に応じてエラー処理を追加

    # 別スレッドで実行
    thread = threading.Thread(target=run)
    thread.daemon = True  # メインスレッド終了時にこのスレッドも終了
    thread.start()

def stop_lidar():
    """LiDAR プログラムを非同期で停止する"""
    def run():
        try:
            # 実行結果を無視してバックグラウンドで処理
            subprocess.run(
                [SCRIPT_PATH, "stop"],
                
            )
        except subprocess.CalledProcessError:
            pass  # 必要に応じてエラー処理を追加

    # 別スレッドで実行
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()


#index.htmlを返す
@app.route('/')
def index():
    return render_template('index.html')


#カメラ映像を配信する
@app.route('/video')
def video():
    print('video')
    # camera = DepthCamera()
    camera = Camera()
    return Response(gen(camera, "thermo"),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_1')
def video_1():
    print('video')
    camera1 = DepthCamera()
    return Response(gen(camera1, "depth"),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_2')
def video_2():
    print('video')
    camera2 = DepthCameraRGB()
    return Response(gen(camera2, "rgb"),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_3')
def video_3():
    print('lidar')
    camera3 = Lidarmid70()
    return Response(gen(camera3, "lidar"),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_recording', methods=['POST'])
def toggle_recording():
    global IS_RECORDING
    print('NOW RECORDING IS', IS_RECORDING)
    if IS_RECORDING:
        stop_lidar()
    else:
        start_lidar(LIDAR_CAMERA_POS_TXT, SAVE_DATA_STEM,
                     LIDAR_VIS_MAX_POINTS, LIDAR_VIS_INTERVAL)    
    IS_RECORDING = not IS_RECORDING
    print('CHANGE TO ', IS_RECORDING)
    return jsonify(is_recording=IS_RECORDING), 200

def save_img(frame, camera_name):
    global IS_RECORDING
    if IS_RECORDING and camera_name not in ["lidar", "OAK-D"]:
        # 現在の日時をベースにファイル名を生成
        dt_now = datetime.datetime.now()
        yyyymmdd = dt_now.strftime('%Y%m%d')
        hh = dt_now.strftime('%H00')
        filename_base = dt_now.strftime('%Y%m%d-%H%M%S_%f')
        path = os.path.join(SAVE_DATA_STEM, camera_name, yyyymmdd, hh, filename_base + f"-{camera_name}.png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        cv2.imwrite(path, frame)
        print("[NOTE] Save file: {}".format(path))

#カメラオブジェクトから静止画を取得する
def gen(camera, camera_name=""):
    while True:
        frame = camera.get_frame()
        save_img(frame, camera_name)
        frame = cv2.imencode('.jpg', frame)[1].tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/heartbeat')
def heartbeat():
    return "Server is alive!", 200

#カメラスレッドを生成してFlaskを起動する
if __name__ == '__main__':
    threaded=True
    # video()
    # video_1()
    # video_2()
    video_3()
    # ip address を入力
    app.run(host=IP_ADDR, port=8888)

