from datetime import datetime

EVENT_CAMERA_STARTED = "Camera Started"
EVENT_CAMERA_STOPPED = "Camera Stopped"
EVENT_IMAGE_CAPTURED = "Image Captured"
EVENT_MOTION_DETECTED = "Motion Detected"
EVENT_BLOBSERVICE_STARTED = "Connected to Azure Blob Service"
EVENT_IMAGE_WRITTEN_LOCAL = "Image Saved Locally"
EVENT_IMAGE_WRITTEN_CLOUD = "Image Saved To Cloud"


def output_log_to_console(event, additional_data=None):
    additional_data_string = ""
    if additional_data is not None:
        for data in additional_data:
            additional_data_string += data + " "

    current_datetime = datetime.now()

    print("{} {} {}".format(current_datetime, event, additional_data_string))

