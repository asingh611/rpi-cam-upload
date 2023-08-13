from datetime import datetime
from camera_constants import *

EVENT_CAMERA_STARTED = "Camera Started"
EVENT_CAMERA_STOPPED = "Camera Stopped"
EVENT_IMAGE_CAPTURED = "Image Captured"
EVENT_MOTION_DETECTED = "Motion Detected"
EVENT_BLOBSERVICE_STARTED = "Connected to Azure Blob Service"
EVENT_IMAGE_WRITTEN_LOCAL = "Image Saved Locally"
EVENT_IMAGE_WRITTEN_CLOUD = "Image Saved To Cloud"
EVENT_IMAGE_WRITE_SKIP = "Skipping image write"


# Method to generate the output for an event that would be written locally
def generate_local_log_output(event, additional_data=None):
    additional_data_string = ""
    if additional_data is not None:
        for data in additional_data:
            additional_data_string += data + " | "

    current_datetime = datetime.now()

    return "{} | {} | {}".format(current_datetime, event, additional_data_string)


# Wrapper method for outputting to log
def output_log(event, additional_data=None):
    if LOG_CONSOLE:
        output_log_to_console(event, additional_data)
    if LOG_FILE:
        output_log_to_file(event, additional_data)


# Output log event to the console
def output_log_to_console(event, additional_data=None):
    print(generate_local_log_output(event, additional_data))


# Output log event to a log file
def output_log_to_file(event, additional_data=None):
    with open(LOG_FILE_NAME, 'a') as f:
        f.write(generate_local_log_output(event, additional_data) + "\n")

