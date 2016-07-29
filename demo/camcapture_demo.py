from __future__ import print_function # with this, print behaves like python 3.x even if using python 2.x
import cv2

camera_device_index = 1 #choose camera device [0,N-1], 0 for first device, 1 for second device etc.
cap = cv2.VideoCapture(camera_device_index)

if cap.isOpened(): # try to get the first frame
    print("Opened camera stream!")
    ret, frame = cap.read()
    if ret == True:
        width = cap.get(3)
        height = cap.get(4)
        print("Frame width x height: {} x {} ".format( width, height ))
        print("Press 'Esc' to close application")
        window_name = "webcam_demo"
else:
    ret = False

while ret:
    cv2.imshow(window_name, frame)
    ret, frame = cap.read()
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break
    
# When everything is done, release the capture device
cap.release()
cv2.destroyWindow(window_name)
 #%%