from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import os
import io
import cv2
from datetime import datetime
import camera_logging

LOCAL_OUTPUT_FOLDER = 'local_output'  # Local folder for where to output images
LOCAL_OUTPUT_SUBFOLDER = datetime.now().strftime('%Y%m%d')  # e.g. 20230729


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
    camera_logging.output_log(camera_logging.EVENT_BLOBSERVICE_STARTED)
    return blob_container_client


# Method to handle writing to Azure
def write_image_to_azure(azure_container_client, picam2_obj, filename):
    # Capture image to memory
    data = io.BytesIO()
    picam2_obj.capture_file(data, format='jpeg')
    # Write to blob storage
    blob_client = azure_container_client.upload_blob(name=filename + '.jpg', data=data.getvalue())
    camera_logging.output_log(camera_logging.EVENT_IMAGE_WRITTEN_CLOUD, ["Filename: " + filename])


# Method for handling writing image locally
def write_image_locally(picam2_obj, filename, difference_img, main_img, lores_img, capture_again, debug):
    if capture_again:
        picam2_obj.capture_file(os.path.join(LOCAL_OUTPUT_FOLDER, LOCAL_OUTPUT_SUBFOLDER, filename + '.jpg'))
    else:
        cv2.imwrite(os.path.join(LOCAL_OUTPUT_FOLDER, LOCAL_OUTPUT_SUBFOLDER, filename + '.jpg'), main_img)

    if debug:
        difference_normalize = cv2.normalize(difference_img, dst=None,
                                             alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        cv2.imwrite(os.path.join(LOCAL_OUTPUT_FOLDER, LOCAL_OUTPUT_SUBFOLDER, "difference", filename + '.png'),
                    difference_normalize)
        cv2.imwrite(os.path.join(LOCAL_OUTPUT_FOLDER, LOCAL_OUTPUT_SUBFOLDER, "lores", filename + '.png'), lores_img)
    camera_logging.output_log(camera_logging.EVENT_IMAGE_WRITTEN_LOCAL, ["Filename: " + filename])


# Method for creating folder directories for local image write if they don't
def create_local_write_folder():
    date_folder_path = os.path.join(LOCAL_OUTPUT_FOLDER, LOCAL_OUTPUT_SUBFOLDER)
    difference_path = os.path.join(LOCAL_OUTPUT_FOLDER, LOCAL_OUTPUT_SUBFOLDER, "difference")
    lores_path = os.path.join(LOCAL_OUTPUT_FOLDER, LOCAL_OUTPUT_SUBFOLDER, "lores")
    if not os.path.exists(date_folder_path):
        os.mkdir(date_folder_path)
    if not os.path.exists(difference_path):
        os.mkdir(difference_path)
    if not os.path.exists(lores_path):
        os.mkdir(lores_path)
