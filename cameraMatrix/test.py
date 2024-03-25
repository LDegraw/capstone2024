import os
import cv2
import numpy as np

img = cv2.imread('images/image17e.jpg')
cv2.imshow('Distorted', img)
cv2.moveWindow('Distorted', 500, 100)
mtx = np.array([[1.29771795e+03, 0.00000000e+00, 2.87319287e+02],[0.00000000e+00, 1.29601178e+03, 2.51839486e+02],[0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
dist = np.array( [[ 2.12181564e-01, -9.17660066e-01,  5.23648768e-03, -1.47978626e-02, 5.43448417e+00]])
dst = cv2.undistort(img, mtx, dist, None)
cv2.imshow('image', dst)

while True:
    if cv2.waitKey(1)==ord('q'):
        break
cv2.destroyAllWindows()
