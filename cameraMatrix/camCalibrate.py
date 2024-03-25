import cv2
import os
import numpy as np

#https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.htmln as reference

objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

a = 6
b = 8

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((b*a,3), np.float32)
objp[:,:2] = np.mgrid[0:a,0:b].T.reshape(-1,2)

images = os.listdir("images")
x = 0
for photo in images:
    print(photo)
    print(x)
    x +=1
    img = cv2.imread("images/%s" % photo)

    grayScale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow('Gray', grayScale)
    cv2.moveWindow('Gray', 700, 0)

    background = cv2.inRange(grayScale,100, 255)
    
    # setting region of interest
    roi = background[100:600, 300:850]
    cv2.imshow('edited', roi)
    cv2.moveWindow('edited',350, 300)

    ret, corners = cv2.findChessboardCorners(grayScale, (a,b),  None)

    if ret == True:
        print("Appended!")
        objpoints.append(objp)
        imgpoints.append(corners)
        drawn = cv2.drawChessboardCorners(img, (a,b), corners, ret)
    else:
        print("FAILED: Image %s" % photo)
    
    cv2.imshow('img', img)
    cv2.waitKey(500)

cv2.destroyAllWindows()
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, grayScale.shape[::-1], None, None)
dst = cv2.undistort(img, mtx, dist, None)
cv2.imshow('img', img)
cv2.moveWindow('img', 500, 100)
cv2.imshow('undistorted image', dst)
cv2.waitKey(5000)
cv2.destroyAllWindows()
print("Camera Calibrated: ", ret)
print("\nCamera Matrix:\n", mtx)
print("\nDistortion Parameters\n", dist)
print("\nRotation Vectors:\n", rvecs)
print("\nTranslation Vectors:\n", tvecs)
mean_error = 0
for i in range(len(objpoints)):
 imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
 error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
 print(error)
 print(i)
 mean_error += error
 
print( "total error: {}".format(mean_error/len(objpoints)) )