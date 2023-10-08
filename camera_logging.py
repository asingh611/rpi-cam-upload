from datetime import datetime
from camera_constants import *
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient
import os

# TODO: Update logging events to objects with multiple properties (description, log level)
# TODO: Add minimum log level (to determine how verbose the logs should be)

EVENT_CAMERA_STARTED = "Camera Started"
EVENT_CAMERA_STOPPED = "Camera Stopped"
EVENT_IMAGE_CAPTURED = "Image Captured"
EVENT_MOTION_DETECTED = "Motion Detected"
EVENT_BLOBSERVICE_STARTED = "Connected to Azure Blob Service"
EVENT_IMAGE_WRITTEN_LOCAL = "Image Saved Locally"
EVENT_IMAGE_WRITTEN_CLOUD = "Image Saved To Cloud"
EVENT_IMAGE_WRITE_SKIP = "Skipping image write"
EVENT_CAMERA_SLEEP = "Camera Pausing - Going To Sleep"
EVENT_CAMERA_WAKE = "Camera Restarting - Waking from Sleep"
EVENT_AZURE_CV_CONNECTED = "Connected to Azure CV Service"
EVENT_OBJECT_DETECTED = "Object Detected"
EVENT_OBJECT_NOT_DETECTED = "Object Not Detected"
EVENT_AZURE_LOGGING_STARTED = "Connected to Azure Log Ingestion"


# Connect to Azure using environment variables loaded the .env file
def initialize_azure_connection():
    # Load environment variables
    load_dotenv(".env")

    endpoint = os.environ.get("AZURE_DATA_COLLECTION_ENDPOINT")
    credential = DefaultAzureCredential()
    logs_client = LogsIngestionClient(endpoint, credential)
    rule_id = os.environ.get('AZURE_LOGGING_DCR_ID')
    stream_name = os.environ.get('AZURE_LOGGING_STREAM_NAME')

    return logs_client, rule_id, stream_name


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


# Output log event to Azure
def output_log_to_azure(log_client, dcr, stream_name, event, additional_data=None):
    # TODO: Parse additional data and add it to body
    # TODO: Implement different log levels (currently all events set to 10)
    body = [{
        "TimeGenerated": str(datetime.now()),
        "EventName": event,
        "LogLevel": "10",
        "AdditionalData": ""
    }]
    log_client.upload(rule_id=dcr, stream_name=stream_name, logs=body)
