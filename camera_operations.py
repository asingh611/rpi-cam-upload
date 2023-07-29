from picamera2 import Picamera2
import time
import cv2
import camera_logging

MAIN_RESOLUTION = (640, 480)  # Resolution for image captured
LORES_RESOLUTION = (160, 120)  # Resolution for preview window

# Range of pixels in the image to focus on for motion detection (area of the image where the bird seeds are)
# These values are constant as long as the camera isn't moved
x_1, x_2, y_1, y_2 = (50, 110, 15, 150)


# Start the Raspberry Pi camera
def start_camera():
    # Start camera
    picam2_start = Picamera2()
    camera_config = picam2_start.create_still_configuration(main={"size": MAIN_RESOLUTION},
                                                      lores={"size": LORES_RESOLUTION, "format": "YUV420"},
                                                      display="lores")
    picam2_start.configure(camera_config)
    picam2_start.start()
    time.sleep(1)
    camera_logging.output_log(camera_logging.EVENT_CAMERA_STARTED, ["Resolution: " + str(MAIN_RESOLUTION)])
    return picam2_start


# Capture current frame and return results from both resolution streams and a cropped grayscale version of lores
def capture_current_image(picam2_obj):
    (img_main, img_lores), img_metadata = picam2_obj.capture_arrays(["main", "lores"])
    img_gray = cv2.cvtColor(img_lores, cv2.COLOR_YUV420p2GRAY)[x_1:x_2, y_1:y_2]
    # camera_logging.output_log(camera_logging.EVENT_IMAGE_CAPTURED)
    return img_main, img_lores, img_gray
