import cv2
import numpy as np
import os
import time
from camera_constants import *
import camera_logging

# This is the label position for "bird" in the class name text file
BIRD_CLASS_LABEL_INDEX = 14

config_path = os.path.join(MODEL_FOLDER, MODEL_CONFIGURATION_FILENAME)  # Config file for object detection
weight_path = os.path.join(MODEL_FOLDER, MODEL_WEIGHTS_FILENAME)  # Weights file for object detection
classname_path = os.path.join(MODEL_FOLDER, MODEL_CLASSNAME_FILENAME)  # Class name definitions

# Read in config and weights
net = cv2.dnn.readNetFromDarknet(config_path, weight_path)

# Build list of class labels
class_labels = list()

with open(classname_path) as f:
    lines = f.readlines()
    for line in lines:
        class_labels.append(line.replace('\n', ''))


# Method for detecting whether there is a bird in the input image
def bird_detected(input_image):
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
