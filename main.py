from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import os
from picamera2 import Picamera2
import time
import uuid
import io
import cv2
import numpy as np
import atexit
from datetime import datetime, timedelta
import camera_logging

WRITE_TO_AZURE = False  # Whether to write image locally or to Azure
WRITE_IMAGE_LOCALLY = True
LOCAL_OUTPUT_FOLDER = 'local_output'  # Local folder for where to output images
LOCAL_OUTPUT_DEBUG_IMAGES = True  # Output image representations of arrays used in determining motion
N = 10  # Number of frames to take median of
DIFFERENCE_THRESHOLD = 15  # Threshold value for abs difference of current frame and median image
MOTION_THRESHOLD = 0.10  # Percent of pixels to determine that motion occurred
MAIN_RESOLUTION = (640, 480)  # Resolution for image captured
LORES_RESOLUTION = (160, 120)  # Resolution for preview window
START_HOUR = 8  # Hour of the day to start camera
END_HOUR = 18  # Hour of the day to stop camera
TIME_BETWEEN_MOTION = 30  # Number of seconds to wait before trying to detect motion again
CAPTURE_NEW_IMAGE_ON_WRITE = True  # When performing a write operation, capture a new image

# Range of pixels in the image to focus on for motion detection (area of the image where the bird seeds are)
# These values are constant as long as the camera isn't moved
x_1, x_2, y_1, y_2 = (50, 110, 15, 150)


# Connect to Azure using environment variables loaded the .env file
def initialize_azure_connection():
    # Load environment variables
    load_dotenv(".env")
    account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL")
    default_credential = DefaultAzureCredential()

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient(account_url, credential=default_credential)

    # Get the container
    container_name = os.environ.get("AZURE_STORAGE_CONTAINER_NAME")
    blob_container_client = blob_service_client.get_container_client(container=container_name)
    camera_logging.output_log_to_console(camera_logging.EVENT_BLOBSERVICE_STARTED)
    return blob_container_client


# Start the Raspberry Pi camera
def start_camera(main_resolution, lores_resolution):
    # Start camera
    picam2_start = Picamera2()
    camera_config = picam2_start.create_still_configuration(main={"size": main_resolution},
                                                      lores={"size": lores_resolution, "format": "YUV420"},
                                                      display="lores")
    picam2_start.configure(camera_config)
    picam2_start.start()
    time.sleep(1)
    camera_logging.output_log_to_console(camera_logging.EVENT_CAMERA_STARTED, ["Resolution: " + str(main_resolution)])
    return picam2_start


# Capture current frame and return results from both resolution streams and a cropped grayscale version of lores
def capture_current_image(picam2_obj):
    (img_main, img_lores), img_metadata = picam2_obj.capture_arrays(["main", "lores"])
    img_gray = cv2.cvtColor(img_lores, cv2.COLOR_YUV420p2GRAY)[x_1:x_2, y_1:y_2]
    # camera_logging.output_log_to_console(camera_logging.EVENT_IMAGE_CAPTURED)
    return img_main, img_lores, img_gray


# Generate array of previous images
# This set of images will be used to generate an image to compare to the current frame
def create_history_array(picam2_obj, n):
    history_array = None
    for i in range(0, n):
        main_img, lores_img, gray_img = capture_current_image(picam2_obj)
        if history_array is None:
            history_array = np.zeros((gray_img.shape[0], gray_img.shape[1], n))
        history_array[:, :, i] = gray_img
    return main_img, lores_img, gray_img, history_array


# Based on the previous frames and the current frame, determine if motion was detected
def detect_motion(history_array, current_image):
    # Take the median
    median_image = np.median(history_array, axis=2)

    # Take the absolute difference between the median and current frame
    difference_img = np.abs(median_image - current_image)

    # Only show pixels where the difference between the median image and current frame is higher than the threshold
    difference_img[difference_img <= DIFFERENCE_THRESHOLD] = 1
    difference_img[difference_img > DIFFERENCE_THRESHOLD] = 0  # motion

    # Morphological operation to clean up image
    kernel = np.ones((3, 3), np.uint8)
    difference_dilation = cv2.dilate(difference_img, kernel, iterations=1)

    # Take action if certain percentage of pixels are 0 (higher than the threshold)
    count_nonzero = np.count_nonzero(difference_dilation == 0)
    if count_nonzero > MOTION_THRESHOLD * np.size(difference_dilation):
        camera_logging.output_log_to_console(camera_logging.EVENT_MOTION_DETECTED,
                                             ["Number of changed pixels: " + str(count_nonzero),
                                              " Current motion threshold: " + str(MOTION_THRESHOLD)])
        return True, difference_img
    return False, difference_img


