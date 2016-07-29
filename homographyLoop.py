# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 08:43:04 2016

@author: ROMANMUELLER

automatically finding matching points, calculate H, process images to compare, plots
"""
import cv2 
import numpy as np

# SETTIGNS
option = 0 #choose 0 for files, 1 for webcam

#image Settings
imgOL_path = "./src/pikachu.jpg"
imgBG_path = "./src/original.png"
camera_device_index = 0 #choose camera device [0,N-1], 0 for first device, 1 for second device etc.

# For captured camera images:
imgSourceDir = "./imgs2"
imgFileNameDesc = "img%03d.png"
imgStartIndex = 0
imgEndIndex = 200


# Do IT
imgOL= cv2.imread(imgOL_path, 1)
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

while True:
    cv2.imshow("projector", imgProj)    
    
    if option == 1:
        # wEB CAM
        frame = cap.read()
    else:
        if imgIndex > imgEndIndex:
            break
        # File Source
        imgFileName = imgFileNameDesc % (imgIndex)
        imgFilePath = imgSourceDir + "/" + imgFileName
        print("Loading" + imgFilePath)
        frame = cv2.imread(imgFilePath)
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
    
    UV = np.dot(H, UVcenter) #H or H^-1 ???
    UVconv = np.array([[0], [0]])
    UVconv[0] = max(0 + 0.5 * wOL, UV[0])
    UVconv[1] = max(0 + 0.5 * hOL, UV[1])
    UVconv[0] = min(UV[0], 640 - 0.5 * wOL)
    UVconv[1] = min(UV[1], 480 - 0.5 * hOL)
    
    
    #imgProj = np.zeros(h1, w1, np.uint8)
    imgProj = imgBG
    imgProj[(np.int(UVconv[1] - 0.5 * hOL)):np.int((UVconv[1] + 0.5 * hOL)), np.int((UVconv[0] - 0.5 * wOL)):np.int((UVconv[0] + 0.5 * wOL))] = imgOL
# This does not work:
# new comment    
    #imgProj = cv2.cvtColor(imgProj, cv2.COLOR_GRAY2BGR)
#    
    key = cv2.waitKey(2)
    if key == 27:
        cv2.destroyAllWindows()
        break

