import cv2
import numpy as np
import os

# Started with this tutorial: https://docs.opencv.org/4.x/da/d53/tutorial_py_houghcircles.html
# Was hoping to detect the suction cups to help figure out the positioning and scale of the bird feeder
# Notes: This method detected too many circles in the wrong places; it would probably require a lot of tuning

image_path_bird = os.path.join('../local_output', 'bird', '0aaf52e6-c958-4729-80ad-34a6f4f0685e.jpg')

image_bird = cv2.imread(image_path_bird, cv2.IMREAD_GRAYSCALE)
img = cv2.medianBlur(image_bird, 5)

circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 80,
                           param1=50, param2=80, minRadius=50, maxRadius=150)
circles = np.uint16(np.around(circles))

for i in circles[0, :]:
    # draw the outer circle
    cv2.circle(image_bird, (i[0], i[1]), i[2], (0, 255, 0), 2)
    # draw the center of the circle
    cv2.circle(image_bird, (i[0], i[1]), 2, (0, 0, 255), 3)
cv2.imshow('detected circles', image_bird)
cv2.waitKey(0)
cv2.destroyAllWindows()