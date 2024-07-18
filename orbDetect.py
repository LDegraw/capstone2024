import cv2
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Camera matrix and distortion coefficients
mtx = np.array([[1.29387823e+03, 0.00000000e+00, 2.99094538e+02],
                [0.00000000e+00, 1.29307613e+03, 2.56401215e+02],
                [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
dist = np.array([[2.16509127e-01, -1.40474548e+00, 5.43486820e-03, -9.72788009e-03, 9.25525206e+00]])

# Sensor size and image dimensions
sensor_width_mm = 3.68
sensor_height_mm = 2.76
image_width_px = 3280
image_height_px = 2464

# Focal lengths in pixels
fx_px = mtx[0, 0]
fy_px = mtx[1, 1]

# Pixel size in mm
pixel_size_x_mm = sensor_width_mm / image_width_px
pixel_size_y_mm = sensor_height_mm / image_height_px

# Initialize camera
cam = cv2.VideoCapture(0)

# Initialize position
x, y, z = 0, 0, 0
x_data, y_data, z_data = [], [], []

# Initialize plot
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))

ax1.set_title('X Translation')
ax1.set_xlim(0, 100)
ax1.set_ylim(-10, 10)
line1, = ax1.plot([], [], lw=2)

ax2.set_title('Y Translation')
ax2.set_xlim(0, 100)
ax2.set_ylim(-10, 10)
line2, = ax2.plot([], [], lw=2)

ax3.set_title('Z Translation')
ax3.set_xlim(0, 100)
ax3.set_ylim(-10, 10)
line3, = ax3.plot([], [], lw=2)

def init():
    line1.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    return line1, line2, line3

def update(frame):
    global x, y, z

    # Capture first frame
    ret1, frame1 = cam.read()
    if not ret1:
        return line1, line2, line3
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)

    # Feature detection
    orb = cv2.ORB.create(1000)
    keyPoints1, descriptors1 = orb.detectAndCompute(gray1, None)

    # Capture second frame
    ret2, frame2 = cam.read()
    if not ret2:
        return line1, line2, line3
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    keyPoints2, descriptors2 = orb.detectAndCompute(gray2, None)

    # FLANN parameters and matching
    FLANN_INDEX_LSH = 6
    indexParams = dict(algorithm=FLANN_INDEX_LSH, table_number=6, key_size=12, multi_probe_level=1)
    searchParams = dict(checks=50)
    flann = cv2.FlannBasedMatcher(indexParams, searchParams)

    try:
        matches = flann.knnMatch(descriptors1, descriptors2, k=2)
        goodMatches = []
        for m, n in matches:
            if m.distance < 0.9 * n.distance:
                goodMatches.append(m)
        
        q1 = np.float32([keyPoints1[m.queryIdx].pt for m in goodMatches])
        q2 = np.float32([keyPoints2[m.trainIdx].pt for m in goodMatches])

        # Calculate essential matrix and recover pose
        essentialMat, mask = cv2.findEssentialMat(q1, q2, cameraMatrix=mtx)
        _, R, T, mask = cv2.recoverPose(essentialMat, q1, q2, cameraMatrix=mtx)

        translation_real_world = np.array([T[0] * pixel_size_x_mm / fx_px,
                                           T[1] * pixel_size_y_mm / fy_px,
                                           T[2] * pixel_size_x_mm])

        x += 100000*translation_real_world[0]
        y += 100000*translation_real_world[1]
        z += 100*translation_real_world[2]
        print(f'{x, y, z}')
        x_data.append(x)
        y_data.append(y)
        z_data.append(z)
        
        if len(x_data) > 100:
            x_data.pop(0)
            y_data.pop(0)
            z_data.pop(0)
        
        line1.set_data(range(len(x_data)), x_data)
        line2.set_data(range(len(y_data)), y_data)
        line3.set_data(range(len(z_data)), z_data)
    except Exception as e:
        print(e)

    # Visualization
    matchedImg = cv2.drawMatches(gray1, keyPoints1, gray2, keyPoints2, goodMatches, None)
    blurring = cv2.GaussianBlur(gray1, (5, 5), 0)
    img2 = cv2.drawKeypoints(blurring, keyPoints1, None, color=(128, 128, 0), flags=cv2.DrawMatchesFlags_DRAW_RICH_KEYPOINTS)
    
    cv2.imshow("Keypoints", img2)
    cv2.imshow("Matched", matchedImg)
    cv2.moveWindow("Matched", 200, 0)

    if cv2.waitKey(1) == ord('q'):
        cam.release()
        cv2.destroyAllWindows()
        plt.close('all')
    
    return line1, line2, line3

ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=100)
plt.tight_layout()
plt.show()
