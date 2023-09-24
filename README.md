# Raspberry Pi Bird Camera
Code running on my Raspberry Pi for detecting and capturing images of birds visiting our window bird feeder

## Hardware Used

- Raspberry Pi 1 Model B
- Raspberry Pi Camera Board v2

## Overview
On startup, the camera captures N frames and calculates a median image

For every loop after startup, the camera captures a new frame and:

- Take the difference between the current frame and the median image
- Observe the number of pixels where the difference between the two images is larger than threshold DIFFERENCE_THRESHOLD
- If the percentage of pixels with a difference of DIFFERENCE_THRESHOLD is greater than MOTION_THRESHOLD, then output that motion occurred
- If it's been long enough since the last motion detection (based on TIME_BETWEEN_MOTION), then write image
- Replace the oldest frame in the array of images for calculating the median image with the latest image so that a new median image can be calculated

## Some additional features

- The camera automatically stops at a certain time (END_HOUR) and restarts the next day at START_HOUR so that the code isn't running overnight when there is no visibility
- Images can be written locally or to Azure Blob Storage (WRITE_IMAGE_LOCALLY, WRITE_TO_AZURE)
- Events are logged in the console or in a local log file (LOG_CONSOLE, LOG_FILE)
- Can specify a specific region of the image to focus on for motion detection (FOCUS_REGION_ROW_START, FOCUS_REGION_ROW_END, FOCUS_REGION_COL_START, FOCUS_REGION_COL_END)

## Getting started
### .env
This file contains some information needed to connect to Azure, including a client ID/secret. 
There is a sample.env file that can be populated and renamed to .env

### camera_constants.py
This file contains the constants/thresholds/configurations to be used. Within this file, you can configure properties like:

- Image resolution 
- Where to output the images to
- Threshold values for motion detection
- Where to output logs

There is a camera_constants_example.py file that can be populated and renamed

## Some planned improvements

- After first pass to detect motion, use object detection model to detect whether there is a bird (in order to reduce false positives)
- Log to Azure
- Capture video
- Take in args to override certain config values from their defaults
- Determine START_HOUR and END_HOUR based on CSV that contains sunrise/sunset hours for the year
