from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import os
from picamera2 import Picamera2
import time
import uuid
import io
import cv2 as cv
import numpy as np

# Switch between choosing to upload file from test directory or from camera data
USE_CAMERA_DATA = True
WRITE_TO_AZURE = False
n = 10  # Number of frames to take median of
previous_frames = None  # Holds numpy array of previous frames
difference = None
frames_captured = 0  # Keeps track of the total number of frames
difference_threshold = 15  # Threshold value for abs difference of current frame and median image
motion_threshold = 0.02  # Percent of pixels to determine that motion occurred
main_resolution = (640, 480)  # Resolution for image captured
lores_resolution = (160, 120)  # Resolution for preview window

# Range of pixels in the image to focus on
x_1 = 50
x_2 = 110
y_1 = 15
y_2 = 150


def initialize_azure_connection():
    # Load environment variables
    load_dotenv(".env")
    account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL")
    default_credential = DefaultAzureCredential()

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient(account_url, credential=default_credential)

    # Get the container
    container_name = os.environ.get("AZURE_STORAGE_CONTAINER_NAME")
    return blob_service_client.get_container_client(container=container_name)


if __name__ == '__main__':
    try:
        # Initialize connection for blob storage
        if WRITE_TO_AZURE:
            container_client = initialize_azure_connection()

        # Generate unique filename
        blob_filename = str(uuid.uuid4())

        if USE_CAMERA_DATA:
            # Start camera
            picam2 = Picamera2()
            camera_config = picam2.create_still_configuration(main={"size": main_resolution},
                                                              lores={"size": lores_resolution, "format": "YUV420" }, display="lores")
            picam2.configure(camera_config)
            picam2.start()
            time.sleep(1)
            while True:
                # frame = picam2.capture_array()
                (main, lores), metadata = picam2.capture_arrays(["main", "lores"])
                # print("Image Captured")
                gray = cv.cvtColor(lores, cv.COLOR_YUV420p2GRAY)[x_1:x_2, y_1:y_2]
                frames_captured += 1
                if previous_frames is None:
                    previous_frames = np.zeros((gray.shape[0], gray.shape[1], n))
                    previous_frames[:, :, 0] = gray
                    for i in range(1, n):
                        # frame = picam2.capture_array()
                        (main, lores), metadata = picam2.capture_arrays(["main", "lores"])
                        gray = cv.cvtColor(lores, cv.COLOR_YUV420p2GRAY)[x_1:x_2, y_1:y_2]
                        previous_frames[:, :, i] = gray
                        frames_captured += 1
                # Take the median
                median_image = np.median(previous_frames, axis=2)

                # Take the absolute difference between the median and current frame
                difference = np.abs(median_image - gray)

                difference[difference <= difference_threshold] = 1
                difference[difference > difference_threshold] = 0  # motion

                # Update the oldest frame in previous_frames with the latest image
                index_to_update = frames_captured % n
                previous_frames[:, :, index_to_update] = gray
                # cv.imshow('threshold', difference)
                # print(np.count_nonzero(difference == 0))

                kernel = np.ones((3, 3), np.uint8)
                difference_dilation = cv.dilate(difference, kernel, iterations=1)

                # Take action if certain percentage of pixels are 0
                if np.count_nonzero(difference_dilation == 0) > motion_threshold * np.size(difference_dilation):
                    print("Motion Detected")
                    print(np.count_nonzero(difference_dilation == 0))
                    
                    if WRITE_TO_AZURE:
                        # Capture image to memory
                        data = io.BytesIO()
                        picam2.capture_file(data, format='jpeg')
                        # Write to blob storage
                        blob_client = container_client.upload_blob(name=blob_filename, data=data.getvalue())
                        print("Blob write completed")
                    else:
                        picam2.capture_file(os.path.join('local_output', blob_filename + '.jpg'))
                        # cv.imwrite(os.path.join('local_output', blob_filename + '.png'), main)
                        difference_normalize = cv.normalize(difference, dst=None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX)
                        cv.imwrite(os.path.join('local_output', "difference", blob_filename + '.png'), difference_normalize)
                        cv.imwrite(os.path.join('local_output', "lores", blob_filename + '.png'), lores)
                    blob_filename = str(uuid.uuid4())
            # Stop camera
            picam2.stop()
        if not USE_CAMERA_DATA:
            # For testing when not using the Raspberry Pi
            # Writes image from sample_data directory to blob storage
            with open(file=os.path.join('sample_data', 'image.jpg'), mode="rb") as data:
                blob_client = container_client.upload_blob(name=blob_filename, data=data)

    except Exception as e:
        print(e)
