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
PHOTO_DELAY = 60
n = 20  # Number of frames to take median of
previous_frames = None  # Holds numpy array of previous frames
difference = None
frames_captured = 0  # Keeps track of the total number of frames
difference_threshold = 15  # Threshold value for abs difference of current frame and median image
motion_threshold = 0.05  # Percent of pixels to determine that motion occurred
main_resolution = (1920, 1080)  # Resolution for image captured
lores_resolution = (640, 480)  # Resolution for preview window

if __name__ == '__main__':
    try:
        # Load environment variables
        load_dotenv(".env")
        account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL")
        default_credential = DefaultAzureCredential()

        # Create the BlobServiceClient object
        blob_service_client = BlobServiceClient(account_url, credential=default_credential)

        # Get the container
        container_name = os.environ.get("AZURE_STORAGE_CONTAINER_NAME")
        container_client = blob_service_client.get_container_client(container=container_name)
        print("Ready to write to blob")

        # Write blob to container
        # Generate unique filename
        blob_filename = str(uuid.uuid4())
        if USE_CAMERA_DATA:
            # Start camera
            picam2 = Picamera2()
            camera_config = picam2.create_still_configuration(main={"size": main_resolution},
                                                              lores={"size": lores_resolution}, display="lores")
            picam2.configure(camera_config)
            picam2.start()
            time.sleep(1)
            while True:
                frame = picam2.capture_array()
                gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                frames_captured += 1
                if previous_frames is None:
                    previous_frames = np.zeros((gray.shape[0], gray.shape[1], n))
                    previous_frames[:, :, 0] = gray
                    for i in range(1, n):
                        frame = picam2.capture_array()
                        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
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

                # Take action if certain percentage of pixels are 0
                if np.count_nonzero(difference == 0) > motion_threshold * np.size(difference):
                    print("Motion Detected")
                    if WRITE_TO_AZURE:
                        # Capture image to memory
                        data = io.BytesIO()
                        picam2.capture_file(data, format='jpeg')
                        # Write to blob storage
                        blob_client = container_client.upload_blob(name=blob_filename, data=data.getvalue())
                    else:
                        picam2.capture_file(os.path.join('local_output', blob_filename + '.jpg'))
            # Stop camera
            picam2.stop()
        if not USE_CAMERA_DATA:
            # For testing when not using the Raspberry Pi
            # Writes image from sample_data directory to blob storage
            with open(file=os.path.join('sample_data', 'image.jpg'), mode="rb") as data:
                blob_client = container_client.upload_blob(name=blob_filename, data=data)
        print("Blob write completed")

    except Exception as e:
        print(e)
