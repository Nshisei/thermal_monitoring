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

#OAK-D PRO
SCRIPT_PATH_DEPTH = "./run_depth.sh"

def start_depth():
    """OAK-D PRO デプスカメラプログラムを非同期で起動する"""
    

    def run():
        try:
            # 実行結果を無視してバックグラウンドで処理
            subprocess.run(
                [SCRIPT_PATH_DEPTH, "start"],
            )
        except subprocess.CalledProcessError:
            pass  # 必要に応じてエラー処理を追加

    # 別スレッドで実行
    thread = threading.Thread(target=run)
    thread.daemon = True  # メインスレッド終了時にこのスレッドも終了
    thread.start()

def stop_depth():
    """OAK-D PRO デプスカメラプログラムを非同期で停止する"""
    def run():
        try:
            # 実行結果を無視してバックグラウンドで処理
            subprocess.run(
                [SCRIPT_PATH_DEPTH, "stop"],
            )
        except subprocess.CalledProcessError:
            pass  # 必要に応じてエラー処理を追加

    # 別スレッドで実行
    thread = threading.Thread(target=run)
    thread.daemon = True  # メインスレッド終了時にこのスレッドも終了
    thread.start()


#index.htmlを返す
@app.route('/')
def index():
    return render_template('index.html')


#カメラ映像を配信する
@app.route('/thremal_wide')
def thremal_wide():
    print('thremal_wide')
    # camera = DepthCamera()
    camera = Camera()
    return Response(gen(camera, "thermo_wide"),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

#カメラ映像を配信する
@app.route('/thermal')
def thermal():
    print('thermal')
    # camera = DepthCamera()
    camera = Camera2()
    return Response(gen(camera, "thermo"),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/realsense')
def realsense():
    print('realsense')
    camera = DepthCamera()
    return Response(gen(camera, "realsense_depth"),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/realsense_rgb')
def realsense_rgb():
    print('realsense_rgb')
    camera = DepthCameraRGB()
    return Response(gen(camera, "realsense_rgb"),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/lidar')
def lidar():
    print('lidar')
    camera = Lidarmid70()
    return Response(gen(camera, "lidar"),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/oakdepth')
def oakdepth():
    print('oak_depth')
    camera = OAKDPRO()
    return Response(gen(camera, "OAK-D"),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/toggle_recording', methods=['POST'])
def toggle_recording():
    global IS_RECORDING
    print('NOW RECORDING IS', IS_RECORDING)
    if IS_RECORDING:
        # stop_lidar()
        stop_depth()
    else:
        # start_lidar(LIDAR_CAMERA_POS_TXT, SAVE_DATA_STEM,
        #              LIDAR_VIS_MAX_POINTS, LIDAR_VIS_INTERVAL)
        start_depth()    
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
from detect_charuco import detectmarkers
#カメラオブジェクトから静止画を取得する
def gen(camera, camera_name=""):
    global IS_RECORDING
    while True:
        frame = camera.get_frame()
        if camera_name == "realsense_rgb":
            frame = detectmarkers(frame, IS_RECORDING=IS_RECORDING)
        if frame is not None:
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
    thremal_wide()
    thermal()
    realsense()
    realsense_rgb()
    oakdepth()
    # ip address を入力
    app.run(host=IP_ADDR, port=8888)

