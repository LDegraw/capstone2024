import os
import cv2
import matplotlib
import random
import numpy as np
import time
from vpython import *
#import matplotlib.pyplot as plt

x = 0
y = 0
z = 0

mtx = np.array( [[1.29387823e+03, 0.00000000e+00, 2.99094538e+02],[0.00000000e+00, 1.29307613e+03, 2.56401215e+02],[0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
dist = np.array( [[ 2.16509127e-01, -1.40474548e+00,  5.43486820e-03, -9.72788009e-03, 9.25525206e+00]])

sensor_width_mm = 3.68  # Example sensor width
sensor_height_mm = 2.76

image_width_px = 3280 
image_height_px = 2464

fx_px = mtx[0, 0]  # Focal length along x-axis in pixels
fy_px = mtx[1, 1]

pixel_size_x_mm = sensor_width_mm / image_width_px
pixel_size_y_mm = sensor_height_mm / image_height_px

robot = sphere(radius=0.0001, color=color.red)
roboPath = curve(pos=[vec(0, 0, 0)], color=color.blue)

lk_params = dict(winSize  = (21, 21), 
				#maxLevel = 3,
             	criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
# Feedback for odemetry errors

# TODO: Camera Calibration for raspberry pi
# checkerboard test

cam = cv2.VideoCapture(0)

#ax = plt.figure().add_subplot(projection='3d')

while True:
    #ax.scatter(sequence_containing_x_vals, sequence_containing_y_vals, sequence_containing_z_vals)
    #plt.show() 
    start_time = time.time()
    _, frame1 = cam.read()
    roboPath.append(pos=vector(x,y,z), color=color.blue)
    robot.pos=vector(x, y, z)
    # undistort images
    dst = cv2.undistort(frame1, mtx, dist, None)
    gray1 = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    fast = cv2.FastFeatureDetector_create(threshold=45)
    #creating 1000 
    orb = cv2.ORB.create(1000)
    keyPoints1, descriptors1 = orb.detectAndCompute(gray1, None)

    # creating two frames to read from
    _, frame2 = cam.read()
    dst2 = cv2.undistort(frame2, mtx, dist, None)
    gray2 = cv2.cvtColor(dst2, cv2.COLOR_BGR2GRAY)
    keyPoints2, descriptors2 = orb.detectAndCompute(gray2, None)
    keys1 = np.expand_dims(cv2.KeyPoint_convert(keyPoints1), axis=1)
    keys2 = np.expand_dims(cv2.KeyPoint_convert(keyPoints2), axis=1)
    
    FLANN_INDEX_LSH = 6
    indexParams = dict(algorithm = FLANN_INDEX_LSH, table_number=6, key_size=12, multi_probe_level=1)
    searchParams = dict(checks=50)
    flann = cv2.FlannBasedMatcher(indexParams=indexParams, searchParams=searchParams)  

    matches = flann.knnMatch(descriptors1, descriptors2, k=2)

    #kp2, st, err = cv2.calcOpticalFlowPyrLK(gray1, gray2, keys1, None, **lk_params)
    #st = st.reshape(st.shape[0])

    goodMatches = []
    for i, pair in enumerate(matches):
        try:
            m, n = pair
            if m.distance < 0.99*n.distance:
                goodMatches.append(m)
        except ValueError:
            pass

    q1 = np.float32([keyPoints1[m.queryIdx].pt for m in goodMatches])
    q2 = np.float32([keyPoints2[m.trainIdx].pt for m in goodMatches])

    matchedImg = cv2.drawMatches(gray1, keyPoints1, gray2, keyPoints2, goodMatches, None)  

    #focal=focalLength, method=cv2.RANSAC, prob=0.999, threshold=1.0
    # Need only 5 good points to calculate any distance from frame to frame to input into essential matrix
    try:
        essentialMat, mask = cv2.findEssentialMat(q1, q2, cameraMatrix=mtx)
        retval, R, T, mask = cv2.recoverPose(essentialMat, q1, q2, cameraMatrix=mtx)
        translation_real_world = np.array([T[0] * pixel_size_x_mm / fx_px,T[1] * pixel_size_y_mm / fy_px,T[2] * pixel_size_x_mm])
        
        x = x + 0.1*translation_real_world[0]
        y = y + 0.1*translation_real_world[1]
        z = z + 0.1*translation_real_world[2]
    
        print("X: %s\n" % x)
        print("Y: %s\n" % y)
        print("Z: %s\n" % z)
    except:
        pass
    # y_1^T * E * y = 0 for y being normalized image coordinates
    
    # recover rotation matrix
    

    #print(R)
    #print(T)
    #using guassian blurring to make image more fuzzy/ better for detector
    blurring = cv2.GaussianBlur(gray1, (5,5), 0)

    img2 = cv2.drawKeypoints(blurring, keyPoints1, None, color=(128,128,0), flags=0)
    cv2.imshow('Matched', matchedImg)
    cv2.moveWindow('Matched', 200, 0)
    cv2.imshow("Fast Algorithm", img2)
    end_time = time.time()
    print((end_time-start_time))
    if cv2.waitKey(1)==ord('q'):
        break
cam.release()


