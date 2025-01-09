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
以下の場合, 6番
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
2. settings.pyの line 10を変更
```
THREMAL_CAMERA_WIDE_ID = 6
```

### Lidar
1. Lidar画像のカメラポジションを決定する
  1-1. 点群を5秒間サンプリングする -> 複数のcsvが生成される 
```
cd ./Livox-SDK/build/sample_cc/point_cloud
rm -rf *.csv  # フォルダ内に点群csvが残っているとうまくいかないのでいったん削除
./sampling    # 5秒間のcsvファイルが複数作成される
```
  1-2. png画像として保存するカメラ位置を決定する
```
./save_camera_pos ./
# -> マウスでカメラ位置を調整. 位置が決まったらウィンドウを×ボタンで閉じる 
# -> "camera_position.txt" が生成される
```
   1-3. うまく画像が生成できるかテスト (うまくいかなければ1-2に戻る)
```
./screen_shot ./
``` 

2. setting.py line 6 を書き換えてカメラ位置を反映させる (初期設定では生成されたカメラ位置が記録されたtxtファイル)
```
LIDAR_CAMERA_POS_TXT = "/home/srv-admin/monitoring/Livox-SDK/build/sample_cc/point_cloud/camera_position.txt"
``` 

3. その他設定項目をいじりたいときはsetting.pyを変える
```
IP_ADDR = "192.168.0.181" # flaskのサーバーのアドレス
# IP_ADDR = "127.0.0.1"  
FPS = 9 # 使わない

SAVE_DATA_STEM = "/home/srv-admin/monitoring/ssd/test/" # 生成されたデータを保存するパス. その中に様々なデータが保存される 
LIDAR_CAMERA_POS_TXT = "/home/srv-admin/monitoring/Livox-SDK/build/sample_cc/point_cloud/camera_position.txt" # 点群画像を生成する際のカメラ位置を記録したテキストファイルの絶対パス
LIDAR_VIS_MAX_POINTS = 100000 # 点群画像を生成する際過去何回分のサンプリングを画像に含めるか. 多いほど点群の数は増えるが、昔の点も残ってしまう
LIDAR_VIS_INTERVAL = 1000 # Lidarが点群をサンプリングした時に何回サンプリングした後、画像を生成するかの頻度. ただし単位は(回)であるため特定の時間と対応しているわけではない
THREMAL_CAMERA_ID = 6 # その他usbカメラの番号. 追加したい場合はindex.htmlもいじって描画されるように変更する必要がある
THREMAL_CAMERA_WIDE_ID = 6 # PureThermal のusb番号
SAVE_FPS = 1 # OAK-D PRO のサンプリングFPS (1以外でやると画像の生成スピードと描画が追い付かなくなる)
```


## モニタリングシステムの実行
```
cd ./monitoring
python3 camera_server.py
-> move to displayed IP ADDR
```
"Start Recordng" をクリックする前は "Lidar" and "OAK-D Depth"の画像は映りません
(Lidar と OAK-D Depthは別プログラムrun_depth.sh, run_lidar.shを実行して生成されたpngを表示するようにしているため)

停止時は"Stop Recording"を押す. ただし、OAK-D Depthはすぐには止まらないのでしばらくまつ

## 生成されたファイルの内役
```
.
├── Lidar
│   ├── csv # Lidar の点群CSVファイル (ファイル名はUNIX時間)
│   └── png # Lidar のスクリーンショット画像 (ファイル名はUNIX時間)
├── OAK-D
│   ├── bbox # OAK-D PRO 物体検出結果(csv)
│   ├── color # OAK-D PRO のRGB画像
│   ├── depth # OAK-D PRO のDepth (カラー画像)
│   └── depthRaw # OAK-D PRO のDepth (.npy)
├── realsense_depth # RealSenseのDepth (.npy)
├── realsense_rgb # RealSenseのRGB画像
└── thermo_wide   # PureThermal
```
