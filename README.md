# thermal_monitoring

## 温度のRAW画像取得方法

0. libuvcインストール前の準備
```
$ apt-get install libusb-1.0-0-dev
$ apt-get install cmake
```

1. libucvのインストール
```
(公式はこちらを参照しているがraspiだと動かなかった...)
$ git clone https://github.com/groupgets/libuvc
(こちらでも動くのでいろいろ試して無理ならこちらを試してもいい)
$  git clone https://github.com/libuvc/libuvc

# 以下はどちらをcloneしても同じ流れ
git clone https://github.com/libuvc/libuvc
cd libuvc
mkdir build
cd build
cmake ..
make && sudo make install
```

2. 実行
```
python3 get_raw.py 
```
→ test.pngにグレー画像と、最大値と最小値についてのポイントが保存

### 困ったときは
1
```
Error: could not find libuvc
```
→ libuvc.soが認識されてないようです。
`./libuvc/build/libuvc.so`があるはずなので、以下コマンドでカレントディレクトリにリンクを張る
```
ln -s ./libuvc/build/libuvc.so
```

2
```
uvc_open error
```
[参考サイト](https://github.com/groupgets/purethermal1-uvc-capture/issues/7)にあるようにwebカメラの権限が悪い可能性がある。
```
$ lsusb
Bus 001 Device 006: ID 1e4e:0100 Cubeternet WebCam ← でDevice Noを把握
Bus 001 Device 004: ID 0424:7800 Microchip Technology, Inc. (formerly SMSC) 
Bus 001 Device 003: ID 0424:2514 Microchip Technology, Inc. (formerly SMSC) USB 2.0 Hub
Bus 001 Device 002: ID 0424:2514 Microchip Technology, Inc. (formerly SMSC) USB 2.0 Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

$ find /dev/bus/usb/*/* -exec ls -l {} \;
crw-rw-r-- 1 root root 189, 0 Sep  2 12:17 /dev/bus/usb/001/001
crw-rw-r-- 1 root root 189, 1 Sep  2 12:17 /dev/bus/usb/001/002
crw-rw-r-- 1 root root 189, 2 Sep  2 12:17 /dev/bus/usb/001/003
crw-rw-r-- 1 root root 189, 3 Sep  2 12:17 /dev/bus/usb/001/004
crw-rw-r-- 1 root root 189, 5 Sep  6 17:24 /dev/bus/usb/001/006  ←  該当デバイスの権限を変更

$ sudo chmod 666 /dev/bus/usb/001/006

$ find /dev/bus/usb/*/* -exec ls -l {} \;
crw-rw-r-- 1 root root 189, 0 Sep  2 12:17 /dev/bus/usb/001/001
crw-rw-r-- 1 root root 189, 1 Sep  2 12:17 /dev/bus/usb/001/002
crw-rw-r-- 1 root root 189, 2 Sep  2 12:17 /dev/bus/usb/001/003
crw-rw-r-- 1 root root 189, 3 Sep  2 12:17 /dev/bus/usb/001/004
crw-rw-rw- 1 root root 189, 5 Sep  6 17:36 /dev/bus/usb/001/006  ←  こうなってればok
```