# Method to handle writing to Azure
def write_image_to_azure(azure_container_client, picam2_obj, filename):
    # Capture image to memory
    data = io.BytesIO()
    picam2_obj.capture_file(data, format='jpeg')
    # Write to blob storage
    blob_client = azure_container_client.upload_blob(name=filename + '.jpg', data=data.getvalue())
    camera_logging.output_log_to_console(camera_logging.EVENT_IMAGE_WRITTEN_CLOUD, ["Filename: " + filename])


# Method for handling writing image locally
def write_image_locally(picam2_obj, filename, difference_img, main_img, lores_img):
    if CAPTURE_NEW_IMAGE_ON_WRITE:
        picam2_obj.capture_file(os.path.join(LOCAL_OUTPUT_FOLDER, filename + '.jpg'))
    else:
        cv2.imwrite(os.path.join(LOCAL_OUTPUT_FOLDER, filename + '.jpg'), main_img)

    if LOCAL_OUTPUT_DEBUG_IMAGES:
        difference_normalize = cv2.normalize(difference_img, dst=None,
                                             alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        cv2.imwrite(os.path.join(LOCAL_OUTPUT_FOLDER, "difference", filename + '.png'),
                    difference_normalize)
        cv2.imwrite(os.path.join(LOCAL_OUTPUT_FOLDER, "lores", filename + '.png'), lores_img)
    camera_logging.output_log_to_console(camera_logging.EVENT_IMAGE_WRITTEN_LOCAL, ["Filename: " + filename])


# Method for creating folder directories for local image write if they don't
def create_local_write_folder():
    folder_date = datetime.now()
    folder_name = folder_date.strftime('%Y%m%d')
    os.makedirs(os.path.join(LOCAL_OUTPUT_FOLDER, folder_name, "difference"), True)
    os.makedirs(os.path.join(LOCAL_OUTPUT_FOLDER, folder_name, "lores"), True)


if __name__ == '__main__':
    try:
        # Initialize connection for blob storage
        if WRITE_TO_AZURE:
            container_client = initialize_azure_connection()

        # Ensure folders for writing images locally are available
        if WRITE_IMAGE_LOCALLY:
            create_local_write_folder()

        # Generate unique filename
        blob_filename = str(uuid.uuid4())

        picam2 = None
        previous_frames = None  # Holds numpy array of previous frames
        frames_captured = 0  # Keeps track of the total number of frame
        last_motion_time = datetime.now() + timedelta(seconds=-TIME_BETWEEN_MOTION) # Tracks when motion was last detected

        while True:
            # Start the camera for the first time
            if picam2 is None:
                picam2 = start_camera(MAIN_RESOLUTION, LORES_RESOLUTION)

            # Initialize the array of N previous frames if needed
            if previous_frames is None:
                main, lores, gray, previous_frames = create_history_array(picam2, N)
                frames_captured += N

            # Otherwise, capture current image
            else:
                main, lores, gray = capture_current_image(picam2)
                frames_captured += 1

            # Determine if motion is detected
            motion_detected, difference = detect_motion(previous_frames, gray)
            if motion_detected:
                # Calculate if it has been enough time since the last time motion was detected
                # This is to prevent multiple images of the same bird being captured
                current_motion_time = datetime.now()
                motion_time_difference = current_motion_time - last_motion_time
                if motion_time_difference.seconds > TIME_BETWEEN_MOTION:
                    last_motion_time = current_motion_time
                    # Write image file
                    if WRITE_TO_AZURE:
                        write_image_to_azure(container_client, picam2, blob_filename)
                    if WRITE_IMAGE_LOCALLY:
                        write_image_locally(picam2, blob_filename, difference, main, lores)

                    # Generate new file name
                    blob_filename = str(uuid.uuid4())

                else:
                    camera_logging.output_log_to_console(camera_logging.EVENT_IMAGE_WRITE_SKIP)

            # Finally, update the oldest frame in previous_frames with the latest image
            index_to_update = frames_captured % N
            previous_frames[:, :, index_to_update] = gray

    except Exception as e:
        print(e)
