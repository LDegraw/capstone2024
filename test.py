#Test for 3d mapping

import cv2
import time
import matplotlib.pyplot as plt


cam = cv2.VideoCapture(0)

ax = plt.figure()


while True:
    _, frame1 = cam.read()
    gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    sized = cv2.resize(gray, (800, 600))

    stereo = cv2.StereoBM_create(numDisparities=16, blockSize=21)

    depth = stereo(frame1, frame2)

    orb = cv2.ORB.create(1000)
    keyPoints1, descriptors1 = orb.detectAndCompute(sized, None)
    img2 = cv2.drawKeypoints(sized, keyPoints1, None, color=(128,128,0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow("resized", img2)
    if cv2.waitKey(1)==ord('q'):
        break
cv2.destroyAllWindows()

cam.release()