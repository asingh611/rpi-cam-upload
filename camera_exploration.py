# References
# https://opencv-tutorial.readthedocs.io/_/downloads/en/latest/pdf/
# https://docs.opencv.org/3.4/d1/dc5/tutorial_background_subtraction.html
# CS6476 8D-L1 Introduction To Video Analysis
# Sample video: https://www.shutterstock.com/video/clip-1104853005-4k-video-clip-robin-eating-seeds-feeding
import cv2 as cv
import numpy as np

USE_CAMERA = False
n = 20  # Number of frames to take median of
previous_frames = None  # Holds numpy array of previous frames
difference = None
frames_captured = 0  # Keeps track of the total number of frames
difference_threshold = 15  # Threshold value for abs difference of current frame and median image
motion_threshold = 0.05  # Percent of pixels to determine that motion occurred

if USE_CAMERA:
    cap = cv.VideoCapture(0)
else:
    cap = cv.VideoCapture('sample_input_videos/1104853005-preview.mp4')
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Can't receive frame")
        break

    # Convert to grayscale
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frames_captured += 1
    # If we are just starting, populate previous_frames with n frames
    if previous_frames is None:
        previous_frames = np.zeros((gray.shape[0], gray.shape[1], n))
        previous_frames[:, :, 0] = gray
        for i in range(1, n):
            ret, frame = cap.read()
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            previous_frames[:, :, i] = gray
            frames_captured += 1

    # Take the median
    median_image = np.median(previous_frames, axis=2)

    # Take the absolute difference between the median and current frame
    difference = np.abs(median_image-gray)

    difference[difference <= difference_threshold] = 1
    difference[difference > difference_threshold] = 0  # motion

    # Update the oldest frame in previous_frames with the latest image
    index_to_update = frames_captured % n
    previous_frames[:, :, index_to_update] = gray

    # Take action if certain percentage of pixels are 0
    if np.count_nonzero(difference == 0) > motion_threshold * np.size(difference):
        print("Motion Detected")

    # Calculate MSE (could be another metric to use)
    # mse = np.mean(abs(previous_frames[:, :, (frames_captured-1) % n]-gray))
    mse = np.mean(abs(median_image - gray))
    print(mse)

    # Display the resulting frame
    cv.imshow('frame', frame)
    cv.imshow('median', median_image.astype(np.uint8))
    cv.imshow('threshold', difference)

    # I wasn't able to get these to return a result for the sample video even with tuning the parameters
    # backSub = cv.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)
    # backSub = cv.createBackgroundSubtractorKNN(history=10, dist2Threshold=1000, detectShadows=False)
    # fgMask = backSub.apply(gray, learningRate=0.1)

    # cv.rectangle(frame, (10, 2), (100, 20), (255, 255, 255), -1)
    # cv.putText(frame, str(cap.get(cv.CAP_PROP_POS_FRAMES)), (15, 15),
    #            cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
    #
    # cv.imshow('Frame', gray)
    # cv.imshow('FG Mask', fgMask)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
