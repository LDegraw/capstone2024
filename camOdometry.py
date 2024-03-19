import os
import cv2
import matplotlib
import random
import numpy as np
import time

# Feedback for odemetry errors

# TODO: Camera Calibration for raspberry pi
# checkerboard test

cam = cv2.VideoCapture(0)

# setting to known resolution
cam.set(3, 1280)
cam.set(4, 720)

while True:
    start_time = time.time()
    _, frame1 = cam.read()
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    fast = cv2.FastFeatureDetector_create(threshold=45)
    fast.setNonmaxSuppression(0)
    keyPoints1 = fast.detect(gray1, None)
    
    # 3 more goals end of semester

    # creating two frames to read from
    #_, frame2 = cam.read()
    #gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    #keyPoints2 = fast.detect(gray2, None)

    #cv2.calcOpticalFlowPyrLK(gray1, gray2, keyPoints1, keyPoints2)
    # Need only 5 good points to calculate any distance from frame to frame to input into essential matrix
    #cv2.findEssentialMat()
    # y_1^T * E * y = 0 for y being normalized image coordinates
    
    # recover rotation matrix
    #recoverPose(E, kepoints1, keypoints2, R, t, focal, pp, mask)

    #using guassian blurring to make image more fuzzy/ better for detector
    blurring = cv2.GaussianBlur(gray1, (5,5), 0)
    print(len(keyPoints1))

    img2 = cv2.drawKeypoints(blurring, keyPoints1, None, color=(128,128,0), flags=0)

    cv2.imshow("Fast Algorithm", img2)
    end_time = time.time()
    print((end_time-start_time))
    if cv2.waitKey(1)==ord('q'):
        break
cam.release()