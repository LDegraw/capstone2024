import os
import cv2
import numpy as np

img = cv2.imread('images/image17e.jpg')
cv2.imshow('Distorted', img)
cv2.moveWindow('Distorted', 500, 100)
mtx = np.array( [[1.29387823e+03, 0.00000000e+00, 2.99094538e+02],[0.00000000e+00, 1.29307613e+03, 2.56401215e+02],[0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
dist = np.array( [[ 2.16509127e-01, -1.40474548e+00,  5.43486820e-03, -9.72788009e-03, 9.25525206e+00]])
dst = cv2.undistort(img, mtx, dist, None)
gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
lines = cv2.HoughLines(gray, 1, np.pi/180, 120, np.array([]))
for line in lines:
    rho, theta = line[0]
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 1000*(-b))
    y1 = int(y0 + 1000*(a))
    x2 = int(x0 - 1000*(-b))
    y2 = int(y0 - 1000)
cv2.line(gray, (x1, y1), (x2, y2), (0, 0, 255), 10)
cv2.imshow("Lines", gray)
cv2.moveWindow("Lines", 1000, 200)
cv2.imshow('image', dst)

while True:
    if cv2.waitKey(1)==ord('q'):
        break
cv2.destroyAllWindows()


cv2.spatialGradient