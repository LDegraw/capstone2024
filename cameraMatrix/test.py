import os
import cv2
import numpy as np

img = cv2.imread('images/image17e.jpg')
cv2.imshow('Distorted', img)
cv2.moveWindow('Distorted', 500, 100)
mtx = np.array( [[1.29387823e+03, 0.00000000e+00, 2.99094538e+02],[0.00000000e+00, 1.29307613e+03, 2.56401215e+02],[0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
dist = np.array( [[ 2.16509127e-01, -1.40474548e+00,  5.43486820e-03, -9.72788009e-03, 9.25525206e+00]])
dst = cv2.undistort(img, mtx, dist, None)
cv2.imshow('image', dst)

while True:
    if cv2.waitKey(1)==ord('q'):
        break
cv2.destroyAllWindows()
