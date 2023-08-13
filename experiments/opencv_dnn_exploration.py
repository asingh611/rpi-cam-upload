# Trying out object detection
# Following along with:
# https://opencv-tutorial.readthedocs.io/en/latest/yolo/yolo.html
# https://github.com/odundar/computer-vision/blob/master/OpenCV%20Object%20Detection%20DNN.ipynb
# https://github.com/opencv/opencv/blob/4.x/samples/dnn/object_detection.py
# Uses a pre-trained model

import cv2 as cv
import numpy as np
import os
import time

# image_path_bird = os.path.join('../local_output', 'bird', '7a084b8a-7a1a-4cf9-86aa-828c8e179306.jpg')
# image_path_no_bird = os.path.join('../local_output', 'aeb42440-857e-4504-9ad0-811b17a69f01.jpg')

# This is the label position for "bird" in the class name text file
BIRD_CLASS_LABEL_INDEX = 14

image_base_path_bird = os.path.join('../local_output', 'bird')
image_base_path_no_bird = os.path.join('../local_output', 'no_bird')

config_path = os.path.join('../opencv_yolo', 'yolov3.cfg')
weight_path = os.path.join('../opencv_yolo', 'yolov3.weights')
classname_path = os.path.join('../opencv_yolo', 'coco.names')

# Read in config and weights
net = cv.dnn.readNetFromDarknet(config_path, weight_path)

# Build list of class labels
class_labels = list()

with open(classname_path) as f:
    lines = f.readlines()
    for line in lines:
        class_labels.append(line.replace('\n', ''))


def run_object_detection(image_base_path, should_detect):
    success = 0
    failure = 0
    # Read in all images in test path
    for filename in os.listdir(image_base_path):
        image_path = os.path.join(image_base_path, filename)
        image_to_evaluate = cv.imread(image_path)[:, 50:650]  # Assumes input image is 800x600 and crops it to 600x600
        img = cv.resize(image_to_evaluate, (416, 416))  # Resize image to expected dimension

        confThreshold = 0.7

        # Keep track of original image size
        frameHeight = img.shape[0]
        frameWidth = img.shape[1]

        blob = cv.dnn.blobFromImage(img, 1.0 / 255., (416, 416), swapRB=True, crop=False)

        # Set blob input
        net.setInput(blob)
        outNames = net.getUnconnectedOutLayersNames()

        # Get output
        start_time = time.time()
        outs = net.forward(outNames)
        end_time = time.time()

        print('Model run in {} seconds'.format((end_time - start_time)))
        layerNames = net.getLayerNames()
        lastLayerId = net.getLayerId(layerNames[-1])
        lastLayer = net.getLayer(lastLayerId)
        # print(lastLayer.type)

        classIds = []
        confidences = []
        boxes = []

        # Notes from OpenCV sample:
        # Network produces output blob with a shape NxC where N is a number of
        # detected objects and C is a number of classes + 4 where the first 4
        # numbers are [center_x, center_y, width, height]
        max_confidence = 0.0
        for out in outs:
            for detection in out:
                scores = detection[5:]
                classId = np.argmax(scores)
                confidence = scores[classId]
                # Only append results if they are more confident and are for birds
                if confidence > confThreshold and confidence > max_confidence:  # and classId == BIRD_CLASS_LABEL_INDEX:
                    max_confidence = confidence
                    center_x = int(detection[0] * frameWidth)
                    center_y = int(detection[1] * frameHeight)
                    width = int(detection[2] * frameWidth)
                    height = int(detection[3] * frameHeight)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    classIds.append(classId)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])

            #     # Optimistic approach: only take the first bird result if any
            #     # Only append results if they are more confident and are for birds
            #     if confidence > confThreshold and classId == BIRD_CLASS_LABEL_INDEX:
            #         max_confidence = confidence
            #         center_x = int(detection[0] * frameWidth)
            #         center_y = int(detection[1] * frameHeight)
            #         width = int(detection[2] * frameWidth)
            #         height = int(detection[3] * frameHeight)
            #         left = int(center_x - width / 2)
            #         top = int(center_y - height / 2)
            #         classIds.append(classId)
            #         confidences.append(float(confidence))
            #         boxes.append([left, top, width, height])
            #         break
            # if max_confidence != 0.0:
            #     break

        if max_confidence == 0.0:
            print("No objects found")
            if should_detect:
                failure += 1
            else:
                success += 1
            # print(filename)
            # cv.imshow('Current image', img)
            # cv.waitKey(0)
            # cv.destroyWindow("Current image")
        else:
            # left, top, width, height = boxes[-1]
            # cv.rectangle(img, (left, top), (left + width, top + height), (0, 255, 0))

            label = '%s: %s' % (class_labels[classIds[-1]], format(confidences[-1], '.3f'))
            print(label)
            if classIds[-1] == BIRD_CLASS_LABEL_INDEX and should_detect:
                success += 1
            else:
                failure += 1
            # labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            # top = max(top, labelSize[1])
            # cv.rectangle(img, (left, top - labelSize[1]), (left + labelSize[0], top + baseLine), (255, 255, 255),
            #              cv.FILLED)
            # cv.putText(img, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

            # cv.imshow('Current image', img)
            # cv.waitKey(0)
            # cv.destroyWindow("Current image")
        print("Number Correct: {}".format(success))
        print("Number Incorrect: {}".format(failure))


if __name__ == '__main__':
    run_object_detection(image_base_path_bird, True)
    # run_object_detection(image_base_path_no_bird, False)

    # Results:
    # ~80% True Positive | ~20% False Negative
    # 100% True Negative | 0% False Positive
