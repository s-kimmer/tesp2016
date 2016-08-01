# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 08:43:04 2016

@author: ROMANMUELLER

automatically finding matching points, calculate H, process images to compare, plots
"""
import cv2 
import numpy as np

# SETTIGNS
option = 1 #choose 0 for files, 1 for webcam

#image Settings
imgOL_path = "./src/pikachu.jpg"
imgBG_path = "./src/original.png"
camera_device_index = 0 #choose camera device [0,N-1], 0 for first device, 1 for second device etc.

# For captured camera images:
imgSourceDir = "./src/imgs5"
imgFileNameDesc = "img%03d.png"
imgStartIndex = 0
imgEndIndex = 400


# Do IT
imgOL = cv2.imread(imgOL_path, 1)
imgBG = cv2.imread(imgBG_path, 1)

#ORB detector
cv2.ocl.setUseOpenCL(False) #bugfix
orb = cv2.ORB_create()

kpBG = orb.detect(imgBG,None) #find the keypoints with ORB
kpBG, desBG = orb.compute(imgBG, kpBG) # compute the descriptors with ORB
cv2.ocl.setUseOpenCL(True) #endoffix

if option == 1:
    #cam initialzation
    cap = cv2.VideoCapture(camera_device_index)
    
    if cap.isOpened(): # try to get the first frame
        print("Opened camera stream!")
        ret, frame = cap.read()
        if ret == True:
            wframe = cap.get(3)
            hframe = cap.get(4)
            print("Frame width x height: {} x {} ".format( wframe, hframe ))
    else:
        ret = False
        
    if ret: 
        cv2.imshow("webcam", frame)
else:
    frame = 0
    
imgProj = imgBG
#hframe, wframe = frame.shape[:2]
hOL, wOL = imgOL.shape[:2]
UVcenter = np.array([[320], [240], [1]])

imgIndex = imgStartIndex

doLoop = True

RotIndOrig = np.array([[320,320],[0,480],[1,1]])
Rot = 0
# if no rotation, Rot = 0; if anticlockwise rotation(90+-30), Rot = 1, if 
#clockwise rotation(90+-30), Rot = 2; else Rot = 3 

def rotation(H,RotIndOrig):        #Rotation dection
    RotIndProj = np.dot(np.linalg.inv(H), RotIndOrig)
    RotDis = RotIndProj[1,0] - RotIndProj[1,1]
    if np.abs(RotDis) < 240:#240 = 480*sin30
        if RotIndProj[0,0] < RotIndProj[0,1]:
            Rot = 1 #anticlockwise rotation
        else:
            Rot = 2 #clockwise rotation
    elif np.abs(RotDis) > 339:#339 = 480*cos30
        Rot = 0
    else:
        Rot = 3
#    print Rot
    return Rot

mode = 0 #mode
numOfH = 0 #number of 'high' states
counter = 3 #noise toleration 
def switch(Rot,counter,numOfH,mode):
    if Rot == 1:
        counter = 3
        if Rot !=1 :
            counter = counter - 1
                
        if counter >= 0:
            numOfH = numOfH + 1
       
    print "Rot = %d" % Rot
    print "numOfH = %d"%numOfH        
    
    if numOfH >= 15:        
        if mode >= 3:# 3 modes
            mode = 0
        else:
            mode = mode + 1
        numOfH = 0
        counter = 3            

    print "mode = %d\n" % mode
    return (mode,counter,numOfH)        


# Create Window for fullscreen display
cv2.namedWindow("projector", cv2.WND_PROP_FULLSCREEN)          
cv2.setWindowProperty("projector", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.moveWindow("projector", 1920, 0)


while doLoop:
    cv2.imshow("projector", imgProj)    
    
    
    if option == 1:
        # wEB CAM
        ret, frame = cap.read()
        if ret == False:
            print("Img capture failed")
            break
    else:
        if imgIndex > imgEndIndex:
            break
        # File Source
        imgFileName = imgFileNameDesc % (imgIndex)
        imgFilePath = imgSourceDir + "/" + imgFileName
        print("Loading: " + imgFilePath)
        frame = cv2.imread(imgFilePath, 1)
        imgIndex = imgIndex + 1
    
    
    #ORB detector
    cv2.ocl.setUseOpenCL(False) #bugfix
    kpframe = orb.detect(frame,None) #find the keypoints with ORB
    kpframe, desframe = orb.compute(frame, kpframe) # compute the descriptors with ORB
    cv2.ocl.setUseOpenCL(True) #endoffix
    
    #find matching points
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True) #create BFMatcher object
    matches = bf.match(desBG,desframe) # Match descriptors
    
    MIN_MATCH_COUNT = 4       
    if len(matches)>MIN_MATCH_COUNT:
        src_pts = np.float32([ kpBG[m.queryIdx].pt for m in matches ])
        dst_pts = np.float32([ kpframe[m.trainIdx].pt for m in matches ])
    else:
        print("Error: less than four matching points")
        break


    #homography    
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
    
    UV = np.dot(np.linalg.inv(H), UVcenter) #H or H^-1 ???
    UVconv = np.array([[0], [0]])
    UVconv[0] = max(1 + 0.5 * wOL, UV[0])
    UVconv[1] = max(1 + 0.5 * hOL, UV[1])
    UVconv[0] = min(UV[0], 640 - 0.5 * wOL -1)
    UVconv[1] = min(UV[1], 480 - 0.5 * hOL -1)
    
 
    #imgProj = np.zeros(h1, w1, np.uint8)
    imgProj = imgBG.copy()
#    imgProj[(np.int(UVconv[1] - 0.5 * hOL)):np.int((UVconv[1] + 0.5 * hOL)), np.int((UVconv[0] - 0.5 * wOL)):np.int((UVconv[0] + 0.5 * wOL))] = imgOL
    
    # Rotation detection
    Rot = rotation(H,RotIndOrig)
    mode,counter,numOfH = switch(Rot,counter,numOfH,mode)
    # Show orig frame

    cv2.imshow("camera", frame)

    key = cv2.waitKey(2)
    if key == 27:
        cv2.destroyAllWindows()
        cap.release
        doLoop = False
        break

#    while key != 13 & option != 0:
#        key = cv2.waitKey(2)
#        if key == 27:
#            cv2.destroyAllWindows()
#            doLoop = False
#            break


