import time
import uuid
from datetime import datetime, timedelta
import camera_logging
import camera_operations
import camera_motion
import image_write
from camera_constants import *
import camera_objdetect
import threading
import os

if __name__ == '__main__':
    try:
        container_client = None
        vision_client = None

        # Initialize connection for blob storage
        if WRITE_TO_AZURE:
            container_client = image_write.initialize_azure_connection()

        # Initialize connection for cognitive services
        if USE_AZURE_OBJECT_DETECTION:
            vision_client = camera_objdetect.initialize_azure_connection()

        # Ensure folders for writing images locally are available
        if WRITE_IMAGE_LOCALLY:
            image_write.create_local_write_folder()

        picam2 = None
        previous_frames = None  # Holds numpy array of previous frames
        frames_captured = 0  # Keeps track of the total number of frame
        blob_filename = str(uuid.uuid4())  # Generate unique filename
        last_motion_time = datetime.now() + timedelta(seconds=-TIME_BETWEEN_MOTION)  # When motion was last detected

        while True:
            # Start the camera for the first time
            if picam2 is None:
                picam2 = camera_operations.start_camera()

            # Check the time to see if it's within the hours it should be running
            # If it's past the camera's bedtime, sleep until the start time
            is_bedtime, restart_time = camera_operations.check_bedtime(datetime.now())
            if is_bedtime:
                camera_operations.go_to_sleep(datetime.now(), restart_time)
                # Reset previous frames array
                previous_frames = None
                frames_captured = 0

            # Initialize the array of N previous frames if needed
            if previous_frames is None:
                main, lores, gray, previous_frames = camera_motion.create_history_array(picam2, N)
                frames_captured += N

            # Otherwise, capture current image
            else:
                main, lores, gray = camera_operations.capture_current_image(picam2)
                frames_captured += 1

            # Determine if motion is detected
            motion_detected, difference, current_motion_time = camera_motion.detect_motion(previous_frames, gray,
                                                                                           DIFFERENCE_THRESHOLD,
                                                                                           MOTION_THRESHOLD)

            # Update the oldest frame in previous_frames with the latest image
            index_to_update = frames_captured % N
            previous_frames[:, :, index_to_update] = gray

            if motion_detected:
                # Calculate if it has been enough time since the last time motion was detected
                # This is to prevent multiple images of the same bird being captured
                if camera_motion.enough_time_since_motion(last_motion_time, current_motion_time, TIME_BETWEEN_MOTION):
                    # Use object detection if enabled
                    if USE_OBJECT_DETECTION:
                        # Run object detection on captured frame
                        # Start next loop iteration if no bird detected
                        if not camera_objdetect.bird_detected(main, vision_client):
                            continue

                    # Reset motion last detected time
                    last_motion_time = current_motion_time

                    # Write image file
                    if WRITE_TO_AZURE:
                        image_write.write_image_to_azure(container_client, picam2, blob_filename)
                    if WRITE_IMAGE_LOCALLY:
                        image_write.write_image_locally(picam2, blob_filename, difference, main, lores,
                                                        CAPTURE_NEW_IMAGE_ON_WRITE, LOCAL_OUTPUT_DEBUG_IMAGES)

                        # Generate new file name
                        blob_filename = str(uuid.uuid4())

                else:
                    camera_logging.output_log(camera_logging.EVENT_IMAGE_WRITE_SKIP)

    except Exception as e:
        print(e)

