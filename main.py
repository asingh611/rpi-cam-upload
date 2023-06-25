from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import os

# Switch between choosing to upload file from test directory or from camera data
USE_CAMERA_DATA = False

if __name__ == '__main__':
    try:
        # Load environment variables
        load_dotenv(".env")
        account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL")
        default_credential = DefaultAzureCredential()

        # Create the BlobServiceClient object
        blob_service_client = BlobServiceClient(account_url, credential=default_credential)

        # Get the container
        container_name = "cameraimages"
        container_client = blob_service_client.get_container_client(container=container_name)
        print("Ready to write to blob")

        # Write blob to container
        # image_tags = {"Content": "image", "Date": "2023-06-24"}
        if not USE_CAMERA_DATA:
            with open(file=os.path.join('sample_data', 'image.jpg'), mode="rb") as data:
                blob_client = container_client.upload_blob(name="image-blob-2.jpg", data=data)
        print("Blob write completed")

    except Exception as e:
        print(e)

