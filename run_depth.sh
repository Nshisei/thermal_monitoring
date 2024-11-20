#!/bin/bash

# 実行中のプロセスを管理するためのPIDファイル
PID_FILE="/tmp/mydepth.pid"

# 実行するプログラムのパス
DEPTH_PROGRAM="./depthai/depthai_demo.py"  # OAK-D PROの実行ファイル

if [ "$1" == "start" ]; then
    # プログラム開始
    if [ -f "$PID_FILE" ]; then
        echo "Depth camera is already running with PID $(cat $PID_FILE)"
        exit 1
    fi

    # プログラムの起動
    $DEPTH_PROGRAM

elif [ "$1" == "stop" ]; then
    # プログラム停止

    PROCESS_NAME="/home/srv-admin/anaconda3/envs/depth-ai/bin/python3 depthai_demo.py --noSupervisor --guiType qt"
    #for test env
    # PROCESS_NAME="/home/srv-admin/anaconda3/envs/test/bin/python3 depthai_demo.py --noSupervisor --guiType qt"

    # プロセスのPIDを取得
    PIDS=$(ps aux | grep "$PROCESS_NAME" | grep -v "grep" | awk '{print $2}')

    # プロセスが存在するかチェック
    if [ -z "$PIDS" ]; then
    echo "No process found with name: $PROCESS_NAME"
    else
    echo "PIDs matching '$PROCESS_NAME':"
    kill "$PIDS"
    echo "Depth camera stopped."
    fi

else
    echo "Usage: $0 start|stop <camera_position_path> <save_dir_path> <frame_rate> <resolution>"
    exit 1
fi
