import os
import cv2
import matplotlib
import random
import numpy as np
import time
from vpython import *


x = 0
y = 0
z = 0

robot = sphere(radius=0.5, color=color.red)
roboPath = curve(pos=[vec(0, 0, 0)], color=color.blue)

lk_params = dict(winSize  = (21, 21), 
				#maxLevel = 3,
             	criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
# Feedback for odemetry errors


# TODO: Camera Calibration for raspberry pi
# checkerboard test

cam = cv2.VideoCapture(0)

# setting to known resol    `ution
cam.set(3, 1280)
cam.set(4, 720)
focalLength = 3.02

while True:
    start_time = time.time()
    _, frame1 = cam.read()
    x = x+0.1
    roboPath.append(pos=vector(x,y,z), color=color.blue)
    robot.pos=vector(x, y, z)

    # undistort images
    mtx = np.array([[1.30402710e+03, 0.00000000e+00, 2.73394644e+02],[0.00000000e+00, 1.29870489e+03, 2.50434247e+02],[0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    dist = np.array([[ 2.91858045e-01, -2.19979963e+00,  3.85731309e-03, -2.51220306e-02, 1.83543619e+01]])
    dst = cv2.undistort(frame1, mtx, dist, None)

    gray1 = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    fast = cv2.FastFeatureDetector_create(threshold=45)
    fast.setNonmaxSuppression(0)
    keyPoints1 = fast.detect(gray1, None)
    
    # 3 more goals end of semester

    # creating two frames to read from
    _, frame2 = cam.read()
    dst2 = cv2.undistort(frame2, mtx, dist, None)
    gray2 = cv2.cvtColor(dst2, cv2.COLOR_BGR2GRAY)
    keyPoints2 = fast.detect(gray2, None)
    keys1 = np.expand_dims(cv2.KeyPoint_convert(keyPoints1), axis=1)
    #keys2 = np.expand_dims(cv2.KeyPoint_convert(keyPoints2), axis=1)
    
    
    FLANN_INDEX_LSH = 6
    indexParams = dict(algorithm = FLANN_INDEX_LSH, table_number=6, key_size=12, multi_probe_level=1)
    searchParams = dict(checks=50)
    flann = cv2.FlannBasedMatcher(indexParams=indexParams, searchParams=searchParams)
    #matchedImg = cv2.drawMatches(gray1, keyPoints1, gray2, keyPoints2, matches, None)    

    matches = flann.knnMatch(keyPoints1, keyPoints2)

    kp2, st, err = cv2.calcOpticalFlowPyrLK(gray1, gray2, keys1, None, **lk_params)
    st = st.reshape(st.shape[0])
    good = []

    for m,n in matches:
        if m.distance < 0.7 * n.distance:
            good.append[m]

    # Need only 5 good points to calculate any distance from frame to frame to input into essential matrix
    #E, mask = cv2.findEssentialMat(keys1, keys2, focal=focalLength, method=cv2.RANSAC, prob=0.999, threshold=1.0)
    # y_1^T * E * y = 0 for y being normalized image coordinates
    
    # recover rotation matrix
    #_, R, T = cv2.recoverPose(E, keyPoints2, keyPoints1, focalLength, pp=(x,y))

    #print(R)
    #print(T)
    #using guassian blurring to make image more fuzzy/ better for detector
    blurring = cv2.GaussianBlur(gray1, (5,5), 0)

    img2 = cv2.drawKeypoints(blurring, keyPoints1, None, color=(128,128,0), flags=0)
    
    cv2.moveWindow('Matched', 500, 0)
    cv2.imshow("Fast Algorithm", img2)
    end_time = time.time()
    print((end_time-start_time))
    if cv2.waitKey(1)==ord('q'):
        break
cam.release()

1