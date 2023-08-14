from picamera2 import Picamera2
import libcamera
import time
import cv2
import camera_logging
from camera_constants import *


# Start the Raspberry Pi camera
def start_camera():
    # Start camera
    picam2_start = Picamera2()
    # Default to single stream still image configuration if none defined
    if CAMERA_MODE == "Multi-Still":
        camera_config = picam2_start.create_still_configuration(main={"size": MAIN_RESOLUTION},
                                                          lores={"size": LORES_RESOLUTION, "format": "YUV420"},
                                                          display="lores")
    else:
        camera_config = picam2_start.create_still_configuration(main={"size": MAIN_RESOLUTION})
    camera_config["transform"] = libcamera.Transform(hflip=1, vflip=1)
    picam2_start.configure(camera_config)
    picam2_start.start()
    time.sleep(1)
    camera_logging.output_log(camera_logging.EVENT_CAMERA_STARTED, ["Resolution: " + str(MAIN_RESOLUTION)])
    return picam2_start


# Capture current frame and return results from main resolution stream and a cropped grayscale version
def capture_current_image(picam2_obj):
    img_main = picam2_obj.capture_array()
    img_gray = cv2.cvtColor(img_main, cv2.COLOR_BGR2GRAY)
    img_gray_resized = cv2.resize(img_gray, LORES_RESOLUTION)[FOCUS_REGION_ROW_START:FOCUS_REGION_ROW_END,
               FOCUS_REGION_COL_START:FOCUS_REGION_COL_END]
    # camera_logging.output_log(camera_logging.EVENT_IMAGE_CAPTURED)
    return img_main, img_gray_resized, img_gray_resized


# Capture current frame and return results from both resolution streams and a cropped grayscale version of lores
def capture_current_image_multistream(picam2_obj):
    (img_main, img_lores), img_metadata = picam2_obj.capture_arrays(["main", "lores"])
    img_gray = cv2.cvtColor(img_lores, cv2.COLOR_YUV420p2GRAY)[FOCUS_REGION_ROW_START:FOCUS_REGION_ROW_END,
               FOCUS_REGION_COL_START:FOCUS_REGION_COL_END]
    # camera_logging.output_log(camera_logging.EVENT_IMAGE_CAPTURED)
    return img_main, img_lores, img_gray
