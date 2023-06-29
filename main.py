from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import os
from picamera2 import Picamera2
import time
import uuid
import io

# Switch between choosing to upload file from test directory or from camera data
USE_CAMERA_DATA = True
PHOTO_DELAY = 60

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
                picam2.start()
                time.sleep(1)
                # Capture image to memory
                data = io.BytesIO()
                picam2.capture_file(data, format='jpeg')
                # Write to blob storage
                blob_client = container_client.upload_blob(name=blob_filename, data=data.getvalue())
                # Stop camera                
                picam2.stop()
        if not USE_CAMERA_DATA:
                # For testing when not using the Raspberry Pi
                # Writes image from sampe_data directory to blob storage    
                with open(file=os.path.join('sample_data', 'image.jpg'), mode="rb") as data:
                        blob_client = container_client.upload_blob(name=blob_filename, data=data)
        print("Blob write completed")

    except Exception as e:
        print(e)

