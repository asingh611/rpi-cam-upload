# Following along with
# https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/quickstarts-sdk/image-analysis-client-library
from dotenv import load_dotenv
import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

# Load environment variables
load_dotenv("../.env")
vision_key = os.environ.get("AZURE_VISION_KEY")
vision_endpoint = os.environ.get("AZURE_VISION_ENDPOINT")

vision_client = ComputerVisionClient(vision_endpoint, CognitiveServicesCredentials(vision_key))

image_base_path = os.path.join('../local_output', 'bird')
image_path = os.path.join(image_base_path, "0fd96662-859a-4833-a239-ec005c4277ea.jpg")

local_image = open(image_path, "rb")
# Call API local image
tags_result_local = vision_client.tag_image_in_stream(local_image)

# Print results with confidence score
print("Tags in the local image: ")
if len(tags_result_local.tags) == 0:
    print("No tags detected.")
else:
    for tag in tags_result_local.tags:
        print("'{}' with confidence {:.2f}%".format(tag.name, tag.confidence * 100))
print()
