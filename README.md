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
(depth-ai)
cd depthai
python install_requirements.py
```


## Livox-SDK
```
(depth-ai)
cd Livox-SDK
cd build && cmake ..
make
sudo make install
```



### Permmision
```
(depth-ai)
sudo chmod +x ./run_lidar.sh
./run_lidar.sh
```

