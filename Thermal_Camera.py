import cv2          #Opencv
import sys          #変数&関数
import datetime     #時刻
import os           #FILE&directory
from loguru import logger
import time
from base_camera import BaseCamera
from PIL import Image
from uvctypes import *
import time
import cv2
import numpy as np
try:
  from queue import Queue
except ImportError:
  from Queue import Queue
import platform
from setting import *
###################################################
## 定数定義
###################################################
#動画の格納パス
#ファイル名を時刻にするため時刻取得

os.makedirs(LOGDIR, exist_ok=True)
size = (160, 120)

#保存形式指定
size = (160, 120)                                            #画像サイズ(1280,720) (640,480)
logger.add(os.path.join(LOGDIR, "logtest.log"), rotation="1h")

##################################################
## UVC用の設定
##################################################
BUF_SIZE = 2
q = Queue(BUF_SIZE)

def py_frame_callback(frame, userptr):

  array_pointer = cast(frame.contents.data, POINTER(c_uint16 * (frame.contents.width * frame.contents.height)))
  data = np.frombuffer(
    array_pointer.contents, dtype=np.dtype(np.uint16)
  ).reshape(
    frame.contents.height, frame.contents.width
  )

  if frame.contents.data_bytes != (2 * frame.contents.width * frame.contents.height):
    return

  if not q.full():
    q.put(data)

PTR_PY_FRAME_CALLBACK = CFUNCTYPE(None, POINTER(uvc_frame), c_void_p)(py_frame_callback)

def ktof(val):
  return (1.8 * ktoc(val) + 32.0)

def ktoc(val):
  return (val - 27315) / 100.0

def raw_to_8bit(data):
  cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(data, 8, data)
  return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)

def display_temperature(img, val_k, loc, color):
  val = ktoc(val_k)
  cv2.putText(img,"{0:.1f} degF".format(val), loc, cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
  x, y = loc
  cv2.line(img, (x - 2, y), (x + 2, y), color, 1)
  cv2.line(img, (x, y - 2), (x, y + 2), color, 1)

###############################################
## main
###############################################

class Camera(BaseCamera):           #<--２箇所目
    ###################################################
    ## カメラ処理のメインメソッド
    ###################################################
    @staticmethod
    def frames():
        ctx = POINTER(uvc_context)()
        dev = POINTER(uvc_device)()
        devh = POINTER(uvc_device_handle)()
        ctrl = uvc_stream_ctrl()

        res = libuvc.uvc_init(byref(ctx), 0)
        if res < 0:
            logger.error("uvc_init error")
            exit(1)

        try:
            res = libuvc.uvc_find_device(ctx, byref(dev), PT_USB_VID, PT_USB_PID, 0)
            if res < 0:
                logger.error("uvc_find_device error")
                exit(1)

            try:
                res = libuvc.uvc_open(dev, byref(devh))
                if res < 0:
                    logger.error("uvc_open error")
                    exit(1)

                logger.info("device opened!")

                print_device_info(devh)
                print_device_formats(devh)

                frame_formats = uvc_get_frame_formats_by_guid(devh, VS_FMT_GUID_Y16)
                if len(frame_formats) == 0:
                    logger.error("device does not support Y16")
                    exit(1)

                libuvc.uvc_get_stream_ctrl_format_size(devh, byref(ctrl), UVC_FRAME_FORMAT_Y16,
                    frame_formats[0].wWidth, frame_formats[0].wHeight, int(1e7 / frame_formats[0].dwDefaultFrameInterval)
                )

                res = libuvc.uvc_start_streaming(devh, byref(ctrl), PTR_PY_FRAME_CALLBACK, None, 0)
                if res < 0:
                    logger.error("uvc_start_streaming failed: {0}".format(res))
                    exit(1)

                try:
                    while True:
                        # 保存先の設定
                        dt_now = datetime.datetime.now()
                        yyyymmdd = dt_now.strftime('%Y%m%d')
                        hh = dt_now.strftime('%H00')
                        file_name = dt_now.strftime('%Y%m%d-%H%M%S_%f')
                        save_dir = os.path.join(FOLODER, yyyymmdd, hh)
                        os.makedirs(save_dir, exist_ok=True)
                        output_path = os.path.join(save_dir, file_name + '.png')
                        # 生データ取得と保存
                        data = q.get(True, 500)
                        if data is None:
                            continue
                        frame = cv2.resize(data[:,:], (size))  #保存形式指定のフレーム
                        cv2.imwrite(output_path, frame)
                        logger.info(f"SAVE {output_path}")

                        # 画像表示側への処理
                        frame = raw_to_8bit(frame)
                        frame = cv2.resize(frame,(640, 480))
                        frame = cv2.applyColorMap(frame, cv2.COLORMAP_INFERNO)
                        yield cv2.imencode('.jpg', frame)[1].tobytes()
                finally:
                    logger.error(f"Fail {output_path}")
                    libuvc.uvc_stop_streaming(devh)
            finally:
                logger.info("done")
                libuvc.uvc_unref_device(dev)
        finally:
            libuvc.uvc_exit(ctx)