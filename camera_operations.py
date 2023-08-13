from picamera2 import Picamera2
import time
from datetime import datetime, timedelta
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
    picam2_start.configure(camera_config)
    picam2_start.start()
    time.sleep(1)
    camera_logging.output_log(camera_logging.EVENT_CAMERA_STARTED, ["Resolution: " + str(MAIN_RESOLUTION)])
    return picam2_start


# Capture current frame and return results from main resolution stream and a cropped grayscale version
def capture_current_image(picam2_obj):
    img_main = picam2_obj.capture_array()
    img_gray = cv2.cvtColor(img_main, cv2.COLOR_BGR2GRAY)
    img_gray_resized = cv2.resize(img_main, LORES_RESOLUTION)[FOCUS_REGION_ROW_START:FOCUS_REGION_ROW_END,
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


# Function to check if it is currently outside the camera's operating hours
def check_bedtime(current_time):
    # If it's too late in the day
    if current_time.hour > END_HOUR:
        restart_time = (current_time + timedelta(days=1)).replace(hour=START_HOUR, minute=0)
    # If it's too early in the morning
    elif current_time.hour < START_HOUR:
        restart_time = current_time.replace(hour=START_HOUR, minute=0)
    # Otherwise we're good to proceed
    else:
        return False, None

    return True, restart_time


# Operations to perform when the camera goes to sleep
def go_to_sleep(current_time, restart_time):
    sleep_for = (restart_time - current_time).seconds
    camera_logging.output_log(camera_logging.EVENT_CAMERA_SLEEP)
    time.sleep(sleep_for)
    camera_logging.output_log(camera_logging.EVENT_CAMERA_WAKE)