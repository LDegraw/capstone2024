#Test for 3d mapping

import cv2
import time



cam = cv2.VideoCapture(0)

detector = cv2.QRCodeDetector()

while True:
    _, frame1 = cam.read()
    gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    sized = cv2.resize(gray, (800, 600))

    ret_qr, decoded_info, points, _ = detector.detectAndDecodeMulti(gray)
    if ret_qr:
        if(decoded_info== ('left',)):
            print("do Shit")
    cv2.imshow("resized", frame1)
    if cv2.waitKey(1)==ord('q'):
        break
cv2.destroyAllWindows()

cam.release()