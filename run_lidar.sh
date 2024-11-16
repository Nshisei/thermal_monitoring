#!/bin/bash

# 実行中のプロセスを管理するためのPIDファイル
PID_FILE="/tmp/mylidar.pid"

# 仮想ディスプレイ用のPIDファイル
XVFB_PID_FILE="/tmp/xvfb.pid"

# 実行するプログラムのパス
LIDAR_PROGRAM="./Livox-SDK/build/sample_cc/my_lidar/my_lidar"

if [ "$1" == "start" ]; then
    # プログラム開始
    if [ -f "$PID_FILE" ]; then
        echo "LiDAR is already running with PID $(cat $PID_FILE)"
        exit 1
    fi

    # 仮想ディスプレイ開始
    if [ ! -f "$XVFB_PID_FILE" ]; then
        echo "Starting virtual display..."
        Xvfb :99 -screen 0 1024x768x24 &
        XVFB_PID=$!
        echo $XVFB_PID > "$XVFB_PID_FILE"
        echo "Virtual display started with PID $XVFB_PID"
    else
        echo "Virtual display already running with PID $(cat $XVFB_PID_FILE)"
    fi

    # DISPLAY 環境変数を設定
    export DISPLAY=:99

    # 引数を受け取る
    CAMERA_PATH="$2"
    SAVE_DIR="$3"
    MAX_POINTS="$4"
    SCREENSHOT_INTERVAL="$5"

    # 必須引数のチェック
    if [ -z "$CAMERA_PATH" ] || [ -z "$SAVE_DIR" ] || [ -z "$MAX_POINTS" ] || [ -z "$SCREENSHOT_INTERVAL" ]; then
        echo "Usage: $0 start <camera_position_path> <save_dir_path> <max_points> <screenshot_interval>"
        exit 1
    fi

    # プログラムの起動
    $LIDAR_PROGRAM --camera "$CAMERA_PATH" --save_dir "$SAVE_DIR" --max_points "$MAX_POINTS" --interval "$SCREENSHOT_INTERVAL" &
    echo $! > "$PID_FILE"
    echo "LiDAR started with PID $(cat $PID_FILE)"

elif [ "$1" == "stop" ]; then
    # プログラム停止
    if [ -f "$PID_FILE" ]; then
        kill $(cat "$PID_FILE") && rm -f "$PID_FILE"
        echo "LiDAR stopped."
    else
        echo "LiDAR is not running."
    fi

    # 仮想ディスプレイ停止
    if [ -f "$XVFB_PID_FILE" ]; then
        kill $(cat "$XVFB_PID_FILE") && rm -f "$XVFB_PID_FILE"
        echo "Virtual display stopped."
    else
        echo "Virtual display is not running."
    fi

else
    echo "Usage: $0 start|stop <camera_position_path> <max_points> <screenshot_interval>"
    exit 1
fi
