import cv2
import numpy as np

ARUCO_DICT = cv2.aruco.DICT_6X6_250
SQUARES_VERTICALLY = 2
SQUARES_HORIZONTALLY = 3
def detectmarkers(frame, IS_RECORDING=False):
    if IS_RECORDING:
        return frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    marker_coners, marker_ids, _ = cv2.aruco.detectMarkers(gray, dict)
    if marker_ids is not None:
        if len(marker_ids) > 0:
            cv2.aruco.drawDetectedMarkers(frame, marker_coners, marker_ids) 
    return frame
