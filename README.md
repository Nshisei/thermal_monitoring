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
echo "source ~/anaconda3/etc/profile.d/conda.sh" >> ~/.zshrc
source .zshrc
```

### create virtural environment
```
conda create -n depth-ai python=3.9
conda activate depth-ai
```
Confirm ```python --version``` returns Python 3.9.0


## depthai
<span style="color: red;">From here, run on a conda environment.</span>

```
python -m pip install -r reqirements.txt
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
1. Check Thermal device number
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
2. Change "Camera.py" line 25
```
def frames():
    print("camera_id", 0)
    cap = cv2.VideoCapture(6) # change caputure device number
```

### Lidar
1. Setting viewer potision
  1-1. sampling point cloud in 5s -> create csv files 
```
cd ./Livox-SDK/build/sample_cc/point_cloud
rm -rf *.csv
./sampling
```
  1-2. determining viewer point
```
./save_camera_position ./
-> if decided close window
-> then made "camera_position.txt"
```
   1-3. run screen_shot to check camera position
   if you alter position, back to 1-2
```
./screen_shot ./
``` 

2. reflect camera position to setting.py
Change setting.py line 6
```
LIDAR_CAMERA_POS_TXT = "/home/srv-admin/monitoring/lidar_position.txt"
``` 

3. if you want to change other parameters
```

```