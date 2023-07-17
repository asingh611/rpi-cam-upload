import cv2 as cv
import numpy as np
import os

image_path_bird = os.path.join('local_output', 'e52135f1-09f0-498e-8aa5-3dd2aeb1e43c.jpg')
image_path_no_bird = os.path.join('local_output', 'aeb42440-857e-4504-9ad0-811b17a69f01.jpg')
image_path_no_bird_2 = os.path.join('local_output', 'd8c8ff32-cad7-403e-ae58-9e2f714b8ccb.jpg')

image_bird = cv.imread(image_path_bird, cv.IMREAD_GRAYSCALE)[50:110, 15:150]
image_no_bird = cv.imread(image_path_no_bird, cv.IMREAD_GRAYSCALE)[50:110, 15:150]
image_no_bird_2 = cv.imread(image_path_no_bird_2, cv.IMREAD_GRAYSCALE)[50:110, 15:150]

# difference_path_bird = os.path.join('local_output', '845e3689-2a94-45eb-8a3f-6f923bdceb4a.png')
difference_path_bird = os.path.join('local_output', 'e52135f1-09f0-498e-8aa5-3dd2aeb1e43c.png')

difference_path_no_bird = os.path.join('local_output', '6c812ee2-b0a0-4e89-86ff-df330d56014d.png')
difference_bird = cv.imread(difference_path_bird, cv.IMREAD_GRAYSCALE)[50:110, 15:150]
difference_no_bird = cv.imread(difference_path_no_bird, cv.IMREAD_GRAYSCALE)[50:110, 15:150]


# difference = abs(image_bird - image_no_bird)
# difference2 = abs(image_no_bird_2 - image_no_bird)
# difference_threshold = 100
# difference[difference <= difference_threshold] = 1
# difference[difference > difference_threshold] = 0  # motion
# difference_normalize = cv.normalize(difference, dst=None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX)
# print(np.count_nonzero(difference == 0)/np.size(difference))
#
#
# difference2[difference2 <= difference_threshold] = 1
# difference2[difference2 > difference_threshold] = 0  # motion
# difference_normalize_2 = cv.normalize(difference2, dst=None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX)
# print(np.count_nonzero(difference2 == 0)/np.size(difference2))
#
# # cv.rectangle(sample_image, (15, 110), (150, 50), (0,255,0), 1)
# # cv.imshow("Image", sample_image)
#
# cv.imshow("Bird", difference_normalize)
# cv.imshow("No Bird", difference_normalize_2)

print(np.count_nonzero(difference_bird == 0)/np.size(difference_bird))
print(np.count_nonzero(difference_no_bird == 0)/np.size(difference_no_bird))

cv.imshow("Bird", difference_bird)
cv.imshow("No Bird", difference_no_bird)

kernel = np.ones((3, 3), np.uint8)
# img_erosion = cv.erode(difference_bird, kernel, iterations=1)
# print(np.count_nonzero(img_erosion == 0)/np.size(img_erosion))
img_dilation = cv.dilate(difference_bird, kernel, iterations=1)
img_dilation_no_bird = cv.dilate(difference_no_bird, kernel, iterations=1)
print(np.count_nonzero(img_dilation == 0)/np.size(img_dilation))
print(np.count_nonzero(img_dilation_no_bird == 0)/np.size(img_dilation_no_bird))
# cv.imshow('Erosion', img_erosion)
cv.imshow('Dilation', img_dilation)
cv.imshow('Dilation No Bird', img_dilation_no_bird)

# Wait for the user to press a key
cv.waitKey(0)

# Close all windows
cv.destroyAllWindows()