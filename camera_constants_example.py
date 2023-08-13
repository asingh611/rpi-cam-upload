from datetime import datetime

###################
# Camera Options
###################
START_HOUR = 8  # Hour of the day to start camera
END_HOUR = 18  # Hour of the day to stop camera
MAIN_RESOLUTION = (800, 600)  # Resolution for image captured
LORES_RESOLUTION = (160, 120)  # Resolution for preview window
x_1, x_2, y_1, y_2 = (50, 110, 15, 150)  # Range of pixels in the image to focus on for motion detection

###################
# Write Options
###################
WRITE_TO_AZURE = False  # Whether to write image to Azure
WRITE_IMAGE_LOCALLY = True  # Whether to write image locally
LOCAL_OUTPUT_DEBUG_IMAGES = True  # Output image representations of arrays used in determining motion
CAPTURE_NEW_IMAGE_ON_WRITE = True  # When performing a write operation, capture a new image
LOCAL_OUTPUT_FOLDER = 'local_output'  # Local folder for where to output images
LOCAL_OUTPUT_SUBFOLDER = datetime.now().strftime('%Y%m%d')  # e.g. 20230729

###################
# Motion Options
###################
N = 10  # Number of frames to take median of
DIFFERENCE_THRESHOLD = 15  # Threshold pixel value for abs difference of current frame and median image
MOTION_THRESHOLD = 0.10  # Percent of pixels to determine that motion occurred
TIME_BETWEEN_MOTION = 30  # Number of seconds to wait before trying to detect motion again

###################
# Motion Options
###################
LOG_FILE_NAME = "camera_events.log"  # Local file name for log file
LOG_CONSOLE, LOG_FILE, LOG_AZURE = (True, True, False)  # Where to write logs to
