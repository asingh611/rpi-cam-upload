import cv2
import numpy as np
import os
import time
import io
from camera_constants import *
import camera_logging
from dotenv import load_dotenv
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

# Variables used for local object detection
# This is the label position for "bird" in the class name text file
BIRD_CLASS_LABEL_INDEX = 14

config_path = os.path.join(MODEL_FOLDER, MODEL_CONFIGURATION_FILENAME)  # Config file for object detection
weight_path = os.path.join(MODEL_FOLDER, MODEL_WEIGHTS_FILENAME)  # Weights file for object detection
classname_path = os.path.join(MODEL_FOLDER, MODEL_CLASSNAME_FILENAME)  # Class name definitions

net = None
class_labels = list()  # Build list of class labels

if USE_LOCAL_OBJECT_DETECTION:
    # Read in config and weights
    net = cv2.dnn.readNetFromDarknet(config_path, weight_path)

    with open(classname_path) as f:
        lines = f.readlines()
        for line in lines:
            class_labels.append(line.replace('\n', ''))


# Method for setting up connection to Azure
def initialize_azure_connection():
    # Load environment variables
    load_dotenv(".env")
    vision_key = os.environ.get("AZURE_VISION_KEY")
    vision_endpoint = os.environ.get("AZURE_VISION_ENDPOINT")

    return ComputerVisionClient(vision_endpoint, CognitiveServicesCredentials(vision_key))


# Wrapper method for calling object detection
def bird_detected(input_image, picam2_obj, vision_client):
    if USE_LOCAL_OBJECT_DETECTION:
        return bird_detected_local(input_image)
    elif USE_AZURE_OBJECT_DETECTION:
        return bird_detected_azure(picam2_obj, vision_client)
    else:
        print("No object detection enabled")
        return False


# Method for running object detection on Azure
def bird_detected_azure(picam2_obj, vision_client):
    # Capture image to memory
    data = io.BytesIO()
    picam2_obj.capture_file(data, format='jpeg')
    tags_result_local = vision_client.tag_image_in_stream(data)
    for tag in tags_result_local.tags:
        if tag.name == "bird":
            camera_logging.output_log(camera_logging.EVENT_OBJECT_DETECTED)
            return True
    camera_logging.output_log(camera_logging.EVENT_OBJECT_NOT_DETECTED)
    return False


# Method for detecting whether there is a bird in the input image
# Uses local model that would run on the Raspberry Pi
# When testing this on the Raspberry Pi 1B, it was very slow
def bird_detected_local(input_image):
    cropped_image = input_image[:, 100:700]  # Assumes input image is 800x600 and crops it to 600x600
    img = cv2.resize(cropped_image, (416, 416))  # Resize image to expected dimension

    blob = cv2.dnn.blobFromImage(img, 1.0 / 255., (416, 416), swapRB=True, crop=False)

    # Set blob input
    net.setInput(blob)
    outNames = net.getUnconnectedOutLayersNames()

    # Get output
    start_time = time.time()
    outs = net.forward(outNames)
    end_time = time.time()

    # print('Model run in {} seconds'.format((end_time - start_time)))

    # Notes from OpenCV sample:
    # Network produces output blob with a shape NxC where N is a number of
    # detected objects and C is a number of classes + 4 where the first 4
    # numbers are [center_x, center_y, width, height]
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            # Optimistic approach: only take the first bird result if any
            if confidence > MODEL_CONFIDENCE_THRESHOLD and class_id == BIRD_CLASS_LABEL_INDEX:
                camera_logging.output_log(camera_logging.EVENT_OBJECT_DETECTED)
                return True
    camera_logging.output_log(camera_logging.EVENT_OBJECT_NOT_DETECTED)
    return False



