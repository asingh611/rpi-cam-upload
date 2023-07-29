import cv2
import numpy as np
import camera_logging
import camera_operations
from datetime import datetime


# Generate array of previous images
# This set of images will be used to generate an image to compare to the current frame
def create_history_array(picam2_obj, n):
    history_array = None
    for i in range(0, n):
        main_img, lores_img, gray_img = camera_operations.capture_current_image(picam2_obj)
        if history_array is None:
            history_array = np.zeros((gray_img.shape[0], gray_img.shape[1], n))
        history_array[:, :, i] = gray_img
    return main_img, lores_img, gray_img, history_array


# Based on the previous frames and the current frame, determine if motion was detected
def detect_motion(history_array, current_image, difference_threshold, motion_threshold):
    # Take the median
    median_image = np.median(history_array, axis=2)

    # Take the absolute difference between the median and current frame
    difference_img = np.abs(median_image - current_image)

    # Only show pixels where the difference between the median image and current frame is higher than the threshold
    difference_img[difference_img <= difference_threshold] = 1
    difference_img[difference_img > difference_threshold] = 0  # motion

    # Morphological operation to clean up image
    kernel = np.ones((3, 3), np.uint8)
    difference_dilation = cv2.dilate(difference_img, kernel, iterations=1)

    current_motion_time = datetime.now()

    # Take action if certain percentage of pixels are 0 (higher than the threshold)
    count_nonzero = np.count_nonzero(difference_dilation == 0)
    if count_nonzero > motion_threshold * np.size(difference_dilation):
        camera_logging.output_log(camera_logging.EVENT_MOTION_DETECTED,
                                             ["Number of changed pixels: " + str(count_nonzero),
                                              " Current motion threshold: " + str(motion_threshold)])
        return True, difference_img, current_motion_time
    return False, difference_img, current_motion_time


# Checks if there has been enough time since the last time motion was detected
# Prevents too many images from being saved
def enough_time_since_motion(last_motion_time, time_threshold, current_motion_time):
    motion_time_difference = current_motion_time - last_motion_time
    if motion_time_difference.seconds > time_threshold:
        return True
    return False
