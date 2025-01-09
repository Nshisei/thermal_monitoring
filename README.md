# monitoring 


## Environment
Ubuntu 18.04
python 3.7.5

OAK-D-PRO
Realsense D435i
Livox MID-70
Lepton 


## conda
### installation
```
sudo mkdir /tmp
cd /tmp
curl -O https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh
bash Anaconda3-2020.02-Linux-x86_64.sh
cd ~
echo "source ~/anaconda3/etc/profile.d/conda.sh" >> ~/.bashrc
source .bashrc
```

### create virtural environment
```
conda create -n depth-ai python=3.9
conda activate depth-ai
```
Confirm ```python --version``` returns Python 3.9


## depthai
<span style="color: red;">From here, run on a conda environment.</span>

```
git clone --recursive https://github.com/Nshisei/thermal_monitoring.git -b monitoring
cd thermal_monitoring
python -m pip install -r requirements.txt
```


## Livox-SDK
```
cd Livox-SDK
cd build && cmake ..
make
sudo make install
```



### Permmision
```
sudo chmod +x ./run_lidar.sh
sudo chmod +x ./run_depth.sh
```

# How to use
## Prepare devices
### Thremal or other camera devices
1. サーマルカメラのデバイス番号を確認する
```
v4l2-ctl --list-devices
```
In this case, 6
```
Intel(R) RealSense(TM) Depth Ca (usb-0000:00:14.0-5):
        /dev/video0
        /dev/video1
        /dev/video2
        /dev/video3
        /dev/video4
        /dev/video5

PureThermal (fw:v1.3.0): PureTh (usb-0000:00:14.0-7):
        /dev/video6
        /dev/video7

```
2. "Camera.py" line 25 を変更する
```
def frames():
    print("camera_id", 0)
    cap = cv2.VideoCapture(6) # change caputure device number
```

### Lidar
1. Setting viewer potision
  1-1. 点群を5秒間サンプリングする -> 複数のcsvが生成される 
```
cd ./Livox-SDK/build/sample_cc/point_cloud
rm -rf *.csv
./sampling
```
  1-2. png画像として保存するカメラ位置を決定する
```
./save_camera_pos ./
# -> マウスでカメラ位置を調整. 位置が決まったらウィンドウを×ボタンで閉じる 
# -> "camera_position.txt" が生成される
```
   1-3. run screen_shot to check camera position
   if you alter position, back to 1-2
```
./screen_shot ./
``` 

2. カメラ位置をsetting.py に反映させる
Change setting.py line 6
```
LIDAR_CAMERA_POS_TXT = "/home/srv-admin/monitoring/lidar_position.txt"
``` 

3. 設定項目をいじりたいときはsetting.pyを変える (e.g. save data path, lidar sampling interval...)
change setting.py

## モニタリングシステムの実行
```
cd ./monitoring
python3 camera_server.py
-> move to displayed IP ADDR
```
"Start Recordng" をクリックする前は "Lidar" and "OAK-D Depth"の画像は映りません
(Lidar と OAK-D Depthは別プログラムrun_depth.sh, run_lidar.shを実行して生成されたpngを表示するようにしているため)

停止時は"Stop Recording"を押す. ただし、OAK-D Depthはすぐには止まらないのでしばらくまつ
