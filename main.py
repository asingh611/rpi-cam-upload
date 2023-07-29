import uuid
from datetime import datetime, timedelta
import camera_logging
import camera_operations
import camera_motion
import image_write

###################
# Camera Options
###################
START_HOUR = 8  # Hour of the day to start camera
END_HOUR = 18  # Hour of the day to stop camera

###################
# Write Options
###################
WRITE_TO_AZURE = False  # Whether to write image to Azure
WRITE_IMAGE_LOCALLY = True  # Whether to write image locally
LOCAL_OUTPUT_DEBUG_IMAGES = True  # Output image representations of arrays used in determining motion
CAPTURE_NEW_IMAGE_ON_WRITE = True  # When performing a write operation, capture a new image

###################
# Motion Options
###################
N = 10  # Number of frames to take median of
DIFFERENCE_THRESHOLD = 15  # Threshold pixel value for abs difference of current frame and median image
MOTION_THRESHOLD = 0.10  # Percent of pixels to determine that motion occurred
TIME_BETWEEN_MOTION = 30  # Number of seconds to wait before trying to detect motion again


if __name__ == '__main__':
    try:
        # Initialize connection for blob storage
        if WRITE_TO_AZURE:
            container_client = image_write.initialize_azure_connection()

        # Ensure folders for writing images locally are available
        if WRITE_IMAGE_LOCALLY:
            image_write.create_local_write_folder()

        # Initialize some values
        picam2 = None
        previous_frames = None  # Holds numpy array of previous frames
        frames_captured = 0  # Keeps track of the total number of frame
        blob_filename = str(uuid.uuid4())  # Generate unique filename
        last_motion_time = datetime.now() + timedelta(seconds=-TIME_BETWEEN_MOTION)  # When motion was last detected

        while True:
            # Start the camera for the first time
            if picam2 is None:
                picam2 = camera_operations.start_camera()

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
                                                                      DIFFERENCE_THRESHOLD, MOTION_THRESHOLD)
            if motion_detected:
                # Calculate if it has been enough time since the last time motion was detected
                # This is to prevent multiple images of the same bird being captured
                if camera_motion.enough_time_since_motion(last_motion_time, current_motion_time, MOTION_THRESHOLD):
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

            # Finally, update the oldest frame in previous_frames with the latest image
            index_to_update = frames_captured % N
            previous_frames[:, :, index_to_update] = gray

    except Exception as e:
        print(e)
