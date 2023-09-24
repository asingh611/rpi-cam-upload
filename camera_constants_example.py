from datetime import datetime

##########################
# Camera Options
##########################
START_HOUR = 8  # Hour of the day to start camera
END_HOUR = 18  # Hour of the day to stop camera
CAMERA_MODE = "Single-Still"
MAIN_RESOLUTION = (800, 600)  # Resolution for image captured
LORES_RESOLUTION = (160, 120)  # Resolution for preview window
# Range of pixels in the image to focus on for motion detection (crops original image)
FOCUS_REGION_ROW_START, FOCUS_REGION_ROW_END = (int(0.4*LORES_RESOLUTION[1]), LORES_RESOLUTION[1])
FOCUS_REGION_COL_START, FOCUS_REGION_COL_END = (0, LORES_RESOLUTION[0])

##########################
# Write Options
##########################
WRITE_TO_AZURE = False  # Whether to write image to Azure
WRITE_IMAGE_LOCALLY = True  # Whether to write image locally
LOCAL_OUTPUT_DEBUG_IMAGES = True  # Output image representations of arrays used in determining motion
CAPTURE_NEW_IMAGE_ON_WRITE = True  # When performing a write operation, capture a new image
LOCAL_OUTPUT_FOLDER = 'local_output'  # Local folder for where to output images
LOCAL_OUTPUT_SUBFOLDER = datetime.now().strftime('%Y%m%d')  # e.g. 20230729

##########################
# Motion Options
##########################
N = 10  # Number of frames to take median of
DIFFERENCE_THRESHOLD = 15  # Threshold pixel value for abs difference of current frame and median image
MOTION_THRESHOLD = 0.10  # Percent of pixels to determine that motion occurred
TIME_BETWEEN_MOTION = 30  # Number of seconds to wait before trying to detect motion again

##########################
# Detection Model Options
##########################
USE_OBJECT_DETECTION = True
MODEL_FOLDER = "model"
MODEL_CONFIGURATION_FILENAME = "yolov3.cfg"
MODEL_WEIGHTS_FILENAME = "yolov3.weights"
MODEL_CLASSNAME_FILENAME = "coco.names"
MODEL_CONFIDENCE_THRESHOLD = 0.75

##########################
# Log Options
##########################
LOG_FILE_NAME = "camera_events.log"  # Local file name for log file
LOG_CONSOLE, LOG_FILE, LOG_AZURE = (True, True, False)  # Where to write logs to
