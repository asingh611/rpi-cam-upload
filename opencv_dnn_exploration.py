# Trying out object detection
# Following along with https://opencv-tutorial.readthedocs.io/en/latest/yolo/yolo.html
# Uses a pre-trained model

import cv2 as cv
import numpy as np
import os
import time

image_path_bird = os.path.join('local_output', 'frame_from_video.PNG')
image_path_no_bird = os.path.join('local_output', 'aeb42440-857e-4504-9ad0-811b17a69f01.jpg')

config_path = os.path.join('opencv_yolo', 'yolov3.cfg')
weight_path = os.path.join('opencv_yolo', 'yolov3.weights')

image_bird = cv.imread(image_path_bird)
image_bird_cropped = image_bird[image_bird.shape[0]-416:image_bird.shape[0], image_bird.shape[1]-416:image_bird.shape[1], :]

net = cv.dnn.readNetFromDarknet(config_path, weight_path)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
ln = net.getLayerNames()
print(len(ln), ln)

# construct a blob from the image
blob = cv.dnn.blobFromImage(image_bird_cropped, 1/255.0, (416, 416), swapRB=True, crop=False)
r = blob[0, 0, :, :]
net.setInput(blob)
t0 = time.time()
outputs = net.forward(ln)
t = time.time()
print(str(t-t0))